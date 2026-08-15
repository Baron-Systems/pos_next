<template>
	<Dialog v-model="show" :options="{ title: __('دفع العميل'), size: 'lg' }" @after-leave="() => { console.log('CustomerPaymentDialog after-leave'); $emit('after-leave') }">
		<template #body-content>
			<div class="flex flex-col gap-4">
				<div v-if="loading" class="flex items-center justify-center py-12">
					<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
				</div>
				<template v-else>
					<!-- Summary Cards as Buttons -->
					<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
						<button
							@click="activeView = 'all'"
							class="text-start border rounded-lg p-3 transition-colors"
							:class="activeView === 'all' ? 'bg-blue-100 border-blue-400' : 'bg-blue-50 border-blue-200 hover:bg-blue-100'"
						>
							<p class="text-xs font-medium" :class="activeView === 'all' ? 'text-blue-700' : 'text-blue-600'">{{ __('المبيعات الكلية') }}</p>
							<p class="text-lg font-bold" :class="activeView === 'all' ? 'text-blue-900' : 'text-blue-800'">{{ formatCurrency(summary.total_sales) }}</p>
						</button>
						<button
							@click="activeView = 'payments'"
							class="text-start border rounded-lg p-3 transition-colors"
							:class="activeView === 'payments' ? 'bg-green-100 border-green-400' : 'bg-green-50 border-green-200 hover:bg-green-100'"
						>
							<p class="text-xs font-medium" :class="activeView === 'payments' ? 'text-green-700' : 'text-green-600'">{{ __('الدفعات الكلية') }}</p>
							<p class="text-lg font-bold" :class="activeView === 'payments' ? 'text-green-900' : 'text-green-800'">{{ formatCurrency(summary.total_payments) }}</p>
						</button>
						<button
							@click="activeView = 'outstanding'"
							class="text-start border rounded-lg p-3 transition-colors"
							:class="activeView === 'outstanding' ? 'bg-orange-100 border-orange-400' : 'bg-orange-50 border-orange-200 hover:bg-orange-100'"
						>
							<p class="text-xs font-medium" :class="activeView === 'outstanding' ? 'text-orange-700' : 'text-orange-600'">{{ __('المبلغ المستحق') }}</p>
							<p class="text-lg font-bold" :class="activeView === 'outstanding' ? 'text-orange-900' : 'text-orange-800'">{{ formatCurrency(summary.outstanding_balance) }}</p>
						</button>
						<button
							@click="activeView = 'unpaid'"
							class="text-start border rounded-lg p-3 transition-colors"
							:class="activeView === 'unpaid' ? 'bg-red-100 border-red-400' : 'bg-red-50 border-red-200 hover:bg-red-100'"
						>
							<p class="text-xs font-medium" :class="activeView === 'unpaid' ? 'text-red-700' : 'text-red-600'">{{ __('الفواتير غير المدفوعة') }}</p>
							<p class="text-lg font-bold" :class="activeView === 'unpaid' ? 'text-red-900' : 'text-red-800'">{{ summary.unpaid_invoice_count }}</p>
						</button>
					</div>

					<!-- Row Limit Selector -->
					<div class="flex items-center justify-between">
						<h4 class="text-sm font-semibold text-gray-800">
							{{ viewTitle }}
						</h4>
						<div class="flex items-center gap-2">
							<label class="text-xs text-gray-600">{{ __('عرض') }}:</label>
							<select v-model="rowLimit" class="text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500">
								<option :value="20">20</option>
								<option :value="50">50</option>
								<option :value="100">100</option>
								<option :value="300">300</option>
							</select>
							<span class="text-xs text-gray-600">{{ __('صف') }}</span>
						</div>
					</div>
					<!-- Invoices Table (for all, outstanding, unpaid views) -->
					<div v-if="showInvoicesTable && filteredInvoices.length > 0">
						<div class="overflow-x-auto border border-gray-200 rounded-lg max-h-[300px] overflow-y-auto">
							<table class="min-w-full text-xs">
								<thead class="bg-gray-50 sticky top-0">
									<tr>
										<th class="px-3 py-2 text-start font-medium text-gray-600">{{ __('رقم الفاتورة') }}</th>
										<th class="px-3 py-2 text-start font-medium text-gray-600">{{ __('التاريخ') }}</th>
										<th class="px-3 py-2 text-end font-medium text-gray-600">{{ __('المجموع') }}</th>
										<th class="px-3 py-2 text-end font-medium text-gray-600">{{ __('المتبقي') }}</th>
										<th class="px-3 py-2 text-center font-medium text-gray-600">{{ __('الحالة') }}</th>
									</tr>
								</thead>
								<tbody class="divide-y divide-gray-100">
									<tr v-for="inv in filteredInvoices" :key="inv.name" class="hover:bg-gray-50 cursor-pointer" @click="openInvoiceDetails(inv)">
										<td class="px-3 py-2 font-medium text-gray-900">{{ inv.name }}</td>
										<td class="px-3 py-2 text-gray-600">{{ inv.posting_date }}</td>
										<td class="px-3 py-2 text-end text-gray-700">{{ formatCurrency(inv.grand_total) }}</td>
										<td class="px-3 py-2 text-end font-semibold" :class="inv.outstanding_amount > 0 ? 'text-orange-600' : 'text-green-600'">{{ formatCurrency(inv.outstanding_amount) }}</td>
										<td class="px-3 py-2 text-center">
											<span :class="statusClass(inv.status)" class="px-2 py-0.5 rounded-full text-[10px] font-medium">{{ inv.status }}</span>
										</td>
									</tr>
								</tbody>
							</table>
						</div>
					</div>
					<div v-else-if="showInvoicesTable" class="text-center py-4 text-sm text-gray-500">{{ __('لا توجد فواتير') }}</div>

					<!-- Payments Table (for payments view) -->
					<div v-if="activeView === 'payments' && limitedPayments.length > 0">
						<div class="overflow-x-auto border border-gray-200 rounded-lg max-h-[300px] overflow-y-auto">
							<table class="min-w-full text-xs">
								<thead class="bg-gray-50 sticky top-0">
									<tr>
										<th class="px-3 py-2 text-start font-medium text-gray-600">{{ __('المرجع') }}</th>
										<th class="px-3 py-2 text-start font-medium text-gray-600">{{ __('التاريخ') }}</th>
										<th class="px-3 py-2 text-end font-medium text-gray-600">{{ __('المبلغ') }}</th>
										<th class="px-3 py-2 text-start font-medium text-gray-600">{{ __('طريقة الدفع') }}</th>
									</tr>
								</thead>
								<tbody class="divide-y divide-gray-100">
									<tr v-for="pay in limitedPayments" :key="pay.name" class="hover:bg-gray-50">
										<td class="px-3 py-2 font-medium text-gray-900">{{ pay.name }}</td>
										<td class="px-3 py-2 text-gray-600">{{ pay.posting_date }}</td>
										<td class="px-3 py-2 text-end text-green-600 font-semibold">{{ formatCurrency(pay.paid_amount) }}</td>
										<td class="px-3 py-2 text-gray-600">{{ pay.mode_of_payment }}</td>
									</tr>
								</tbody>
							</table>
						</div>
					</div>
					<div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
						<div class="flex items-center justify-between mb-3">
							<div class="flex items-center gap-2">
								<h4 class="text-sm font-semibold text-gray-800">{{ __('إرسال تذكير') }}</h4>
								<Button @click="openWhatsAppDialog" variant="solid" size="sm" class="!bg-white !hover:bg-gray-100 border-none p-1.5" :title="__('إرسال تذكير عبر واتساب')">
									<img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp" class="w-6 h-6" />
								</Button>
							</div>
							<div class="text-end">
								<p class="text-xs text-gray-600">{{ __('رصيد الحساب') }}</p>
								<p class="text-lg font-bold" :class="accountBalance > 0 ? 'text-red-600' : accountBalance < 0 ? 'text-green-600' : 'text-gray-600'">
									{{ formatCurrency(accountBalance) }}
								</p>
								<p v-if="accountBalance < 0" class="text-xs text-green-600">{{ __('رصيد دائن (فائض)') }}</p>
								<p v-else-if="accountBalance > 0" class="text-xs text-red-600">{{ __('مستحق على العميل') }}</p>
								<p v-else class="text-xs text-gray-500">{{ __('الحساب متوازن') }}</p>
							</div>
						</div>
						<div class="flex items-end gap-3">
							<div class="flex-1">
								<label class="block text-xs font-medium text-gray-600 mb-1">{{ __('المبلغ') }}</label>
								<input v-model.number="paymentAmount" type="number" :placeholder="__('أدخل المبلغ')" step="0.01"
								class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								@keyup.enter="executePayment" />
							</div>
							<Button @click="executePayment" :loading="paying" :disabled="!paymentAmount || paymentAmount === 0" :theme="paymentAmount < 0 ? 'red' : 'green'" variant="solid">
								{{ paymentAmount < 0 ? __('الدفع للعميل') : __('القبض من العميل') }}
							</Button>
						</div>
						<p v-if="paymentAmount > 0 && paymentAmount > summary.outstanding_balance" class="text-xs text-red-500 mt-2">
							{{ __('المبلغ يتجاوز الرصيد المستحق') }}
						</p>
					</div>
				</template>
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
						<p class="text-sm text-gray-600">{{ __('تاريخ آخر دفعة:') }} {{ lastPaymentDate || __('غير متوفر') }}</p>
						<p class="text-sm text-gray-600">{{ __('مبلغ آخر دفعة:') }} {{ formatCurrency(lastPaymentAmount) }}</p>
						<p class="text-sm text-gray-600">{{ __('رقم الدفعة:') }} {{ lastPayment?.name || '-' }}</p>
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
					<p class="text-blue-800"><span class="font-semibold">{{ __('اسم المستخدم:') }}</span> {{ props.customer?.customer_name || props.customer?.name }}</p>
					<p class="text-blue-800"><span class="font-semibold">{{ __('رقم العميل:') }}</span> {{ props.customer?.id_no || '-' }}</p>
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

	<!-- Invoice Details Dialog -->
	<Dialog v-model="showInvoiceDetails" :options="{ title: selectedInvoice?.name || __('تفاصيل الفاتورة'), size: 'lg' }">
		<template #body-content>
			<div v-if="selectedInvoice" class="flex flex-col gap-4">
				<div class="grid grid-cols-2 gap-4">
					<div>
						<p class="text-xs text-gray-600">{{ __('العميل') }}</p>
						<p class="text-sm font-medium">{{ selectedInvoice.customer_name }}</p>
					</div>
					<div>
						<p class="text-xs text-gray-600">{{ __('التاريخ') }}</p>
						<p class="text-sm font-medium">{{ selectedInvoice.posting_date }}</p>
					</div>
					<div>
						<p class="text-xs text-gray-600">{{ __('الإجمالي الكلي') }}</p>
						<p class="text-sm font-bold text-blue-600">{{ formatCurrency(selectedInvoice.grand_total) }}</p>
					</div>
					<div>
						<p class="text-xs text-gray-600">{{ __('المستحق') }}</p>
						<p class="text-sm font-bold" :class="selectedInvoice.outstanding_amount > 0 ? 'text-orange-600' : 'text-green-600'">{{ formatCurrency(selectedInvoice.outstanding_amount) }}</p>
					</div>
				</div>
				<div v-if="invoiceItems.length > 0">
					<h5 class="text-sm font-semibold text-gray-800 mb-2">{{ __('الأصناف') }}</h5>
					<div class="overflow-x-auto border border-gray-200 rounded-lg">
						<table class="min-w-full text-xs">
							<thead class="bg-gray-50">
								<tr>
									<th class="px-3 py-2 text-start font-medium text-gray-600">{{ __('الصنف') }}</th>
									<th class="px-3 py-2 text-end font-medium text-gray-600">{{ __('الكمية') }}</th>
									<th class="px-3 py-2 text-end font-medium text-gray-600">{{ __('السعر') }}</th>
									<th class="px-3 py-2 text-end font-medium text-gray-600">{{ __('المبلغ') }}</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-gray-100">
								<tr v-for="item in invoiceItems" :key="item.name">
									<td class="px-3 py-2 text-gray-900">{{ item.item_name || item.item_code }}</td>
									<td class="px-3 py-2 text-end text-gray-700">{{ item.qty }}</td>
									<td class="px-3 py-2 text-end text-gray-700">{{ formatCurrency(item.rate) }}</td>
									<td class="px-3 py-2 text-end font-semibold text-gray-900">{{ formatCurrency(item.amount) }}</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>
			</div>
		</template>
		<template #actions>
			<Button variant="solid" @click="showInvoiceDetails = false">{{ __('إغلاق') }}</Button>
		</template>
	</Dialog>
