<template>
	<Dialog
		:modelValue="modelValue"
		@update:modelValue="$emit('update:modelValue', $event)"
		:options="{ title: __('تحويل من حساب إلى حساب'), size: 'sm' }"
	>
		<template #body-content>
			<div class="flex flex-col gap-4 py-2">
				<!-- From Payment Method / Account -->
				<div class="flex flex-col gap-1">
					<label class="text-sm font-medium text-gray-700">{{ __('من حساب') }}</label>
					<select
						v-model="fromModeOfPayment"
						class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
					>
						<option value="" disabled>{{ __('اختر حساب المصدر') }}</option>
						<option v-for="method in paymentMethods" :key="method.mode_of_payment" :value="method.mode_of_payment">
							{{ method.mode_of_payment }}
						</option>
					</select>
				</div>

				<!-- To Payment Method / Account -->
				<div class="flex flex-col gap-1">
					<label class="text-sm font-medium text-gray-700">{{ __('إلى حساب') }}</label>
					<select
						v-model="toModeOfPayment"
						class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
					>
						<option value="" disabled>{{ __('اختر حساب الهدف') }}</option>
						<option v-for="method in paymentMethods" :key="method.mode_of_payment" :value="method.mode_of_payment">
							{{ method.mode_of_payment }}
						</option>
					</select>
				</div>

				<!-- Amount -->
				<div class="flex flex-col gap-1">
					<label class="text-sm font-medium text-gray-700">{{ __('المبلغ') }}</label>
					<input
						v-model.number="amount"
						ref="amountInput"
						type="number"
						min="0.01"
						step="0.01"
						class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						:placeholder="__('أدخل المبلغ')"
						@focus="handleAmountFocus"
						@click="handleAmountClick"
						@mouseup.prevent
					/>
				</div>

				<!-- Posting Date -->
				<div class="flex flex-col gap-1">
					<label class="text-sm font-medium text-gray-700">{{ __('تاريخ القيد') }}</label>
					<input
						v-model="postingDate"
						type="date"
						class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>

				<!-- Reference No -->
				<div class="flex flex-col gap-1">
					<label class="text-sm font-medium text-gray-700">{{ __('رقم المرجع') }}</label>
					<input
						v-model="referenceNo"
						type="text"
						class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						:placeholder="__('اختياري')"
					/>
				</div>

				<!-- Remarks -->
				<div class="flex flex-col gap-1">
					<label class="text-sm font-medium text-gray-700">{{ __('ملاحظات') }}</label>
					<input
						v-model="remarks"
						type="text"
						class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						:placeholder="__('اختياري')"
					/>
				</div>

				<!-- Errors -->
				<div v-if="errors.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-3">
					<ul class="text-sm text-red-700 space-y-1">
						<li v-for="(error, idx) in errors" :key="idx">• {{ error }}</li>
					</ul>
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
					theme="blue"
					:loading="isSubmitting"
					:disabled="!canSubmit"
					@click="handleSubmit"
				>
					{{ __('تحويل') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { Button, Dialog } from "frappe-ui"
import { call } from "@/utils/apiWrapper"
import { useToast } from "@/composables/useToast"
import { computed, ref, watch, nextTick } from "vue"

const props = defineProps({
	modelValue: { type: Boolean, default: false },
	company: { type: String, default: "" },
	paymentMethods: { type: Array, default: () => [] },
	posOpeningShift: { type: String, default: "" },
})

const emit = defineEmits(["update:modelValue", "transfer-created"])

const { showSuccess, showError } = useToast()

const fromModeOfPayment = ref("")
const toModeOfPayment = ref("")
const amount = ref(0)
const postingDate = ref(new Date().toISOString().split("T")[0])
const referenceNo = ref("")
const remarks = ref("")
const isSubmitting = ref(false)
const errors = ref([])
const amountInput = ref(null)

function getCashPaymentMethod(methods) {
	if (!methods || methods.length === 0) return null
	const defaultCash = methods.find(
		(m) => (m.default === 1 || m.default === true) && (m.type || "").toLowerCase() === "cash"
	)
	if (defaultCash) return defaultCash
	const byType = methods.find((m) => (m.type || "").toLowerCase() === "cash")
	if (byType) return byType
	const byName = methods.find((m) => /نقدي|cash/i.test(m.mode_of_payment))
	return byName || methods.find((m) => m.default === 1 || m.default === true) || methods[0]
}

function setDefaultFromPaymentMethod() {
	if (fromModeOfPayment.value || !props.paymentMethods?.length) return
	const method = getCashPaymentMethod(props.paymentMethods)
	fromModeOfPayment.value = method ? method.mode_of_payment : props.paymentMethods[0].mode_of_payment
}

const canSubmit = computed(() =>
	props.company &&
	fromModeOfPayment.value &&
	toModeOfPayment.value &&
	fromModeOfPayment.value !== toModeOfPayment.value &&
	Number(amount.value) > 0,
)

watch(
	() => props.modelValue,
	(newVal, oldVal) => {
		if (newVal) {
			errors.value = []
			postingDate.value = new Date().toISOString().split("T")[0]
			setDefaultFromPaymentMethod()
		} else if (oldVal === true && newVal === false) {
			focusBarcode()
		}
	},
)

watch(() => props.paymentMethods, (methods) => {
	if (methods?.length) setDefaultFromPaymentMethod()
}, { immediate: true })

function focusBarcode() {
	// Wait for the Dialog's own focus/transition to finish before taking focus
	setTimeout(() => {
		const input = document.getElementById("item-search")
		if (input) {
			input.focus()
			input.select()
		}
	}, 300)
}

function selectAmountInput() {
	setTimeout(() => {
		amountInput.value?.select()
	}, 0)
}

function handleAmountFocus() {
	selectAmountInput()
}

function handleAmountClick() {
	selectAmountInput()
}

function handleClose() {
	emit("update:modelValue", false)
}

async function handleSubmit() {
	errors.value = []
	if (!canSubmit.value) return

	isSubmitting.value = true
	try {
		const result = await call("pos_next.api.journal.create_cash_to_card_transfer", {
			company: props.company,
			from_mode_of_payment: fromModeOfPayment.value,
			to_mode_of_payment: toModeOfPayment.value,
			amount: Number(amount.value),
			posting_date: postingDate.value,
			reference_no: referenceNo.value?.trim() || undefined,
			remarks: remarks.value?.trim() || undefined,
			pos_opening_shift: props.posOpeningShift || undefined,
		})
		showSuccess(__("تم إنشاء القيد {0}", [result.journal_entry]))
		emit("transfer-created", result)
		handleClose()
		// Reset form
		fromModeOfPayment.value = ""
		toModeOfPayment.value = ""
		amount.value = 0
		referenceNo.value = ""
		remarks.value = ""
	} catch (e) {
		const message = e?.message || e?.toString() || __("فشل إنشاء التحويل")
		errors.value = [message]
		showError(message)
	} finally {
		isSubmitting.value = false
	}
}
</script>
