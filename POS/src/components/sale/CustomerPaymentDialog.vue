<template>
<Dialog v-model="show" :options="{ title: __('دفع العميل'), size: 'xl' }" @after-leave="() => { console.log('CustomerPaymentDialog after-leave'); $emit('after-leave') }">
<template #body-content>
<div class="flex flex-col gap-4 min-h-[500px]">

<!-- Payment Area (only when supplier selected) -->
<div v-if="localCustomer" class="bg-gray-50 border border-gray-200 rounded-xl p-4">
<div class="flex items-center justify-between mb-4">
<div>
<p class="text-sm font-semibold text-gray-800">{{ localCustomer.customer_name || localCustomer.name }}</p>
<p v-if="localCustomer.mobile_no" class="text-xs text-gray-500">{{ localCustomer.mobile_no }}</p>
<div class="flex items-center gap-2 mt-1">
  <span class="text-xs text-gray-600">{{ __('إرسال تذكير') }}</span>
  <Button @click="openWhatsAppDialog" variant="solid" size="sm" class="!bg-white !hover:bg-gray-100 border-none p-1.5" :title="__('إرسال تذكير عبر واتساب')">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp" class="w-6 h-6" />
  </Button>
</div>
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
{{ paymentAmount < 0 ? __('الدفع للعميل') : __('القبض من العميل') }}
</Button>
</div>
</div>
<div v-if='localCustomer' class='bg-white border border-gray-200 rounded-xl p-4'>
<div class='flex items-center justify-between mb-3'>
<h4 class='text-sm font-semibold text-gray-800'>{{ __('تقرير العميل') }}</h4>
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
<div v-if='!localCustomer' class='text-center py-6 text-sm text-gray-400'>
{{ __('اختر عميلا لعرض تفاصيل الدفع') }}
</div>
</div>
</template>
</Dialog>

<!-- WhatsApp Dialog -->
<Dialog v-model="showWhatsAppDialog" :options="{ title: __('إرسال تذكير عبر واتساب'), size: 'md' }">
<template #body-content>
<div class="flex flex-col gap-4">
<div v-if="customerPhone" class="bg-green-50 border border-green-200 rounded-lg p-3">
<p class="text-sm text-green-800">
<span class="font-semibold">{{ __('رقم العميل:') }}</span> {{ customerPhone }}
</p>
</div>
<div v-else class="space-y-3">
<p class="text-sm text-gray-600">{{ __('لم يتم العثور على رقم هاتف للعميل. يرجى إدخال الرقم:') }}</p>
<div class="flex gap-2">
<select
v-model="countryCode"
class="px-2 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
>
<option value="+970">+970 🇵🇸</option>
<option value="+972">+972 🇮🇱</option>
<option value="+962">+962 🇯🇴</option>
<option value="+966">+966 🇸🇦</option>
<option value="+971">+971 🇦🇪</option>
<option value="+20">+20 🇪🇬</option>
<option value="+1">+1 🇺🇸</option>
<option value="+44">+44 🇬🇧</option>
</select>
<input
v-model="tempPhoneInput"
type="tel"
:placeholder="__('أدخل رقم الهاتف')"
class="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
/>
</div>
<p class="text-xs text-gray-500">{{ __('سيتم حفظ الرقم في بيانات العميل تلقائياً') }}</p>
</div>
<div class="bg-gray-50 border border-gray-200 rounded-lg p-3 space-y-2">
<p class="text-xs font-semibold text-gray-700">{{ __('محتوى الرسالة:') }}</p>
<div v-if="loading" class="text-sm text-gray-500">{{ __('جاري تحميل البيانات...') }}</div>
<template v-else>
<p class="text-sm text-gray-600">{{ __('تاريخ آخر دفعة:') }} {{ lastPaymentDate ? formatDate(lastPaymentDate) : __('غير متوفر') }}</p>
<p class="text-sm text-gray-600">{{ __('مبلغ آخر دفعة:') }} {{ formatCurrency(lastPaymentAmount) }}</p>
<p v-if="!lastPaymentDate" class="text-xs text-orange-600">{{ __('لم يتم العثور على دفعات سابقة') }}</p>
</template>
<p class="text-sm text-gray-600">{{ __('المبلغ المتبقي:') }} {{ formatCurrency(accountBalance) }}</p>
<p class="text-sm text-gray-600">{{ __('الشركة:') }} {{ props.company }}</p>
</div>
<div class="flex items-center gap-2">
<input
id="includePortal"
type="checkbox"
v-model="includePortalInfo"
class="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
/>
<label for="includePortal" class="text-sm text-gray-700 cursor-pointer">{{ __('تضمين معلومات بوابة العميل') }}</label>
</div>
<div v-if="includePortalInfo" class="bg-blue-50 border border-blue-200 rounded-lg p-3 space-y-1 text-sm">
<p class="text-blue-800"><span class="font-semibold">{{ __('رابط البوابة:') }}</span> {{ portalUrl }}</p>
<p class="text-blue-800"><span class="font-semibold">{{ __('اسم المستخدم:') }}</span> {{ localCustomer?.customer_name || localCustomer?.name }}</p>
<p class="text-blue-800"><span class="font-semibold">{{ __('رقم العميل:') }}</span> {{ localCustomer?.id_no || '-' }}</p>
</div>
<div class="space-y-2">
<label class="block text-xs font-medium text-gray-600">{{ __('إضافة نص:') }}</label>
<textarea
v-model="customMessageText"
:placeholder="__('أضف ملاحظات أو تفاصيل إضافية...')"
rows="3"
class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
></textarea>
</div>
</div>
</template>
<template #actions>
<Button variant="outline" @click="closeWhatsAppDialog">{{ __('إلغاء') }}</Button>
<Button theme="green" variant="solid" @click="sendWhatsAppMessage" :loading="updatingPhone" :disabled="!customerPhone && !tempPhoneInput">
{{ updatingPhone ? __('جاري الحفظ...') : __('إرسال عبر واتساب') }}
</Button>
</template>
</Dialog>
</template>

