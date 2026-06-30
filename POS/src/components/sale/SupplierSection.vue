<template>
	<div class="px-2.5 py-2 border-b border-gray-200 bg-gray-50">
		<!-- Inline Supplier Search/Selection -->
		<div ref="supplierSearchContainer" class="relative">
			<div v-if="supplier">
				<!-- Supplier Card with Action Buttons -->
				<div class="flex items-stretch gap-2">
					<!-- Supplier Card -->
					<div class="flex-1 flex items-center gap-1.5 bg-white border border-gray-200 rounded-xl p-1.5 shadow-sm min-w-0">
						<!-- Supplier Avatar & Info -->
						<div class="flex items-center gap-2 min-w-0 flex-1 px-1.5 py-1">
							<div class="w-8 h-8 bg-gradient-to-br from-orange-500 to-orange-600 rounded-full flex items-center justify-center flex-shrink-0">
								<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
								</svg>
							</div>
							<div class="min-w-0 flex-1">
								<p class="text-xs font-semibold text-gray-900 truncate leading-tight">
									{{ supplier.supplier_name || supplier.name }}
								</p>
								<p v-if="supplier.mobile_no" class="text-[10px] text-gray-500 truncate leading-tight">
									{{ supplier.mobile_no }}
								</p>
							</div>
						</div>

						<!-- Action Buttons -->
						<div class="flex items-center gap-0.5 flex-shrink-0" @click.stop>
							<button
								type="button"
								@click.stop="$emit('edit-supplier', supplier)"
								class="w-7 h-7 flex items-center justify-center text-blue-500 hover:bg-blue-50 active:bg-blue-100 rounded-lg transition-colors touch-manipulation"
								:title="__('Edit supplier details')"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
								</svg>
							</button>
							<button
								type="button"
								@click.stop="$emit('create-supplier', '')"
								class="w-7 h-7 flex items-center justify-center text-green-600 hover:bg-green-50 active:bg-green-100 rounded-lg transition-colors touch-manipulation"
								:title="__('Create new supplier')"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
								</svg>
							</button>
							<button
								type="button"
								@click.stop="$emit('supplier-payment', supplier)"
								class="w-7 h-7 flex items-center justify-center text-emerald-600 hover:bg-emerald-50 active:bg-emerald-100 rounded-lg transition-colors touch-manipulation"
								:title="__('Supplier payment')"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
								</svg>
							</button>
							<button
								type="button"
								@click.stop="removeSupplier"
								class="w-7 h-7 flex items-center justify-center text-red-500 hover:bg-red-50 active:bg-red-100 rounded-lg transition-colors touch-manipulation"
								:title="__('Remove supplier')"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						</div>
					</div>
				</div>
			</div>
			<div v-else>
				<div class="flex gap-1.5">
					<!-- Search Input -->
					<div class="relative flex-1">
						<!-- Search Icon Prefix -->
						<div class="absolute inset-y-0 start-0 ps-3 flex items-center pointer-events-none">
							<svg v-if="suppliersLoaded" class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
							<div v-else class="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-blue-500"></div>
						</div>

						<!-- Native Input for Instant Search -->
						<input
							id="cart-supplier-search"
							name="cart-supplier-search"
							:value="supplierSearch"
							@input="handleSearchInput"
							@focus="handleSearchFocus"
							@blur="handleSearchBlur"
							type="text"
							:placeholder="__('Search or add supplier...')"
							class="w-full h-10 ps-9 pe-3 text-xs border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent shadow-sm transition-shadow"
							@keydown="handleKeydown"
							autocomplete="off"
							:aria-label="__('Search supplier in cart')"
						/>
					</div>

					<!-- Quick Create Supplier Button -->
					<button
						type="button"
						@click="createNewSupplier"
						class="flex items-center justify-center w-10 h-10 bg-green-500 hover:bg-green-600 active:bg-green-700 rounded-xl text-white transition-colors shadow-sm hover:shadow touch-manipulation flex-shrink-0"
						:title="__('Create new supplier')"
						:aria-label="__('Create new supplier')"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
							<path stroke-linecap="round" stroke-linejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
						</svg>
					</button>
				</div>
			</div>

			<!-- Supplier List (always visible when no supplier selected) -->
			<div
				v-if="!supplier"
				class="relative w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-sm max-h-[420px] overflow-hidden"
			>
				<!-- Supplier Results -->
				<div v-if="supplierResults.length > 0" class="max-h-[380px] overflow-y-auto overscroll-contain">
					<div class="px-2 py-1 bg-gray-50 border-b border-gray-200">
						<span class="text-[10px] font-medium text-gray-500 uppercase tracking-wide">{{ __('Suppliers') }} ({{ supplierResults.length }})</span>
					</div>
					<button
						type="button"
						v-for="(sup, index) in supplierResults"
						:key="sup.name"
						@mousedown.prevent="selectSupplier(sup)"
						:class="[
							'w-full text-start px-3 py-2 flex items-center gap-2 border-b border-gray-100 last:border-0 touch-manipulation select-none cursor-pointer active:bg-orange-200',
							index === selectedIndex ? 'bg-orange-100' : 'hover:bg-orange-50 active:bg-orange-100',
						]"
					>
						<div class="w-7 h-7 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0 pointer-events-none">
							<span class="text-[11px] font-bold text-orange-600">{{ getInitials(sup.supplier_name || sup.name) }}</span>
						</div>
						<div class="flex-1 min-w-0 pointer-events-none">
							<p class="text-xs font-semibold text-gray-900 truncate">{{ sup.supplier_name || sup.name }}</p>
							<p v-if="sup.mobile_no" class="text-[10px] text-gray-600">{{ sup.mobile_no }}</p>
						</div>
					</button>
				</div>

				<!-- No Results -->
				<div v-else-if="supplierSearch.trim().length >= 1">
					<div class="px-3 py-3 text-center text-xs font-medium text-gray-700 border-b border-gray-100">
						{{ __('No results for "{0}"', [supplierSearch]) }}
					</div>
				</div>

				<!-- Empty state -->
				<div v-else class="px-3 py-6 text-center text-xs text-gray-400">
					{{ __('Type to search suppliers...') }}
				</div>

				<!-- Create New Supplier Option -->
				<button
					type="button"
					v-if="supplierSearch.trim().length >= 1"
					@mousedown.prevent="createNewSupplier"
					class="w-full text-start px-3 py-2 hover:bg-green-50 active:bg-green-100 flex items-center gap-2 border-t border-gray-200 touch-manipulation select-none cursor-pointer"
				>
					<div class="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 pointer-events-none">
						<svg class="w-3.5 h-3.5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>
					</div>
					<div class="flex-1 pointer-events-none">
						<p class="text-xs font-medium text-green-700">{{ __('Create New Supplier') }}</p>
						<p class="text-[10px] text-green-600">"{{ supplierSearch }}"</p>
					</div>
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { createResource } from "frappe-ui";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
	supplier: Object,
});