</template>

<script setup>
import { call } from "@/utils/apiWrapper"
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"
import { useToast } from "@/composables/useToast"
import { Button, Dialog } from "frappe-ui"
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

const show = computed({ get: () => props.modelValue, set: (val) => emit("update:modelValue", val) })
const loading = ref(false)
const paying = ref(false)
const paymentAmount = ref(null)
const activeView = ref('outstanding') // Default view: outstanding
const rowLimit = ref(20) // Default: 20 rows
const summary = ref({ total_sales: 0, total_payments: 0, outstanding_balance: 0, unpaid_invoice_count: 0, currency: "" })
const allInvoices = ref([]) // All customer invoices
const outstandingInvoices = ref([])
const recentPayments = ref([])
const showInvoiceDetails = ref(false)
const selectedInvoice = ref(null)
const invoiceItems = ref([])
const showWhatsAppDialog = ref(false)
const customerPhone = ref("")
const tempPhoneInput = ref("")
const countryCode = ref("+970")
const customMessageText = ref("")
const includePortalInfo = ref(true)
const updatingPhone = ref(false)

// Computed
const showInvoicesTable = computed(() => ['all', 'outstanding', 'unpaid'].includes(activeView.value))

const viewTitle = computed(() => {
	const titles = {
		'all': __('جميع الفواتير'),
		'payments': __('الدفعات الأخيرة'),
		'outstanding': __('الفواتير المستحقة'),
		'unpaid': __('الفواتير غير المدفوعة')
	}
	return titles[activeView.value] || __('Invoices')
})

