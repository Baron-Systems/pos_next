<template>
<Dialog v-model="show" :options="{ title: __('المورد'), size: 'xl' }" @after-leave="() => { console.log('SupplierPaymentDialog after-leave'); $emit('after-leave') }">
<template #body-content>
<div class="flex flex-col gap-4 min-h-[500px]">
<!-- Supplier Selection -->
<SupplierSection
:supplier="localSupplier"
@select-supplier="handleSelectSupplier"
@create-supplier="handleCreateSupplier"
@edit-supplier="handleEditSupplier"
@supplier-payment="handlePaymentFromSection"
@remove-supplier="handleSelectSupplier(null)"
/>

<!-- Payment Area (only when supplier selected) -->
<div v-if="localSupplier" class="bg-gray-50 border border-gray-200 rounded-xl p-4">
<div class="flex items-center justify-between mb-4">
<div>
<p class="text-sm font-semibold text-gray-800">{{ localSupplier.supplier_name || localSupplier.name }}</p>
<p v-if="localSupplier.mobile_no" class="text-xs text-gray-500">{{ localSupplier.mobile_no }}</p>
</div>
<div class="text-end">
<p class="text-xs text-gray-600">{{ __('رصيد الحساب') }}</p>
<p v-if="loading" class="text-xs text-gray-400">{{ __('جاري التحميل...') }}</p>
<p v-else class="text-lg font-bold" :class="accountBalance > 0 ? 'text-red-600' : accountBalance < 0 ? 'text-green-600' : 'text-gray-600'">
{{ formatCurrency(accountBalance) }}
</p>
</div>
</div>

<div class="flex items-end gap-3">
<div class="flex-1">
<label class="block text-xs font-medium text-gray-600 mb-1">{{ __('المبلغ') }}</label>
<Input
v-model.number="paymentAmount"
type="number"
:placeholder="__('أدخل المبلغ')"
step="0.01"
@keyup.enter="executePayment"
/>
</div>
<Button
@click="executePayment"
:loading="paying"
:disabled="!paymentAmount || paymentAmount === 0"
theme="green"
variant="solid"
>
{{ paymentAmount < 0 ? __('القبض من المورد') : __('الدفع للمورد') }}
</Button>
</div>
</div>
<div v-else class="text-center py-6 text-sm text-gray-400">
{{ __('اختر موردًا لعرض تفاصيل الدفع') }}
</div>
</div>
</template>
</Dialog>
</template>

<script setup>
import SupplierSection from "@/components/sale/SupplierSection.vue"
import { call } from "@/utils/apiWrapper"
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"
import { useToast } from "@/composables/useToast"
import { Button, Dialog, Input } from "frappe-ui"
import { computed, ref, watch } from "vue"

const props = defineProps({
modelValue: Boolean,
supplier: { type: Object, default: null },
company: { type: String, default: "" },
openingShift: { type: String, default: "" },
modeOfPayment: { type: String, default: "Cash" },
})

const emit = defineEmits([
"update:modelValue",
"select-supplier",
"create-supplier",
"edit-supplier",
"payment-created",
"after-leave",
])

const { showSuccess, showError } = useToast()

const show = computed({
get: () => props.modelValue,
set: (val) => emit("update:modelValue", val),
})

const localSupplier = computed({
get: () => props.supplier,
set: (val) => emit("select-supplier", val),
})

const loading = ref(false)
const paying = ref(false)
const paymentAmount = ref(null)
const summary = ref({ outstanding_balance: 0, currency: "" })

const accountBalance = computed(() => summary.value.outstanding_balance || 0)

function formatCurrency(value) {
return formatCurrencyUtil(value, summary.value.currency || "USD")
}

async function loadData(supplierRef) {
const sup = supplierRef?.name || supplierRef || props.supplier?.name || props.supplier
if (!sup || !props.company) return
loading.value = true
try {
const result = await call("pos_next.api.supplier.get_supplier_financial_summary", {
supplier: sup,
company: props.company,
})
summary.value = result || { outstanding_balance: 0, currency: "" }
} catch (e) {
showError(e?.message || e)
} finally {
loading.value = false
}
}

async function executePayment() {
const sup = props.supplier?.name || props.supplier
if (!sup || !props.company || !paymentAmount.value || paymentAmount.value === 0) return
paying.value = true
try {
const result = await call("pos_next.api.supplier.create_supplier_payment", {
supplier: sup,
company: props.company,
amount: Math.abs(paymentAmount.value),
mode_of_payment: props.modeOfPayment,
payment_type: paymentAmount.value < 0 ? "Receive" : "Pay",
pos_opening_shift: props.openingShift || undefined,
})
showSuccess(__("تم إنشاء الدفع {0} بنجاح", [result.payment_entry]))
paymentAmount.value = null
await loadData()
emit("payment-created", result)
} catch (e) {
showError(e?.message || e)
} finally {
paying.value = false
}
}

function handleSelectSupplier(sup) {
emit("select-supplier", sup)
if (sup) loadData(sup)
}

function handleCreateSupplier(searchValue) {
emit("create-supplier", searchValue)
}

function handleEditSupplier(sup) {
emit("edit-supplier", sup)
}

function handlePaymentFromSection(sup) {
// Payment button clicked inside SupplierSection; do nothing extra here
}

watch(show, (val) => {
if (val) {
paymentAmount.value = null
if (props.supplier) loadData()
}
})
</script>
