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
class="payment-amount-input"
:placeholder="__('أدخل المبلغ')"
step="0.01"
@input="(val) => paymentAmount = Number(val)"
@keyup.enter="executePayment"
/>
</div>
<Button
@click="executePayment"
:loading="paying"
:disabled="!paymentAmount || paymentAmount === 0"
:theme="paymentAmount < 0 ? 'red' : 'green'"
variant="solid"
>
{{ paymentAmount < 0 ? __('القبض من المورد') : __('الدفع للمورد') }}
</Button>
</div>
</div>
<div v-if='localSupplier' class='bg-white border border-gray-200 rounded-xl p-4'>
<div class='flex items-center justify-between mb-3'>
<h4 class='text-sm font-semibold text-gray-800'>{{ __('تقرير المورد') }}</h4>
<div class='flex items-center gap-2'>
<Button v-if='!showLastMonth' @click='showLastMonth = true' variant='outline'>{{ __('آخر شهر') }}</Button>
<Button v-else @click='showLastMonth = false' variant='solid' theme='blue'>{{ __('إظهار الكل') }}</Button>
<Button @click='printReport' variant='outline'>{{ __('طباعة التقرير') }}</Button>
</div>
</div>
<div class='overflow-auto max-h-[300px]'>
<table v-if='filteredStatement.length' class='min-w-full text-xs'>
<thead class='bg-gray-50 sticky top-0'>
<tr>
<th class='px-3 py-2 text-start font-medium text-gray-600'>{{ __('التاريخ') }}</th>
<th class='px-3 py-2 text-start font-medium text-gray-600'>{{ __('الرقم') }}</th>
<th class='px-3 py-2 text-start font-medium text-gray-600'>{{ __('النوع') }}</th>
<th class='px-3 py-2 text-end font-medium text-gray-600'>{{ __('المبلغ') }}</th>
<th class='px-3 py-2 text-start font-medium text-gray-600'>{{ __('التفاصيل') }}</th>
</tr>
</thead>
<tbody class='divide-y divide-gray-100'>
<template v-for='t in filteredStatement' :key='`${t.type}-${t.name}`'>
<tr class='hover:bg-gray-50'>
<td class='px-3 py-2 text-gray-600'>{{ formatDate(t.posting_date) }}</td>
<td class='px-3 py-2 font-medium text-gray-900'>{{ t.name }}</td>
<td class='px-3 py-2 text-gray-600'>{{ formatRecordType(t) }}</td>
<td class='px-3 py-2 text-end font-semibold'>{{ formatCurrency(t.type === 'invoice' ? t.grand_total : t.paid_amount) }}</td>
<td class='px-3 py-2 text-start text-gray-600'>{{ t.type === 'invoice' ? formatCurrency(t.outstanding_amount) : t.mode_of_payment }}</td>
</tr>
<tr v-if='t.items && t.items.length'>
<td colspan='5' class='px-3 pb-3'>
<div class='bg-gray-50 border border-gray-100 rounded p-2'>
<table class='min-w-full text-[10px]'>
<thead>
<tr class='text-gray-500'>
<th class='px-2 py-1 text-start'>{{ __('الصنف') }}</th>
<th class='px-2 py-1 text-end'>{{ __('الكمية') }}</th>
<th class='px-2 py-1 text-end'>{{ __('السعر') }}</th>
<th class='px-2 py-1 text-end'>{{ __('المبلغ') }}</th>
</tr>
</thead>
<tbody class='divide-y divide-gray-100'>
<tr v-for='item in t.items' :key='item.name'>
<td class='px-2 py-1 text-start text-gray-700'>{{ item.item_name || item.item_code }}</td>
<td class='px-2 py-1 text-end text-gray-700'>{{ item.qty }}</td>
<td class='px-2 py-1 text-end text-gray-700'>{{ formatCurrency(item.rate) }}</td>
<td class='px-2 py-1 text-end font-medium text-gray-900'>{{ formatCurrency(item.amount) }}</td>
</tr>
</tbody>
</table>
</div>
</td>
</tr>
</template>
</tbody>
</table>
<div v-else class='text-center py-4 text-sm text-gray-500'>
{{ __('لا توجد حركات') }}
</div>
</div>
</div>
<div v-if='!localSupplier' class='text-center py-6 text-sm text-gray-400'>
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
const statement = ref([])
const showLastMonth = ref(false)
const letterhead = ref({ content: "", footer: "" })

const accountBalance = computed(() => summary.value.outstanding_balance || 0)

const filteredStatement = computed(() => {
if (!showLastMonth.value) return statement.value
const cutoff = new Date()
cutoff.setDate(cutoff.getDate() - 30)
cutoff.setHours(0, 0, 0, 0)
return statement.value.filter((t) => t.posting_date && new Date(t.posting_date) >= cutoff)
})

function formatCurrency(value) {
return formatCurrencyUtil(value, summary.value.currency || "USD")
}

function formatDate(date) {
if (!date) return "-"
return new Date(date).toLocaleDateString("ar-SA")
}

function formatPaymentType(type) {
const m = { Receive: __('قبض'), Pay: __('دفع') }
return m[type] || type
}

function formatStatus(status) {
const m = { Paid: __('مدفوعة'), Unpaid: __('غير مدفوعة'), Overdue: __('متأخرة'), "Partly Paid": __('مدفوعة جزئياً'), Cancelled: __('ملغية'), Draft: __('مسودة') }
return m[status] || status
}