const emit = defineEmits([
	"select-supplier",
	"create-supplier",
	"edit-supplier",
	"supplier-payment",
	"remove-supplier",
]);

// Local state
const supplierSearch = ref("");
const supplierSearchContainer = ref(null);
const supplierSearchFocused = ref(false);
const selectedIndex = ref(-1);
const allSuppliers = ref([]);
const suppliersLoaded = ref(false);

// Load suppliers from server
const suppliersResource = createResource({
	url: "frappe.client.get_list",
	makeParams() {
		return {
			doctype: "Supplier",
			fields: ["name", "supplier_name", "mobile_no"],
			limit_page_length: 2000,
			order_by: "supplier_name asc",
		};
	},
	auto: true,
	onSuccess(data) {
		allSuppliers.value = data || [];
		suppliersLoaded.value = true;
	},
	onError() {
		allSuppliers.value = [];
		suppliersLoaded.value = true;
	},
});

// Computed: filtered results
const supplierResults = computed(() => {
	const searchValue = supplierSearch.value.trim().toLowerCase();
	if (searchValue.length === 0) {
		return allSuppliers.value;
	}
	return allSuppliers.value.filter((sup) => {
		const displayName = (sup.supplier_name || sup.name || "").toLowerCase();
		const mobile = (sup.mobile_no || "").toLowerCase();
		const id = (sup.name || "").toLowerCase();
		return displayName.includes(searchValue) || mobile.includes(searchValue) || id.includes(searchValue);
	});
});

watch(supplierResults, () => {
	selectedIndex.value = -1;
});

// Functions
function handleSearchInput(event) {
	supplierSearch.value = event.target.value;
}

async function loadSuppliers() {
	await suppliersResource.fetch();
}

function handleSearchFocus() {
	supplierSearchFocused.value = true;
	if (allSuppliers.value.length === 0 && !suppliersResource.loading) {
		loadSuppliers();
	}
}

function handleSearchBlur() {
	setTimeout(() => {
		supplierSearchFocused.value = false;
	}, 100);
}

function handleKeydown(event) {
	if (supplierResults.value.length === 0) return;
	if (event.key === "ArrowDown") {
		event.preventDefault();
		selectedIndex.value = Math.min(selectedIndex.value + 1, supplierResults.value.length - 1);
	} else if (event.key === "ArrowUp") {
		event.preventDefault();
		selectedIndex.value = Math.max(selectedIndex.value - 1, -1);
	} else if (event.key === "Enter") {
		event.preventDefault();
		if (selectedIndex.value >= 0 && selectedIndex.value < supplierResults.value.length) {
			selectSupplier(supplierResults.value[selectedIndex.value]);
		} else if (supplierResults.value.length === 1) {
			selectSupplier(supplierResults.value[0]);
		}
	} else if (event.key === "Escape") {
		supplierSearch.value = "";
	}
}

function selectSupplier(sup) {
	emit("select-supplier", sup);
	supplierSearch.value = "";
	selectedIndex.value = -1;
	supplierSearchFocused.value = false;
}

function removeSupplier() {
	emit("select-supplier", null);
}

function createNewSupplier() {
	const searchValue = supplierSearch.value;
	supplierSearch.value = "";
	supplierSearchFocused.value = false;
	emit("create-supplier", searchValue);
}

function getInitials(name) {
	if (!name) return "?";
	const parts = name.split(" ");
	if (parts.length >= 2) {
		return (parts[0][0] + parts[1][0]).toUpperCase();
	}
	return name.substring(0, 2).toUpperCase();
}

// Click outside to close dropdown (disabled - list is now inline always visible)
function handleOutsideClick(event) {
	// No-op: supplier list is always visible inline now
}

onMounted(() => {
	if (typeof document === "undefined") return;
	// document.addEventListener("mousedown", handleOutsideClick);
});

onBeforeUnmount(() => {
	if (typeof document === "undefined") return;
	document.removeEventListener("mousedown", handleOutsideClick);
});
</script>
