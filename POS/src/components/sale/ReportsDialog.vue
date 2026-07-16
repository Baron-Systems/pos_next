<template>
	<Dialog
		v-model="show"
		:options="{ title: __('التقارير'), size: 'lg' }"
		@after-leave="$emit('after-leave')"
	>
		<template #body-content>
			<div class="flex flex-col gap-5">
				<!-- Loading State -->
				<div v-if="loading" class="text-center py-10">
					<div class="inline-block animate-spin rounded-full h-10 w-10 border-4 border-orange-200 border-t-orange-500"></div>
					<p class="mt-3 text-sm text-gray-500">{{ __('جاري تحميل التقارير...') }}</p>
				</div>

				<!-- Report Content -->
				<div v-else class="flex flex-col gap-4">
					<!-- Summary Cards -->
					<div class="grid grid-cols-2 gap-3">
						<div class="bg-blue-50 border border-blue-100 rounded-xl p-4">
							<div class="flex items-center gap-2 mb-2">
								<div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
									<svg class="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
									</svg>
								</div>
								<p class="text-xs text-gray-600">{{ __('عدد الفواتير') }}</p>
							</div>
							<p class="text-2xl font-bold text-gray-900">{{ reportData.invoice_count || 0 }}</p>
						</div>

						<div class="bg-green-50 border border-green-100 rounded-xl p-4">
							<div class="flex items-center gap-2 mb-2">
								<div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
									<svg class="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
									</svg>
								</div>
								<p class="text-xs text-gray-600">{{ __('إجمالي المبيعات') }}</p>
							</div>
							<p class="text-2xl font-bold text-gray-900">{{ formatCurrency(reportData.total_sales || 0) }}</p>
						</div>
					</div>

					<!-- Out of Stock Items -->
					<div class="bg-white border border-gray-200 rounded-xl p-4">
						<div class="flex items-center gap-2 mb-3">
							<div class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
								<svg class="h-4 w-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/>
								</svg>
							</div>
							<h4 class="text-base font-semibold text-gray-900">{{ __('أصناف نفذ المخزون') }}</h4>
							<span class="ms-auto text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full font-semibold">
								{{ (reportData.out_of_stock_items || []).length }}
							</span>
						</div>
						<div v-if="reportData.out_of_stock_items && reportData.out_of_stock_items.length > 0" class="max-h-[12rem] overflow-y-auto space-y-1">
							<div
								v-for="item in reportData.out_of_stock_items"
								:key="item.item_code + item.warehouse"
								class="flex items-center justify-between py-1.5 px-2 bg-red-50 rounded-lg"
							>
								<div class="flex-1 min-w-0">
									<p class="text-sm font-medium text-gray-900 truncate">{{ item.item_name }}</p>
									<p class="text-xs text-gray-500">{{ item.warehouse }}</p>
								</div>
								<span class="text-xs font-bold text-red-600 bg-red-100 px-2 py-0.5 rounded ms-2 flex-shrink-0">
									{{ item.actual_qty }}
								</span>
							</div>
						</div>
						<div v-else class="text-center py-4">
							<p class="text-sm text-gray-500">{{ __('لا توجد أصناف نفذ مخزونها') }}</p>
						</div>
					</div>

					<!-- Top 20 Products Across All Shifts -->
					<div v-if="reportData.top_products && reportData.top_products.length > 0" class="bg-white border border-gray-200 rounded-xl p-4">
						<div class="flex items-center gap-2 mb-3">
							<div class="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center">
								<svg class="h-4 w-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
								</svg>
							</div>
							<h4 class="text-base font-semibold text-gray-900">{{ __('أفضل 20 منتج مبيعاً') }}</h4>
							<span class="ms-auto text-xs text-gray-500">{{ __('جميع الورديات') }}</span>
						</div>
						<div class="mb-3">
							<select
								v-model="periodMonths"
								class="w-full h-9 border border-gray-200 rounded-lg bg-white px-3 text-sm cursor-pointer focus:outline-none focus:border-gray-400"
								@change="loadReportData"
							>
								<option
									v-for="opt in periodOptions"
									:key="opt.value"
									:value="opt.value"
								>
									{{ opt.label }}
								</option>
							</select>
						</div>
						<div class="max-h-[20rem] overflow-y-auto space-y-1">
							<div
								v-for="(product, index) in reportData.top_products"
								:key="product.item_code"
								class="flex items-center justify-between py-1.5 px-2 bg-gray-50 rounded-lg"
							>
								<div class="flex items-center gap-2 min-w-0">
									<span class="w-5 h-5 rounded-full bg-orange-100 text-orange-600 text-[10px] font-bold flex items-center justify-center flex-shrink-0">
										{{ index + 1 }}
									</span>
									<div class="min-w-0">
										<p class="text-sm font-medium text-gray-900 truncate">{{ product.item_name }}</p>
										<p class="text-xs text-gray-500">{{ __('الكمية: {0}', [product.qty]) }}</p>
									</div>
								</div>
								<p class="text-sm font-semibold text-gray-900 flex-shrink-0">{{ formatCurrency(product.total) }}</p>
							</div>
						</div>
					</div>

					<!-- No Data Message -->
					<div v-else-if="!reportData.out_of_stock_items || reportData.out_of_stock_items.length === 0" class="text-center py-8">
						<div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
							<svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
							</svg>
						</div>
						<p class="text-sm text-gray-500">{{ __('لا توجد بيانات للعرض') }}</p>
					</div>
				</div>
			</div>
		</template>
		<template #actions>
			<Button variant="subtle" @click="show = false">
				{{ __('إغلاق') }}
			</Button>
		</template>
	</Dialog>
