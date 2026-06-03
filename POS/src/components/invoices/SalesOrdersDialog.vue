<template>
	<!-- Full Page Overlay -->
	<Transition name="fade">
		<div
			v-if="show"
			class="fixed inset-0 bg-black bg-opacity-50 z-[300]"
			@click.self="handleClose"
		>
			<!-- Main Container -->
			<div class="fixed inset-0 flex items-center justify-center p-4">
				<div class="w-full h-full max-w-[95vw] max-h-[95vh] bg-white rounded-lg shadow-2xl overflow-hidden flex flex-col">
					<!-- Header -->
					<div class="flex items-center justify-between px-6 py-5 border-b bg-gradient-to-r from-teal-50 to-cyan-50">
						<div class="flex items-center gap-3">
							<div class="p-2 bg-teal-100 rounded-lg">
								<svg class="w-6 h-6 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
								</svg>
							</div>
							<div>
								<h2 class="text-xl font-bold text-gray-900">{{ __('طلبات المبيعات') }}</h2>
								<p class="text-sm text-gray-600 flex items-center mt-0.5">
									{{ __('عرض وتحميل طلبات المبيعات للفوترة') }}
								</p>
							</div>
						</div>
						<div class="flex items-center gap-2">
							<Button
								@click="loadSalesOrders"
								:loading="loading"
								variant="ghost"
								size="sm"
							>
								<template #prefix>
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
									</svg>
								</template>
								{{ __('تحديث') }}
							</Button>
							<button
								@click="handleClose"
								class="p-2 hover:bg-white/50 rounded-lg transition-colors"
							>
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
								</svg>
							</button>
						</div>
					</div>

					<!-- Summary Cards -->
					<div class="bg-gray-50 border-b px-6 py-4">
						<div class="grid grid-cols-3 gap-4">
							<div class="bg-white rounded-lg p-3 border border-teal-200">
								<div class="text-xs text-gray-600 mb-1">{{ __('إجمالي الطلبات') }}</div>
								<div class="text-xl font-bold text-gray-900">{{ summary.total_orders || 0 }}</div>
							</div>
							<div class="bg-white rounded-lg p-3 border border-orange-200">
								<div class="text-xs text-gray-600 mb-1">{{ __('في انتظار الفوترة') }}</div>
								<div class="text-xl font-bold text-orange-600">{{ summary.awaiting_invoice || 0 }}</div>
							</div>
							<div class="bg-white rounded-lg p-3 border border-green-200">
								<div class="text-xs text-gray-600 mb-1">{{ __('القيمة الإجمالية') }}</div>
								<div class="text-xl font-bold text-green-600">{{ formatCurrency(summary.total_value || 0) }}</div>
							</div>
						</div>
					</div>

					<!-- Tab Content -->
					<div class="flex-1 overflow-y-auto bg-gray-50">
						<!-- Loading State -->
						<div v-if="loading" class="flex flex-col items-center justify-center py-16">
							<div class="animate-spin rounded-full h-12 w-12 border-b-3 border-teal-500 mb-4"></div>
							<p class="text-sm font-medium text-gray-600">{{ __('جاري تحميل طلبات المبيعات...') }}</p>
						</div>

						<!-- Empty State -->
						<div v-else-if="salesOrders.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
							<svg class="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
							</svg>
							<p class="text-gray-600 font-medium">{{ __('لا توجد طلبات مبيعات') }}</p>
							<p class="text-gray-500 text-sm mt-1">{{ __('أنشئ طلبات مبيعات من المكتب الخلفي لتظهر هنا') }}</p>
						</div>

						<!-- Sales Orders Grid -->
						<div v-else class="p-6">
							<div class="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
								<div
									v-for="order in salesOrders"
									:key="order.name"
									class="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-lg transition-all overflow-hidden"
								>
									<!-- Card Header -->
									<div class="bg-gradient-to-r from-teal-50 to-cyan-50 px-5 py-4 border-b border-gray-200">
										<div class="flex items-start justify-between mb-2">
											<div class="flex-1">
												<h3 class="text-base font-bold text-gray-900">{{ order.name }}</h3>
												<div class="flex items-center gap-2 mt-1">
													<span
														:class="[
															'text-xs px-2.5 py-1 rounded-full font-semibold',
															getStatusColor(order.status)
														]"
													>
														{{ getStatusLabel(order.status) }}
													</span>
												</div>
											</div>
											<div class="text-end ms-3">
												<div class="text-xs text-gray-500 mb-1">{{ __('الإجمالي') }}</div>
												<div class="text-lg font-bold text-teal-600">
													{{ formatCurrency(order.grand_total) }}
												</div>
											</div>
										</div>
									</div>

									<!-- Card Body -->
									<div class="px-5 py-4 flex flex-col gap-3">
										<!-- Customer Info -->
										<div class="flex items-start">
											<svg class="w-5 h-5 text-gray-400 me-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
											</svg>
											<div class="flex-1">
												<div class="text-xs text-gray-500">{{ __('العميل') }}</div>
												<div class="text-sm font-semibold text-gray-900">{{ order.customer_name || order.customer }}</div>
											</div>
										</div>

										<!-- Date -->
										<div class="flex items-start">
											<svg class="w-5 h-5 text-gray-400 me-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
											</svg>
											<div class="flex-1">
												<div class="text-xs text-gray-500">{{ __('تاريخ الطلب') }}</div>
												<div class="text-sm font-medium text-gray-900">{{ formatDate(order.transaction_date) }}</div>
											</div>
										</div>

										<!-- Delivery Date if different -->
										<div v-if="order.delivery_date && order.delivery_date !== order.transaction_date" class="flex items-start">
											<svg class="w-5 h-5 text-gray-400 me-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/>
											</svg>
											<div class="flex-1">
												<div class="text-xs text-gray-500">{{ __('تاريخ التسليم') }}</div>
												<div class="text-sm font-medium text-gray-900">{{ formatDate(order.delivery_date) }}</div>
											</div>
										</div>

										<!-- Progress Indicators -->
										<div class="grid grid-cols-2 gap-3 pt-2 border-t border-gray-100">
											<div>
												<div class="text-xs text-gray-500 mb-1">{{ __('تم الفوترة') }}</div>
												<div class="flex items-center gap-2">
													<div class="flex-1 bg-gray-200 rounded-full h-2">
														<div
															class="bg-blue-500 h-2 rounded-full transition-all"
															:style="{ width: `${order.per_billed || 0}%` }"
														></div>
													</div>
													<span class="text-xs font-semibold text-gray-700">{{ order.per_billed || 0 }}%</span>
												</div>
											</div>
											<div>
												<div class="text-xs text-gray-500 mb-1">{{ __('تم التسليم') }}</div>
												<div class="flex items-center gap-2">
													<div class="flex-1 bg-gray-200 rounded-full h-2">
														<div
															class="bg-green-500 h-2 rounded-full transition-all"
															:style="{ width: `${order.per_delivered || 0}%` }"
														></div>
													</div>
													<span class="text-xs font-semibold text-gray-700">{{ order.per_delivered || 0 }}%</span>
												</div>
											</div>
										</div>

										<!-- Items Summary -->
										<div class="mt-2 pt-2 border-t border-gray-100">
											<div class="text-xs text-gray-500 mb-2">{{ __('{0} صنف(أصناف)', [order.items_count || 0]) }}</div>
											<div class="flex items-center justify-between">
												<div class="text-xs text-gray-600">
													{{ __('المتبقي:') }}
													<span class="font-semibold text-orange-600">{{ formatCurrency(order.remaining_amount || 0) }}</span>
												</div>
											</div>
										</div>
									</div>

									<!-- Card Footer with Actions -->
									<div class="px-5 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between gap-2">
										<button
											@click="viewOrderDetails(order)"
											class="px-3 py-2 text-xs font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors flex items-center gap-1"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
											</svg>
											<span>{{ __('عرض') }}</span>
										</button>
										<button
											v-if="canLoadIntoCart(order)"
											@click="loadIntoCart(order)"
											class="px-3 py-2 text-xs font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg transition-colors flex items-center gap-1"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/>
											</svg>
											<span>{{ __('تحميل إلى السلة') }}</span>
										</button>
										<span
											v-else
											class="text-xs text-gray-500 italic"
										>
											{{ __('مفوتر بالكامل') }}
										</span>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</Transition>

	<!-- Order Details Dialog -->
	<Dialog
		v-model="showDetailsDialog"
		:options="{ title: __('تفاصيل طلب المبيعات'), size: 'lg' }"
	>
		<template #body-content>
			<div v-if="selectedOrder" class="p-4">
				<!-- Order Header Info -->
				<div class="bg-gray-50 rounded-lg p-4 mb-4">
					<div class="grid grid-cols-2 gap-4">
						<div>
							<div class="text-xs text-gray-500">{{ __('الطلب') }}</div>
							<div class="font-semibold text-gray-900">{{ selectedOrder.name }}</div>
						</div>
						<div>
							<div class="text-xs text-gray-500 mb-1">{{ __('الحالة') }}</div>
							<span
								:class="[
									'px-2 py-0.5 text-xs font-semibold rounded-full',
									getStatusColor(selectedOrder.status)
								]"
							>
								{{ getStatusLabel(selectedOrder.status) }}
							</span>
						</div>
						<div>
							<div class="text-xs text-gray-500">{{ __('العميل') }}</div>
							<div class="font-semibold text-gray-900">{{ selectedOrder.customer_name || selectedOrder.customer }}</div>
						</div>
						<div>
							<div class="text-xs text-gray-500">{{ __('تاريخ الطلب') }}</div>
							<div class="font-semibold text-gray-900">{{ formatDate(selectedOrder.transaction_date) }}</div>
						</div>
					</div>
				</div>

				<!-- Items Table -->
				<div class="border rounded-lg overflow-hidden">
					<table class="w-full text-sm">
						<thead class="bg-gray-100">
							<tr>
								<th class="px-3 py-2 text-left font-semibold text-gray-700">{{ __('الصنف') }}</th>
								<th class="px-3 py-2 text-center font-semibold text-gray-700">{{ __('الكمية') }}</th>
								<th class="px-3 py-2 text-end font-semibold text-gray-700">{{ __('السعر') }}</th>
								<th class="px-3 py-2 text-end font-semibold text-gray-700">{{ __('المبلغ') }}</th>
							</tr>
						</thead>
						<tbody class="divide-y">
							<tr v-for="item in selectedOrder.items" :key="item.item_code" class="hover:bg-gray-50">
								<td class="px-3 py-2">
									<div class="font-medium text-gray-900">{{ item.item_name }}</div>
									<div class="text-xs text-gray-500">{{ item.item_code }}</div>
								</td>
								<td class="px-3 py-2 text-center">
									{{ item.qty }} {{ item.uom }}
								</td>
								<td class="px-3 py-2 text-end">
									{{ formatCurrency(item.rate) }}
								</td>
								<td class="px-3 py-2 text-end font-semibold">
									{{ formatCurrency(item.amount) }}
								</td>
							</tr>
						</tbody>
						<tfoot class="bg-gray-50 font-semibold">
							<tr>
								<td colspan="3" class="px-3 py-2 text-end">{{ __('الإجمالي') }}</td>
								<td class="px-3 py-2 text-end text-teal-600">
									{{ formatCurrency(selectedOrder.total || selectedOrder.net_total || 0) }}
								</td>
							</tr>
							<tr v-if="selectedOrder.discount_amount">
								<td colspan="3" class="px-3 py-2 text-end">{{ __('الخصم') }}</td>
								<td class="px-3 py-2 text-end text-red-600">
									-{{ formatCurrency(selectedOrder.discount_amount) }}
								</td>
							</tr>
							<tr>
								<td colspan="3" class="px-3 py-2 text-end">{{ __('الإجمالي الكلي') }}</td>
								<td class="px-3 py-2 text-end text-teal-600">
									{{ formatCurrency(selectedOrder.grand_total) }}
								</td>
							</tr>
						</tfoot>
					</table>
				</div>
			</div>
		</template>
		<template #actions>
			<div class="flex justify-between w-full">
				<Button variant="subtle" @click="showDetailsDialog = false">
					{{ __('إغلاق') }}
				</Button>
				<Button
					v-if="selectedOrder && canLoadIntoCart(selectedOrder)"
					variant="solid"
					theme="teal"
					@click="loadIntoCart(selectedOrder); showDetailsDialog = false;"
				>
					{{ __('تحميل إلى السلة') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { useFormatters } from "@/composables/useFormatters"
import { useToast } from "@/composables/useToast"
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"
import { Button, call, Dialog } from "frappe-ui"
import { computed, ref, watch } from "vue"

const { formatDate } = useFormatters()
const { showSuccess, showError } = useToast()

const props = defineProps({
	modelValue: Boolean,
	posProfile: String,
	currency: {
		type: String,
		default: "USD",
	},
})

const emit = defineEmits([
	"update:modelValue",
	"load-order",
])

const show = ref(props.modelValue)
const loading = ref(false)
const salesOrders = ref([])
const summary = ref({
	total_orders: 0,
	total_value: 0,
	awaiting_invoice: 0,
	by_status: [],
})

const showDetailsDialog = ref(false)
const selectedOrder = ref(null)

// Watchers
watch(
	() => props.modelValue,
	(val) => {
		show.value = val
		if (val) {
			loadSalesOrders()
			loadSummary()
		}
	},
)

watch(show, (val) => {
	emit("update:modelValue", val)
})

// Methods
function handleClose() {
	show.value = false
}

async function loadSalesOrders() {
	if (!props.posProfile) return

	loading.value = true
	try {
		const result = await call(
			"pos_next.api.sales_orders.get_sales_orders",
			{
				pos_profile: props.posProfile,
				limit: 50,
			}
		)
		salesOrders.value = result || []
	} catch (error) {
		console.error("Error loading sales orders:", error)
		showError(error.message || __("فشل تحميل طلبات المبيعات"))
	} finally {
		loading.value = false
	}
}

async function loadSummary() {
	if (!props.posProfile) return

	try {
		const result = await call(
			"pos_next.api.sales_orders.get_sales_order_summary",
			{
				pos_profile: props.posProfile,
			}
		)
		summary.value = result || {
			total_orders: 0,
			total_value: 0,
			awaiting_invoice: 0,
			by_status: [],
		}
	} catch (error) {
		console.error("Error loading summary:", error)
	}
}

async function viewOrderDetails(order) {
	loading.value = true
	try {
		const result = await call(
			"pos_next.api.sales_orders.get_sales_order_details",
			{
				name: order.name,
			}
		)
		selectedOrder.value = result
		showDetailsDialog.value = true
	} catch (error) {
		console.error("Error loading order details:", error)
		showError(error.message || __("فشل تحميل تفاصيل الطلب"))
	} finally {
		loading.value = false
	}
}

function canLoadIntoCart(order) {
	// Check if order can still be billed
	if (!order.per_billed) return true
	return order.per_billed < 100
}

function loadIntoCart(order) {
	emit("load-order", order)
	showSuccess(__("تم تحميل طلب المبيعات في السلة"))
	handleClose()
}

function formatCurrency(amount) {
	return formatCurrencyUtil(Number.parseFloat(amount || 0), props.currency)
}

function getStatusLabel(status) {
	const labels = {
		"Draft": "مسودة",
		"To Deliver and Bill": "للتسليم والفوترة",
		"To Bill": "للفوترة",
		"To Deliver": "للتسليم",
		"Completed": "مكتمل",
		"Cancelled": "ملغي",
		"Closed": "مغلق",
	}
	return labels[status] || status
}

function getStatusColor(status) {
	const colors = {
		"Draft": "bg-gray-100 text-gray-800",
		"To Deliver and Bill": "bg-orange-100 text-orange-800",
		"To Bill": "bg-yellow-100 text-yellow-800",
		"To Deliver": "bg-blue-100 text-blue-800",
		"Completed": "bg-green-100 text-green-800",
		"Cancelled": "bg-red-100 text-red-800",
		"Closed": "bg-gray-100 text-gray-600",
	}
	return colors[status] || "bg-gray-100 text-gray-800"
}
</script>

<style scoped>
/* Fade transition for overlay */
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
</style>