<script setup>
import { call } from "@/utils/apiWrapper"
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"
import { useToast } from "@/composables/useToast"
import { Button, Dialog, Input } from "frappe-ui"
import { computed, ref, watch } from "vue"

const props = defineProps({
modelValue: Boolean,
customer: { type: Object, default: null },
company: { type: String, default: "" },
openingShift: { type: String, default: "" },
modeOfPayment: { type: String, default: "Cash" },
})

const emit = defineEmits(["update:modelValue", "payment-created", "after-leave"])

const { showSuccess, showError } = useToast()

const show = computed({
get: () => props.modelValue,
set: (val) => emit("update:modelValue", val),
})

const localCustomer = computed(() => props.customer)

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
return record.payment_type === 'Pay' ? __('دفع للعميل') : __('قبض من العميل')
}
return record.is_return ? __('مرتجع مبيعات') : __('فاتورة مبيعات')
}

async function loadData(supplierRef) {
const sup = supplierRef?.name || supplierRef || props.customer?.name || props.customer
if (!sup || !props.company) return
loading.value = true
try {
const [sumResult, stmtResult, lhResult] = await Promise.all([
call("pos_next.api.customer_payment.get_customer_financial_summary", { customer: sup, company: props.company }),
call("pos_next.api.customer_payment.get_customer_statement", { customer: sup, company: props.company, limit: 300 }),
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
const sup = props.customer?.name || props.customer
if (!sup || !props.company || !paymentAmount.value || paymentAmount.value === 0) return
paying.value = true
try {
const result = await call("pos_next.api.customer_payment.create_customer_payment", {
customer: sup,
company: props.company,
amount: Math.abs(paymentAmount.value),
mode_of_payment: props.modeOfPayment,
payment_type: paymentAmount.value < 0 ? "Pay" : "Receive",
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





const lastPayment = computed(() => {
  const payments = statement.value.filter(t => t.type === 'payment')
  if (!payments.length) return null
  const sorted = [...payments].sort((a, b) => {
    const dateDiff = new Date(b.posting_date) - new Date(a.posting_date)
    if (dateDiff !== 0) return dateDiff
    return b.name.localeCompare(a.name)
  })
  return sorted[0]
})

const lastPaymentDate = computed(() => lastPayment.value?.posting_date || null)
const lastPaymentAmount = computed(() => lastPayment.value?.paid_amount || 0)

const showWhatsAppDialog = ref(false)
const customerPhone = ref("")
const tempPhoneInput = ref("")
const countryCode = ref("+970")
const customMessageText = ref("")
const includePortalInfo = ref(true)
const updatingPhone = ref(false)

const portalUrl = computed(() => {
  const domain = window.location.origin
  return `${domain}/portal`
})

async function openWhatsAppDialog() {
  const phone = localCustomer.value?.mobile_no || localCustomer.value?.phone || ""
  customerPhone.value = phone
  if (!phone) {
    tempPhoneInput.value = ""
  }
  await loadData()
  showWhatsAppDialog.value = true
}

function closeWhatsAppDialog() {
  showWhatsAppDialog.value = false
  customerPhone.value = ""
  tempPhoneInput.value = ""
  countryCode.value = "+970"
  customMessageText.value = ""
  includePortalInfo.value = true
}

async function updateCustomerPhone(phoneNumber) {
  const cust = props.customer?.name || props.customer
  if (!cust) return false
  try {
    updatingPhone.value = true
    await call("pos_next.api.customers.update_customer_phone", {
      customer: cust,
      mobile_no: phoneNumber
    })
    if (props.customer) {
      props.customer.mobile_no = phoneNumber
    }
    return true
  } catch (e) {
    showError(e?.message || __('فشل تحديث رقم الهاتف'))
    return false
  } finally {
    updatingPhone.value = false
  }
}

async function sendWhatsAppMessage() {
  let phone = customerPhone.value
  if (!phone) {
    const fullNumber = countryCode.value + tempPhoneInput.value.replace(/^0+/, '')
    phone = fullNumber
    if (!tempPhoneInput.value) {
      showError(__('يرجى إدخال رقم الهاتف'))
      return
    }
    const phoneUpdated = await updateCustomerPhone(fullNumber)
    if (!phoneUpdated) {
      showError(__('لم يتم حفظ الرقم في بيانات العميل، لكن سيتم إرسال الرسالة'))
    }
  }
  phone = phone.replace(/[^\d+]/g, '')
  if (!phone) {
    showError(__('رقم الهاتف غير صالح'))
    return
  }
  if (!phone.startsWith('+')) {
    phone = '+' + phone
  }
  const companyName = props.company || ''
  const remaining = formatCurrency(accountBalance.value)
  const lastPayDate = lastPaymentDate.value ? formatDate(lastPaymentDate.value) : __('غير متوفر')
  const lastPayAmount = formatCurrency(lastPaymentAmount.value)
  const lastPayRef = lastPayment.value?.name || '-'
  let messageText = `مرحباً ${localCustomer.value?.customer_name || ''}\n` +
    `${companyName}\n` +
    `تاريخ آخر دفعة: ${lastPayDate}\n` +
    `مبلغ آخر دفعة: ${lastPayAmount}\n` +
    `رقم الدفعة: ${lastPayRef}\n` +
    `المبلغ المتبقي: ${remaining}\n` +
    `شكراً لتعاملكم معنا`
  if (includePortalInfo.value) {
    const portalLink = portalUrl.value
    const username = localCustomer.value?.customer_name || localCustomer.value?.name || ''
    const customerId = localCustomer.value?.id_no || '-'
    messageText += `\n\nمعلومات بوابة العميل:\n`
    messageText += `رابط الدخول: ${portalLink}\n`
    messageText += `اسم المستخدم: ${username}\n`
    messageText += `رقم العميل: ${customerId}`
  }
  if (customMessageText.value && customMessageText.value.trim()) {
    messageText += `\n\n${customMessageText.value.trim()}`
  }
  const message = encodeURIComponent(messageText)
  window.open(`https://api.whatsapp.com/send?phone=${phone}&text=${message}`, '_blank')
  closeWhatsAppDialog()
}

function printReport() {
const w = window.open('', '_blank', 'width=900,height=700')
if (!w) return
const customerName = localCustomer.value?.customer_name || localCustomer.value?.name || ''
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
    '<td>' + (isInv ? (t.is_return ? __('مرتجع مبيعات') : __('فاتورة مبيعات')) : (t.payment_type === 'Pay' ? __('دفع للعميل') : __('قبض من العميل'))) + '</td>' +
    '<td class="amount">' + amount + '</td>' +
    '<td>' + detail + '</td>' +
    '</tr>' +
    (itemsHtml ? '<tr class="items-row"><td colspan="5">' + itemsHtml + '</td></tr>' : '')
}).join('')

const html = `<!DOCTYPE html>
<html dir=rtl>
<head>
<meta charset=UTF-8>
<title>${__('تقرير العميل')}</title>
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
  <h2>${__('تقرير العميل')}</h2>
  <p class='meta'>${customerName} · ${props.company} · ${__('رصيد الحساب')}: ${formatCurrency(accountBalance.value)} · ${new Date().toLocaleDateString('ar-SA')}</p>
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
<div class='footer'>${__('تقرير عميل')}</div>
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
if (props.customer) loadData()
}
})
</script>