</template>

<script setup>
import { Button, Dialog } from "frappe-ui"
import { computed, ref, watch } from "vue"
import { call } from "@/utils/apiWrapper"
import { useToast } from "@/composables/useToast"

const props = defineProps({
	modelValue: {
		type: Boolean,
		required: true,
	},
	posProfile: {
		type: String,
		default: null,
	},
	currency: {
		type: String,
		default: null,
	},
})

const emit = defineEmits(["update:modelValue", "after-leave"])

const show = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

const { showError } = useToast()

const reportData = ref({
	invoice_count: 0,
	total_sales: 0,
	average_invoice: 0,
	customer_count: 0,
	out_of_stock_items: [],
	top_products: [],
})
const loading = ref(false)

const periodMonths = ref(1)

const periodOptions = [
	{ label: __('1 شهر'), value: 1 },
	{ label: __('3 أشهر'), value: 3 },
	{ label: __('6 أشهر'), value: 6 },
	{ label: __('12 شهر'), value: 12 },
]

watch(
	() => props.modelValue,
	(isOpen) => {
		if (isOpen) {
			loadReportData()
		}
	}
)

watch(
	periodMonths,
	() => {
		if (props.modelValue) {
			loadReportData()
		}
	}
)

async function loadReportData() {
	if (!props.posProfile) {
		reportData.value = {
			invoice_count: 0,
			total_sales: 0,
			average_invoice: 0,
			customer_count: 0,
			out_of_stock_items: [],
			top_products: [],
		}
		return
	}

	loading.value = true
	try {
		const result = await call("pos_next.api.reports.get_shift_report", {
			pos_profile: props.posProfile,
			period_months: periodMonths.value,
		})
		reportData.value = result || {
			invoice_count: 0,
			total_sales: 0,
			average_invoice: 0,
			customer_count: 0,
			out_of_stock_items: [],
			top_products: [],
		}
	} catch (error) {
		showError(__('فشل تحميل التقارير'), error.message)
		reportData.value = {
			invoice_count: 0,
			total_sales: 0,
			average_invoice: 0,
			customer_count: 0,
			out_of_stock_items: [],
			top_products: [],
		}
	} finally {
		loading.value = false
	}
}

function formatCurrency(amount) {
	if (!amount) return '0'
	return new Intl.NumberFormat('ar-SA', {
		style: 'currency',
		currency: props.currency || 'SAR',
		minimumFractionDigits: 2,
	}).format(amount)
}
</script>
