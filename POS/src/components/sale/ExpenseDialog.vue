<template>
	<Dialog
		:modelValue="modelValue"
		@update:modelValue="$emit('update:modelValue', $event)"
		:options="{ title: __('تسجيل مصروف الوردية'), size: 'sm' }"
	>
		<template #body-content>
			<div class="flex flex-col gap-4 py-2">
				<!-- Payment Method -->
				<div class="flex flex-col gap-1">
					<label class="text-sm font-medium text-gray-700">{{ __('طريقة الدفع') }}</label>
					<select
						v-model="modeOfPayment"
						class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-white"
					>
						<option value="" disabled>{{ __('اختر طريقة الدفع') }}</option>
						<option v-for="method in paymentMethods" :key="method.mode_of_payment" :value="method.mode_of_payment">
							{{ method.mode_of_payment }}
						</option>
					</select>
				</div>

				<!-- Expense Name -->
				<div class="flex flex-col gap-1">
					<label class="text-sm font-medium text-gray-700">{{ __('اسم المصروف') }}</label>
					<select
						v-model="selectedExpense"
						class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-rose-500 focus:border-rose-500 bg-white"
					>
						<option value="" disabled>{{ __('اختر المصروف') }}</option>
						<option v-for="ex in nameExpenses" :key="ex.name" :value="ex.name">
							{{ ex.name_of_the_expense }}
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
						class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
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
						class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
					/>
				</div>

				<!-- Remarks -->
				<div class="flex flex-col gap-1">
					<label class="text-sm font-medium text-gray-700">{{ __('ملاحظات') }}</label>
					<input
						v-model="remarks"
						type="text"
						class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
						:placeholder="__('اختياري')"
					/>
				</div>

				<!-- Errors -->
				<div v-if="errors.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-3">
					<ul class="text-sm text-red-700 space-y-1">
						<li v-for="(error, idx) in errors" :key="idx">• {{ error }}</li>
					</ul>
				</div>

				<!-- No expenses message -->
				<div v-else-if="props.modelValue && !isLoading && nameExpenses.length === 0" class="bg-amber-50 border border-amber-200 rounded-lg p-3">
					<p class="text-sm text-amber-700">{{ __('لا توجد مصاريف معرفة لهذه الشركة') }}</p>
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
					theme="rose"
					:loading="isSubmitting"
					:disabled="!canSubmit"
					@click="handleSubmit"
				>
					{{ __('تسجيل المصروف') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { Button, Dialog } from "frappe-ui"
import { call } from "@/utils/apiWrapper"
import { useToast } from "@/composables/useToast"
import { computed, ref, watch, watchEffect, nextTick } from "vue"

const props = defineProps({
	modelValue: { type: Boolean, default: false },
	company: { type: String, default: "" },
	paymentMethods: { type: Array, default: () => [] },
	posOpeningShift: { type: String, default: "" },
})

const emit = defineEmits(["update:modelValue", "expense-created"])

const { showSuccess, showError } = useToast()

const modeOfPayment = ref("")
const selectedExpense = ref("")
const amount = ref(0)
const postingDate = ref(new Date().toISOString().split("T")[0])
const remarks = ref("")
const isSubmitting = ref(false)
const isLoading = ref(false)
const errors = ref([])
const nameExpenses = ref([])
const amountInput = ref(null)

const selectedExpenseData = computed(() =>
	nameExpenses.value.find(ex => ex.name === selectedExpense.value),
)

const expenseAccount = computed(() => selectedExpenseData.value?.account || "")
const expenseName = computed(() => selectedExpenseData.value?.name_of_the_expense || selectedExpense.value)

const canSubmit = computed(() =>
	props.company &&
	modeOfPayment.value &&
	selectedExpense.value &&
	expenseAccount.value &&
	Number(amount.value) > 0,
)

watchEffect(async () => {
	if (props.modelValue && props.company) {
		errors.value = []
		postingDate.value = new Date().toISOString().split("T")[0]
		isLoading.value = true
		try {
			nameExpenses.value = await call("pos_next.api.journal.get_name_expenses", { company: props.company }) || []
		} catch (e) {
			nameExpenses.value = []
			errors.value = [e?.message || e?.toString() || __("فشل تحميل المصاريف")]
		} finally {
			isLoading.value = false
		}
	}
})

watch(() => props.modelValue, (newVal, oldVal) => {
	if (oldVal === true && newVal === false) {
		focusBarcode()
	}
})

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
		const result = await call("pos_next.api.journal.create_shift_expense", {
			company: props.company,
			mode_of_payment: modeOfPayment.value,
			expense_account: expenseAccount.value,
			expense_name: expenseName.value,
			name_expense: selectedExpense.value,
			amount: Number(amount.value),
			posting_date: postingDate.value,
			remarks: remarks.value?.trim() || undefined,
			pos_opening_shift: props.posOpeningShift || undefined,
		})
		showSuccess(__("تم تسجيل المصروف {0}", [result.journal_entry]))
		emit("expense-created", result)
		handleClose()
		// Reset form
		modeOfPayment.value = ""
		selectedExpense.value = ""
		amount.value = 0
		remarks.value = ""
	} catch (e) {
		const message = e?.message || e?.toString() || __("فشل تسجيل المصروف")
		errors.value = [message]
		showError(message)
	} finally {
		isSubmitting.value = false
	}
}
</script>