const filteredInvoices = computed(() => {
	let invoices = []
	if (activeView.value === 'all') {
		// Show all invoices
		invoices = allInvoices.value
	} else if (activeView.value === 'outstanding') {
		// Show all outstanding invoices (any remaining amount)
		invoices = allInvoices.value.filter(inv => inv.outstanding_amount > 0)
	} else if (activeView.value === 'unpaid') {
		// Show only completely unpaid (status = Unpaid)
		invoices = allInvoices.value.filter(inv => inv.status === 'Unpaid' && inv.outstanding_amount > 0)
	}
	// Sort by date ascending (oldest first) then reverse to show newest at top of table
	return invoices
		.sort((a, b) => new Date(a.posting_date) - new Date(b.posting_date))
		.slice(0, rowLimit.value)
		.reverse()
})

const limitedPayments = computed(() => {
	return recentPayments.value
		.sort((a, b) => new Date(a.posting_date) - new Date(b.posting_date))
		.slice(0, rowLimit.value)
		.reverse()
})

// Account Balance = Outstanding Balance from backend (matches General Ledger)
const accountBalance = computed(() => {
	return parseFloat(summary.value.outstanding_balance || 0)
})

function formatCurrency(value) { return formatCurrencyUtil(value, summary.value.currency || "USD") }
function statusClass(status) {
	const m = { "Overdue": "bg-red-100 text-red-700", "Unpaid": "bg-orange-100 text-orange-700", "Paid": "bg-green-100 text-green-700", "Partly Paid": "bg-yellow-100 text-yellow-700" }
	return m[status] || "bg-gray-100 text-gray-600"
}

