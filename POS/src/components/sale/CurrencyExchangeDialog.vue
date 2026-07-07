<template>
	<Dialog
		:modelValue="modelValue"
		@update:modelValue="$emit('update:modelValue', $event)"
		:options="{ title: __('تصريف العملات'), size: 'lg' }"
	>
		<template #body-content>
			<div class="flex flex-col gap-5 py-2">
				<!-- Exchange Rates Section -->
				<div v-if="exchangeRates.length > 0" class="bg-gray-50 border border-gray-200 rounded-lg overflow-hidden">
					<div class="px-4 py-3 bg-gray-100 border-b border-gray-200 flex items-center justify-between">
						<div>
							<h3 class="text-sm font-semibold text-gray-800">{{ __('أسعار الصرف') }}</h3>
							<p class="text-xs text-gray-500 mt-0.5">
								{{ __('العملة الأساسية: {0}', [companyCurrency || '-']) }}
							</p>
						</div>
						<button
							@click="isEditingRates = !isEditingRates"
							class="text-xs px-2 py-1 rounded border transition-all"
							:class="isEditingRates
								? 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100'
								: 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'"
							:disabled="isSavingRates"
						>
							{{ isEditingRates ? __('إلغاء') : __('تعديل الأسعار') }}
						</button>
					</div>
					<div class="overflow-x-auto">
						<table class="min-w-full divide-y divide-gray-200">
							<thead class="bg-gray-50">
								<tr>
									<th class="px-4 py-2 text-start text-xs font-medium text-gray-500 uppercase">{{ __('العملة') }}</th>
									<th class="px-4 py-2 text-end text-xs font-medium text-gray-500 uppercase">{{ __('سعر الشراء') }}</th>
									<th class="px-4 py-2 text-end text-xs font-medium text-gray-500 uppercase">{{ __('سعر البيع') }}</th>
								</tr>
							</thead>
							<tbody class="bg-white divide-y divide-gray-200">
								<tr v-for="rate in editableRates" :key="rate.currency">
									<td class="px-4 py-2 text-sm font-medium text-gray-900">{{ rate.currency }}</td>
									<td class="px-4 py-2 text-sm text-end">
										<input
											v-if="isEditingRates"
											v-model.number="rate.buy_rate"
											type="number"
											min="0"
											step="0.0001"
											class="w-24 text-end text-sm border border-gray-300 rounded px-2 py-1 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-green-700"
										/>
										<span v-else class="text-green-700">{{ formatRate(rate.buy_rate) }}</span>
									</td>
									<td class="px-4 py-2 text-sm text-end">
										<input
											v-if="isEditingRates"
											v-model.number="rate.sell_rate"
											type="number"
											min="0"
											step="0.0001"
											class="w-24 text-end text-sm border border-gray-300 rounded px-2 py-1 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-amber-700"
										/>
										<span v-else class="text-amber-700">{{ formatRate(rate.sell_rate) }}</span>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
					<!-- Save Rates Button -->
					<div v-if="isEditingRates" class="px-4 py-2 bg-gray-50 border-t border-gray-200 flex justify-end">
						<Button
							variant="solid"
							theme="blue"
							:loading="isSavingRates"
							@click="handleSaveRates"
						>
							{{ __('حفظ الأسعار') }}
						</Button>
					</div>
				</div>

				<!-- Transaction Section -->
				<div class="flex flex-col gap-4">
					<!-- Buy / Sell Toggle -->
					<div class="flex gap-2">
						<button
							@click="transactionType = 'Buy'"
							:class="[
								'flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all border',
								transactionType === 'Buy'
									? 'bg-green-600 text-white border-green-600'
									: 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
							]"
						>
							{{ __('شراء') }}
						</button>
						<button
							@click="transactionType = 'Sell'"
							:class="[
								'flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all border',
								transactionType === 'Sell'
									? 'bg-amber-600 text-white border-amber-600'
									: 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
							]"
						>
							{{ __('بيع') }}
						</button>
					</div>

					<!-- Transaction Type Description -->
					<div class="text-xs text-gray-500 bg-gray-50 rounded-lg px-3 py-2 text-center">
						<span v-if="transactionType === 'Buy' && sourceCurrency && targetCurrency">
							{{ __('عملية: شراء {0} — نستلم {0} وندفع {1}', [sourceCurrency, targetCurrency]) }}
						</span>
						<span v-else-if="transactionType === 'Sell' && sourceCurrency && targetCurrency">
							{{ __('عملية: بيع {0} — ندفع {0} ونستلم {1}', [sourceCurrency, targetCurrency]) }}
						</span>
						<span v-else>
							{{ __('اختر نوع العملية والعملات') }}
						</span>
					</div>

					<!-- Currency 1 -->
					<div class="flex flex-col gap-1">
						<label class="text-sm font-medium text-gray-700">{{ __('العملة الأولى') }}</label>
						<select
							v-model="sourceCurrency"
							class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						>
							<option value="">{{ __('اختر العملة') }}</option>
							<option
								v-for="row in allCurrencies"
								:key="row.currency"
								:value="row.currency"
							>
								{{ row.currency }}
							</option>
						</select>
					</div>

					<!-- Amount 1 -->
					<div class="flex flex-col gap-1">
						<label class="text-sm font-medium text-gray-700">
							{{ __('مبلغ العملة الأولى') }}
						</label>
						<input
							v-model.number="amount"
							type="number"
							min="0.01"
							step="0.01"
							class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							:placeholder="__('أدخل المبلغ')"
						/>
					</div>

					<!-- Currency 2 -->
					<div class="flex flex-col gap-1">
						<label class="text-sm font-medium text-gray-700">{{ __('العملة الثانية') }}</label>
						<select
							v-model="targetCurrency"
							class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						>
							<option value="">{{ __('اختر العملة') }}</option>
							<option
								v-for="row in availableTargetCurrencies"
								:key="row.currency"
								:value="row.currency"
							>
								{{ row.currency }}
							</option>
						</select>
					</div>

					<!-- Exchange Rate -->
					<div class="flex flex-col gap-1">
						<label class="text-sm font-medium text-gray-700">
							{{ __('سعر الصرف') }}
							<span v-if="isRateAutoFilled" class="text-xs text-green-600 font-normal">({{ __('تلقائي') }})</span>
						</label>
						<input
							v-model.number="exchangeRate"
							type="number"
							min="0.000001"
							step="0.0001"
							class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							:placeholder="__('أدخل السعر أو اتركه فارغاً للتعبئة التلقائية')"
						/>
					</div>

					<!-- Amount 2 -->
					<div class="flex flex-col gap-1">
						<label class="text-sm font-medium text-gray-700">
							{{ __('مبلغ العملة الثانية') }}
						</label>
						<input
							v-model.number="targetAmount"
							type="number"
							min="0.01"
							step="0.01"
							class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-gray-50"
						/>
					</div>

					<!-- Summary Card -->
					<div
						v-if="sourceCurrency && targetCurrency && amount > 0 && exchangeRate > 0"
						:class="[
							'border rounded-lg p-3',
							transactionType === 'Buy' ? 'bg-green-50 border-green-200' : 'bg-amber-50 border-amber-200'
						]"
					>
						<p class="text-sm font-medium text-center"
							:class="transactionType === 'Buy' ? 'text-green-800' : 'text-amber-800'"
						>
							{{ transactionType === 'Buy' ? __('شراء') : __('بيع') }} {{ formatNumber(amount) }} {{ sourceCurrency }}
							<span class="mx-1">→</span>
							{{ formatNumber(targetAmount) }} {{ targetCurrency }}
							<span class="text-xs block mt-1"
								:class="transactionType === 'Buy' ? 'text-green-600' : 'text-amber-600'"
							>
								{{ __('السعر: {0}', [formatNumber(exchangeRate)]) }}
							</span>
						</p>
					</div>

					<!-- Error Messages -->
					<div v-if="errors.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-3">
						<ul class="text-sm text-red-700 space-y-1">
							<li v-for="(error, idx) in errors" :key="idx">
								• {{ error }}
							</li>
						</ul>
					</div>
				</div>
			</div>
		</template>
		<template #actions>
			<div class="flex gap-2 w-full">
				<Button
					class="flex-1"
					variant="subtle"
					@click="handleClose"
				>
					{{ __('إلغاء') }}
				</Button>
				<Button
					class="flex-1"
					variant="solid"
					:theme="transactionType === 'Buy' ? 'green' : 'amber'"
					:loading="isSubmitting"
					:disabled="!canSubmit"
					@click="handleConfirm"
				>
					{{ transactionType === 'Buy' ? __('تأكيد الشراء') : __('تأكيد البيع') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { computed, ref, watch } from "vue"
import { Dialog, Button, call } from "frappe-ui"
import { useToast } from "@/composables/useToast"

const props = defineProps({
	modelValue: Boolean,
	currencySetup: {
		type: Array,
		default: () => [],
	},
	posOpeningShift: String,
	posProfile: String,
})

const emit = defineEmits(["update:modelValue", "exchange-completed"])

const { showSuccess, showError } = useToast()

const transactionType = ref("Buy")
const sourceCurrency = ref("")
const targetCurrency = ref("")
const amount = ref(0)
const exchangeRate = ref(0)
const isSubmitting = ref(false)
const exchangeRates = ref([])
const editableRates = ref([])
const companyCurrency = ref("")
const isRateAutoFilled = ref(false)
const isEditingRates = ref(false)
const isSavingRates = ref(false)

// Fetch exchange rates when dialog opens
watch(() => props.modelValue, async (isOpen) => {
	if (isOpen && props.posProfile) {
		try {
			const result = await call(
				"pos_next.api.currency_exchange.get_exchange_rates",
				{ pos_profile: props.posProfile }
			)
			if (result) {
				exchangeRates.value = result.rates || []
				editableRates.value = (result.rates || []).map(r => ({
					currency: r.currency,
					buy_rate: r.buy_rate ?? 0,
					sell_rate: r.sell_rate ?? 0,
				}))
				companyCurrency.value = result.company_currency || ""
				// Auto-select company currency as Currency 2 if available
				if (companyCurrency.value) {
					const hasCompanyCurrency = props.currencySetup.some(
						row => row.currency === companyCurrency.value
					)
					if (hasCompanyCurrency && sourceCurrency.value !== companyCurrency.value) {
						targetCurrency.value = companyCurrency.value
					}
				}
			}
		} catch (err) {
			console.error("Failed to fetch exchange rates:", err)
		}
	}
})

const allCurrencies = computed(() => props.currencySetup)

// Available target currencies (exclude source)
const availableTargetCurrencies = computed(() => {
	return props.currencySetup.filter(
		(row) => row.currency !== sourceCurrency.value
	)
})

// Auto-clear target when source changes
watch(sourceCurrency, () => {
	if (targetCurrency.value === sourceCurrency.value) {
		targetCurrency.value = ""
	}
	tryAutoFillRate()
})

// Auto-fill rate when target changes or transaction type changes
watch([targetCurrency, transactionType], () => {
	tryAutoFillRate()
})

function tryAutoFillRate() {
	if (!sourceCurrency.value || !targetCurrency.value || !companyCurrency.value) {
		isRateAutoFilled.value = false
		return
	}
	// Only auto-fill if target is the company default currency
	if (targetCurrency.value !== companyCurrency.value) {
		isRateAutoFilled.value = false
		return
	}
	const rateRow = exchangeRates.value.find(r => r.currency === sourceCurrency.value)
	if (!rateRow) {
		isRateAutoFilled.value = false
		return
	}
	if (transactionType.value === "Buy" && rateRow.buy_rate > 0) {
		exchangeRate.value = parseFloat(rateRow.buy_rate.toFixed(6))
		isRateAutoFilled.value = true
	} else if (transactionType.value === "Sell" && rateRow.sell_rate > 0) {
		exchangeRate.value = parseFloat(rateRow.sell_rate.toFixed(6))
		isRateAutoFilled.value = true
	} else {
		isRateAutoFilled.value = false
	}
}

// Calculate target amount automatically
const targetAmount = computed({
	get() {
		if (amount.value > 0 && exchangeRate.value > 0) {
			return parseFloat((amount.value * exchangeRate.value).toFixed(2))
		}
		return 0
	},
	set(val) {
		if (amount.value > 0 && val > 0) {
			exchangeRate.value = parseFloat((val / amount.value).toFixed(6))
			isRateAutoFilled.value = false
		}
	},
})

const errors = computed(() => {
	const errs = []
	if (!sourceCurrency.value) errs.push(__('العملة الأولى مطلوبة'))
	if (!targetCurrency.value) errs.push(__('العملة الثانية مطلوبة'))
	if (sourceCurrency.value === targetCurrency.value) errs.push(__('العملة الأولى والثانية لا يمكن أن تكونا نفسهما'))
	if (amount.value <= 0) errs.push(__('المبلغ يجب أن يكون أكبر من صفر'))
	if (exchangeRate.value <= 0) errs.push(__('سعر الصرف يجب أن يكون أكبر من صفر'))
	return errs
})

const canSubmit = computed(() => {
	return (
		sourceCurrency.value &&
		targetCurrency.value &&
		sourceCurrency.value !== targetCurrency.value &&
		amount.value > 0 &&
		exchangeRate.value > 0 &&
		!isSubmitting.value
	)
})

function formatNumber(val) {
	return val ? parseFloat(val).toFixed(2) : '0.00'
}

function formatRate(val) {
	if (!val || val <= 0) return '-'
	return parseFloat(val).toFixed(4)
}

function handleClose() {
	emit('update:modelValue', false)
	resetForm()
}

function resetForm() {
	transactionType.value = "Buy"
	sourceCurrency.value = ""
	targetCurrency.value = ""
	amount.value = 0
	exchangeRate.value = 0
	isRateAutoFilled.value = false
	isSubmitting.value = false
	isEditingRates.value = false
	isSavingRates.value = false
}

async function handleSaveRates() {
	if (!props.posProfile || editableRates.value.length === 0) return
	isSavingRates.value = true
	try {
		const result = await call(
			"pos_next.api.currency_exchange.update_exchange_rates",
			{
				pos_profile: props.posProfile,
				rates: editableRates.value.map(r => ({
					currency: r.currency,
					buy_rate: r.buy_rate,
					sell_rate: r.sell_rate,
				})),
			}
		)
		if (result?.success) {
			// Sync back
			exchangeRates.value = editableRates.value.map(r => ({
				currency: r.currency,
				buy_rate: r.buy_rate,
				sell_rate: r.sell_rate,
			}))
			isEditingRates.value = false
			showSuccess(__('تم حفظ الأسعار بنجاح'))
		}
	} catch (error) {
		showError(error.message || __('فشل حفظ الأسعار'))
	} finally {
		isSavingRates.value = false
	}
}

async function handleConfirm() {
	if (!canSubmit.value) return

	isSubmitting.value = true
	try {
		const result = await call(
			"pos_next.api.currency_exchange.create_exchange",
			{
				source_currency: sourceCurrency.value,
				target_currency: targetCurrency.value,
				amount: amount.value,
				exchange_rate: exchangeRate.value,
				transaction_type: transactionType.value,
				pos_opening_shift: props.posOpeningShift,
				pos_profile: props.posProfile,
			}
		)

		if (result) {
			const actionLabel = transactionType.value === 'Buy' ? __('تم الشراء') : __('تم البيع')
			showSuccess(
				__('{0} {1} {2} → {3} {4}', [
					actionLabel,
					formatNumber(amount.value),
					sourceCurrency.value,
					formatNumber(result.target_amount),
					targetCurrency.value,
				])
			)
			emit('exchange-completed', result)
			handleClose()
		}
	} catch (error) {
		showError(error.message || __('فشل إنشاء عملية تصريف العملات'))
	} finally {
		isSubmitting.value = false
	}
}
</script>
