<template>
	<div
		v-if="modelValue"
		class="fixed z-[300] bg-white border border-gray-200 rounded-xl shadow-2xl w-80 p-4"
		style="left: 64px; top: 340px;"
		@click.stop
	>
		<!-- Header -->
		<div class="flex items-center justify-between mb-3">
			<h3 class="text-sm font-bold text-gray-800 flex items-center gap-2">
				<svg class="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
				</svg>
				{{ __('المورد') }}
			</h3>
			<button @click="close" class="text-gray-400 hover:text-gray-600">
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>

		<!-- Supplier Selection Widget -->
		<SupplierSection
			:supplier="supplier"
			@select-supplier="handleSelect"
			@create-supplier="handleCreate"
			@edit-supplier="handleEdit"
			@supplier-payment="handlePayment"
			@remove-supplier="handleRemove"
		/>

		<!-- Collect/Pay Button -->
		<div class="mt-3 pt-3 border-t border-gray-100">
			<button
				type="button"
				@click="handleCollect"
				:disabled="!supplier"
				class="w-full py-2 px-3 rounded-lg text-sm font-semibold transition-colors flex items-center justify-center gap-2"
				:class="supplier ? 'bg-green-500 hover:bg-green-600 text-white' : 'bg-gray-100 text-gray-400 cursor-not-allowed'"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a1 1 0 11-2 0 1 1 0 012 0z" />
				</svg>
				{{ __('اقبض / ادفع للمورد') }}
			</button>
		</div>
	</div>
</template>

<script setup>
import SupplierSection from "@/components/sale/SupplierSection.vue"

const props = defineProps({
	modelValue: Boolean,
	supplier: Object,
})

const emit = defineEmits([
	"update:modelValue",
	"select-supplier",
	"create-supplier",
	"edit-supplier",
	"supplier-payment",
	"remove-supplier",
])

function close() {
	emit("update:modelValue", false)
}

function handleSelect(sup) {
	emit("select-supplier", sup)
	if (!sup) close()
}

function handleCreate(searchValue) {
	emit("create-supplier", searchValue)
}

function handleEdit(sup) {
	emit("edit-supplier", sup)
}

function handlePayment(sup) {
	emit("supplier-payment", sup)
}

function handleRemove() {
	emit("remove-supplier")
}

function handleCollect() {
	if (props.supplier) {
		emit("supplier-payment", props.supplier)
	}
}
</script>