async function loadData() {
	const cust = props.customer?.name || props.customer
	if (!cust || !props.company) return
	loading.value = true
	try {
		// Load all data including all invoices (paid and unpaid)
		const [sum, allInvs, outsInvs, pays] = await Promise.all([
			call("pos_next.api.customer_payment.get_customer_financial_summary", { customer: cust, company: props.company }),
			call("pos_next.api.customer_payment.get_all_invoices", { customer: cust, company: props.company, limit: 300 }),
			call("pos_next.api.customer_payment.get_outstanding_invoices", { customer: cust, company: props.company, limit: 300 }),
			call("pos_next.api.customer_payment.get_recent_payments", { customer: cust, company: props.company, limit: 300 }),
		])
		summary.value = sum
		allInvoices.value = allInvs || []
		outstandingInvoices.value = outsInvs || []
		recentPayments.value = pays || []
	} catch (e) { showError(e?.message || e) }
	finally { loading.value = false }
}

async function openInvoiceDetails(invoice) {
	selectedInvoice.value = invoice
	showInvoiceDetails.value = true
	// Load invoice items
	try {
		const items = await call("pos_next.api.customer_payment.get_invoice_items", { invoice_name: invoice.name })
		invoiceItems.value = items || []
	} catch (e) {
		invoiceItems.value = []
	}
}

