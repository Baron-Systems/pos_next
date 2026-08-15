<template>
	<!-- Icon-Only Sidebar - Hidden on Mobile, Visible on Desktop -->
	<div class="hidden lg:flex w-16 flex-shrink-0 bg-white border-e border-gray-200 flex-col items-center py-4 flex flex-col gap-2">
		<!-- Promotions -->
		<button
			@click="handleMenuClick('promotions')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				activeMenu === 'promotions'
					? 'bg-green-100 text-green-600'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('Promotions')"
		>
			<FeatherIcon name="tag" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('Promotions') }}
			</div>
		</button>

		<!-- Products -->
		<button
			v-if="settingsStore.allowStockLookup"
			@click="handleMenuClick('products')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				activeMenu === 'products'
					? 'bg-purple-100 text-purple-600'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('Products')"
		>
			<FeatherIcon name="package" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('Products') }}
			</div>
		</button>

		<!-- Reports -->
		<button
			@click="handleMenuClick('reports')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				activeMenu === 'reports'
					? 'bg-orange-100 text-orange-600'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('Reports')"
		>
			<FeatherIcon name="bar-chart-2" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('Reports') }}
			</div>
		</button>

		<!-- Invoices -->
		<button
			@click="handleMenuClick('invoices')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				activeMenu === 'invoices'
					? 'bg-indigo-100 text-indigo-600'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('Invoice Management')"
		>
			<FeatherIcon name="file-text" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('Invoice Management') }}
			</div>
		</button>

		<!-- Sales Orders -->
		<button
			@click="handleMenuClick('sales-orders')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				activeMenu === 'sales-orders'
					? 'bg-teal-100 text-teal-600'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('طلبات المبيعات')"
		>
			<FeatherIcon name="clipboard" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('طلبات المبيعات') }}
			</div>
		</button>

		<!-- Shift Notes -->
		<button
			@click="handleMenuClick('shift-notes')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				activeMenu === 'shift-notes'
					? 'bg-amber-100 text-amber-600'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('ملاحظات الوردية')"
		>
			<FeatherIcon name="message-square" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('ملاحظات الوردية') }}
			</div>
		</button>

		<!-- Currency Exchange -->
		<button
			v-if="showCurrencyExchange"
			@click="handleMenuClick('currency-exchange')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				activeMenu === 'currency-exchange'
					? 'bg-yellow-100 text-yellow-600'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('Currency Exchange')"
		>
			<FeatherIcon name="dollar-sign" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('Currency Exchange') }}
			</div>
		</button>

		<!-- Cash to Card Transfer -->
		<button
			v-if="hasMultiplePaymentMethods"
			@click="handleMenuClick('cash-to-card')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				activeMenu === 'cash-to-card'
					? 'bg-emerald-100 text-emerald-600'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('تحويل نقدي إلى بطاقة')"
		>
			<FeatherIcon name="repeat" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('تحويل نقدي إلى بطاقة') }}
			</div>
		</button>

		<!-- Expenses -->
		<button
			v-if="settingsStore.allowShiftExpense"
			@click="handleMenuClick('expenses')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				activeMenu === 'expenses'
					? 'bg-rose-100 text-rose-600'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('مصاريف الوردية')"
		>
			<FeatherIcon name="file-minus" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('مصاريف الوردية') }}
			</div>
		</button>

		<!-- Cart Only -->
		<button
			@click="emit('toggle-cart-only')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				cartOnly
					? 'bg-blue-100 text-blue-600'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('وضع السلة')"
		>
			<FeatherIcon name="columns" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('وضع السلة') }}
			</div>
		</button>

		<!-- Divider -->
		<div class="w-8 border-t border-gray-200 my-2"></div>

		<!-- Supplier -->
		<button
			v-if="settingsStore.allowSupplierPayment"
			@click="handleMenuClick('supplier')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				activeMenu === 'supplier'
					? 'bg-orange-100 text-orange-600'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('المورد')"
		>
			<FeatherIcon name="truck" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('المورد') }}
			</div>
		</button>

		<!-- Settings -->
		<button
			@click="handleMenuClick('settings')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				activeMenu === 'settings'
					? 'bg-gray-100 text-gray-900'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('Settings')"
		>
			<FeatherIcon name="settings" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('Settings') }}
			</div>
		</button>
	</div>
</template>

<script setup>
import { usePOSSettingsStore } from "@/stores/posSettings"
import { FeatherIcon } from "frappe-ui"
import { ref } from "vue"

const settingsStore = usePOSSettingsStore()
const props = defineProps({
	showCurrencyExchange: { type: Boolean, default: false },
	hasMultiplePaymentMethods: { type: Boolean, default: false },
	cartOnly: { type: Boolean, default: false },
})
const emit = defineEmits(["menu-clicked", "toggle-cart-only"])

const activeMenu = ref("")

function handleMenuClick(menuItem) {
	activeMenu.value = menuItem
	emit("menu-clicked", menuItem)
}
</script>