function formatRecordType(record) {
if (record.type === 'payment') {
return record.payment_type === 'Pay' ? __('دفع للمورد') : __('قبض من المورد')
}
return record.is_return ? __('مرتجع مشتريات') : __('فاتورة مشتريات')
}

async function loadData(supplierRef) {
const sup = supplierRef?.name || supplierRef || props.supplier?.name || props.supplier
if (!sup || !props.company) return
loading.value = true
try {
const [sumResult, stmtResult, lhResult] = await Promise.all([
call("pos_next.api.supplier.get_supplier_financial_summary", { supplier: sup, company: props.company }),
call("pos_next.api.supplier.get_supplier_statement", { supplier: sup, company: props.company, limit: 300 }),
call("pos_next.api.utilities.get_company_letterhead", { company: props.company }),
])
summary.value = sumResult || { outstanding_balance: 0, currency: "" }
statement.value = Array.isArray(stmtResult) ? stmtResult : []
letterhead.value = lhResult || { content: "", footer: "" }
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
	const input = document.querySelector('.payment-amount-input input')
	if (input) {
		input.focus()
	}
}

function printReport() {
const w = window.open('', '_blank', 'width=900,height=700')
if (!w) return
const supplierName = localSupplier.value?.supplier_name || localSupplier.value?.name || ''
const rows = filteredStatement.value.map((t) => {
  const isInv = t.type === 'invoice'
  const amount = formatCurrency(isInv ? t.grand_total : t.paid_amount)
  const detail = isInv ? formatCurrency(t.outstanding_amount) : t.mode_of_payment
  let itemsHtml = ''
  if (isInv && t.items && t.items.length) {
    itemsHtml = '<table class="items"><thead><tr><th>' + __('الصنف') + '</th><th>' + __('الكمية') + '</th><th>' + __('السعر') + '</th><th>' + __('المبلغ') + '</th></tr></thead><tbody>' +
      t.items.map((i) => '<tr><td>' + (i.item_name || i.item_code) + '</td><td>' + i.qty + '</td><td>' + formatCurrency(i.rate) + '</td><td>' + formatCurrency(i.amount) + '</td></tr>').join('') +
      '</tbody></table>'
  }
  return '<tr class="' + (isInv ? 'inv' : 'pay') + '">' +
    '<td>' + formatDate(t.posting_date) + '</td>' +
    '<td>' + t.name + '</td>' +
    '<td>' + (isInv ? (t.is_return ? __('مرتجع مشتريات') : __('فاتورة مشتريات')) : (t.payment_type === 'Pay' ? __('دفع للمورد') : __('قبض من المورد'))) + '</td>' +
    '<td class="amount">' + amount + '</td>' +
    '<td>' + detail + '</td>' +
    '</tr>' +
    (itemsHtml ? '<tr class="items-row"><td colspan="5">' + itemsHtml + '</td></tr>' : '')
}).join('')

const html = `<!DOCTYPE html>
<html dir=rtl>
<head>
<meta charset=UTF-8>
<title>${__('تقرير المورد')}</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: 'Tahoma', 'Arial', sans-serif; margin: 0; padding: 24px; background: #fff; color: #333; }
  .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #2563eb; padding-bottom: 12px; }
  .header h2 { margin: 0 0 6px; color: #1e40af; font-size: 22px; }
  .header .meta { margin: 0; color: #666; font-size: 13px; }
  table { width: 100%; border-collapse: collapse; margin-top: 12px; }
  th, td { border: 1px solid #e5e7eb; padding: 8px 10px; text-align: right; font-size: 13px; }
  th { background: #f3f4f6; color: #374151; font-weight: 600; }
  tr.inv td.amount { color: #1e40af; font-weight: 600; }
  tr.pay td.amount { color: #047857; font-weight: 600; }
  tr.items-row td { background: #f9fafb; padding: 0 10px 12px; }
  table.items { margin-top: 6px; border: none; }
  table.items th, table.items td { border: 1px solid #d1d5db; font-size: 11px; padding: 5px 8px; }
  .footer { margin-top: 24px; text-align: center; font-size: 12px; color: #9ca3af; }
  .letterhead-top { margin-bottom: 12px; }
  .letterhead-footer { margin-top: 24px; }
</style>
</head>
<body>
<div class='letterhead-top'>${letterhead.value.content}</div>
<div class='header'>
  <h2>${__('تقرير المورد')}</h2>
  <p class='meta'>${supplierName} · ${props.company} · ${__('رصيد الحساب')}: ${formatCurrency(accountBalance.value)} · ${new Date().toLocaleDateString('ar-SA')}</p>
</div>
<table>
  <thead>
    <tr>
      <th>${__('التاريخ')}</th>
      <th>${__('الرقم')}</th>
      <th>${__('النوع')}</th>
      <th>${__('المبلغ')}</th>
      <th>${__('التفاصيل')}</th>
    </tr>
  </thead>
  <tbody>
    ${rows}
  </tbody>
</table>
<div class='footer'>${__('تقرير مورد')}</div>
<div class='letterhead-footer'>${letterhead.value.footer}</div>
</body>
</html>`
w.document.open()
w.document.write(html)
w.document.close()
w.print()
}

watch(show, (val) => {
if (val) {
paymentAmount.value = null
if (props.supplier) loadData()
}
})
</script>