async function executePayment() {
	const cust = props.customer?.name || props.customer
	if (!cust || !props.company || !paymentAmount.value || paymentAmount.value === 0) return
	paying.value = true
	try {
		const result = await call("pos_next.api.customer_payment.create_customer_payment", {
			customer: cust,
			company: props.company,
			amount: Math.abs(paymentAmount.value),
			mode_of_payment: props.modeOfPayment,
			payment_type: paymentAmount.value < 0 ? "Pay" : "Receive",
			pos_opening_shift: props.openingShift || undefined,
		})
		showSuccess(__("Payment {0} created successfully", [result.payment_entry]))
		paymentAmount.value = null
		await loadData()
		emit("payment-created", result)
	} catch (e) { showError(e?.message || e) }
	finally { paying.value = false }
}

const lastPayment = computed(() => {
	if (recentPayments.value.length === 0) return null
	// Sort by date descending (newest first), then by name/number for same dates
	const sorted = [...recentPayments.value].sort((a, b) => {
		const dateDiff = new Date(b.posting_date) - new Date(a.posting_date)
		if (dateDiff !== 0) return dateDiff
		// If same date, sort by name descending (higher number = more recent)
		return b.name.localeCompare(a.name)
	})
	return sorted[0]
})

const lastPaymentDate = computed(() => {
	return lastPayment.value ? lastPayment.value.posting_date : null
})

const lastPaymentAmount = computed(() => {
	return lastPayment.value ? lastPayment.value.paid_amount : 0
})

async function openWhatsAppDialog() {
	const phone = props.customer?.mobile_no || props.customer?.phone || ""
	customerPhone.value = phone
	if (!phone) {
		tempPhoneInput.value = ""
	}
	// Reload data to get most recent payment
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
		// Update local customer data
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

const portalUrl = computed(() => {
	// Get current domain from window location
	const domain = window.location.origin
	return `${domain}/portal`
})

async function sendWhatsAppMessage() {
	let phone = customerPhone.value
	let phoneUpdated = false
	
	if (!phone) {
		// Combine country code with phone number
		const fullNumber = countryCode.value + tempPhoneInput.value.replace(/^0+/, '')
		phone = fullNumber
		if (!tempPhoneInput.value) {
			showError(__('يرجى إدخال رقم الهاتف'))
			return
		}
		
		// Update customer phone in database
		phoneUpdated = await updateCustomerPhone(fullNumber)
		if (!phoneUpdated) {
			// Continue anyway but warn user
			showError(__('لم يتم حفظ الرقم في بيانات العميل، لكن سيتم إرسال الرسالة'))
		}
	}
	// Remove any non-digit characters except + for international
	phone = phone.replace(/[^\d+]/g, '')
	if (!phone) {
		showError(__('رقم الهاتف غير صالح'))
		return
	}
	// Ensure phone starts with +
	if (!phone.startsWith('+')) {
		phone = '+' + phone
	}
	const companyName = props.company || ''
	const lastPayDate = lastPaymentDate.value ? lastPaymentDate.value : __('غير متوفر')
	const lastPayAmount = formatCurrency(lastPaymentAmount.value)
	const lastPayRef = lastPayment.value?.name || '-'
	const remaining = formatCurrency(accountBalance.value)
	let messageText = `مرحباً ${props.customer?.customer_name || ''}\n` +
		`${companyName}\n` +
		`تاريخ آخر دفعة: ${lastPayDate}\n` +
		`مبلغ آخر دفعة: ${lastPayAmount}\n` +
		`رقم الدفعة: ${lastPayRef}\n` +
		`المبلغ المتبقي: ${remaining}\n` +
		`شكراً لتعاملكم معنا`
	
	// Add portal info if checked
	if (includePortalInfo.value) {
		const portalLink = portalUrl.value
		const username = props.customer?.customer_name || props.customer?.name || ''
		const customerId = props.customer?.id_no || '-'
		messageText += `\n\nمعلومات بوابة العميل:\n`
		messageText += `رابط الدخول: ${portalLink}\n`
		messageText += `اسم المستخدم: ${username}\n`
		messageText += `رقم العميل: ${customerId}`
	}
	
	// Add custom text if provided
	if (customMessageText.value && customMessageText.value.trim()) {
		messageText += `\n\n${customMessageText.value.trim()}`
	}
	
	const message = encodeURIComponent(messageText)
	// Use api.whatsapp.com for better mobile app integration
	const whatsappUrl = `https://api.whatsapp.com/send?phone=${phone}&text=${message}`
	window.open(whatsappUrl, '_blank')
	closeWhatsAppDialog()
}

watch(show, (val) => { if (val) { paymentAmount.value = null; loadData() } })
</script>