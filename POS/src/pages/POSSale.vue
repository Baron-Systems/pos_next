<template>
	<div
		class="flex flex-col bg-gray-50 overflow-x-hidden"
		style="height: 100vh; max-height: 100vh"
	>
		<!-- Loading State -->
		<LoadingSpinner v-if="uiStore.isLoading" />

		<!-- Main App -->
		<template v-else>
			<!-- Header -->
			<POSHeader
				:current-time="shiftStore.currentTime"
				:shift-duration="shiftStore.shiftDuration"
				:has-open-shift="shiftStore.hasOpenShift"
				:profile-name="shiftStore.profileName"
				:user-name="userName"
				:user-image="userImage"
				:is-offline="offlineStore.isOffline"
				:is-syncing="offlineStore.isSyncing"
				:pending-invoices-count="offlineStore.pendingInvoicesCount"
				:is-any-dialog-open="uiStore.isAnyDialogOpen"
				:cache-syncing="itemStore.cacheSyncing"
				:cache-stats="itemStore.cacheStats"
				:stock-sync-active="isStockSyncActive"
				:is-refreshing="stockStore.refreshing"
				:show-success-dialog="showSuccessDialogEnabled"
				:price-lists="priceListStore.priceListOptions"
				:selected-price-list="priceListStore.activePriceList"
				:has-multiple-price-lists="priceListStore.hasMultiplePriceLists"
				@sync-click="handleSyncClick"
				@printer-click="uiStore.showHistoryDialog = true"
				@refresh-click="handleRefresh"
				@clear-cache="handleClearCache"
				@logout="uiStore.showLogoutDialog = true"
				@toggle-success-dialog="showSuccessDialogEnabled = !showSuccessDialogEnabled"
				@price-list-change="handlePriceListChange"
			>
				<template #menu-items>
					<button
						v-if="shiftStore.hasOpenShift"
						@click="uiStore.showOpenShiftDialog = true"
						class="w-full text-start px-4 py-2.5 text-sm text-gray-700 hover:bg-blue-50 flex items-center gap-3 transition-colors"
					>
						<svg
							class="w-5 h-5 text-blue-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						<span>{{ __("View Shift") }}</span>
					</button>
					<button
						@click="uiStore.showDraftDialog = true"
						class="w-full text-start px-4 py-2.5 text-sm text-gray-700 hover:bg-purple-50 flex items-center gap-3 transition-colors relative"
					>
						<svg
							class="w-5 h-5 text-purple-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							/>
						</svg>
						<span>{{ __("Draft Invoices") }}</span>
						<span
							v-if="draftsStore.draftsCount > 0"
							class="ms-auto text-xs bg-purple-600 text-white px-1.5 py-0.5 rounded-full"
						>
							{{ draftsStore.draftsCount }}
						</span>
					</button>
					<button
						@click="uiStore.showHistoryDialog = true"
						class="w-full text-start px-4 py-2.5 text-sm text-gray-700 hover:bg-indigo-50 flex items-center gap-3 transition-colors"
					>
						<svg
							class="w-5 h-5 text-indigo-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							/>
						</svg>
						<span>{{ __("Invoice History") }}</span>
					</button>
					<button
						v-if="offlineStore.pendingInvoicesCount > 0"
						@click="
							uiStore.showOfflineInvoicesDialog = true;
							offlineStore.loadPendingInvoices();
						"
						class="w-full text-start px-4 py-2.5 text-sm text-gray-700 hover:bg-orange-50 flex items-center gap-3 transition-colors relative"
					>
						<svg
							class="w-5 h-5 text-orange-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						<span>{{ __("Offline Invoices") }}</span>
						<span
							class="ms-auto text-xs bg-orange-600 text-white px-1.5 py-0.5 rounded-full"
						>
							{{ offlineStore.pendingInvoicesCount }}
						</span>
					</button>
					<button
						@click="uiStore.showReturnDialog = true"
						class="w-full text-start px-4 py-2.5 text-sm text-gray-700 hover:bg-red-50 flex items-center gap-3 transition-colors"
					>
						<svg
							class="w-5 h-5 text-red-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
							/>
						</svg>
						<span>{{ __("Return Invoice") }}</span>
					</button>
				</template>
				<template #additional-actions>
					<button
						@click="handleCloseShift()"
						class="w-full text-start px-4 py-2.5 text-sm text-gray-700 hover:bg-orange-50 flex items-center gap-3 transition-colors"
					>
						<svg
							class="w-5 h-5 text-orange-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						<span>{{ __("Close Shift") }}</span>
					</button>
				</template>
			</POSHeader>

			<!-- Main Content: Responsive Layout -->
			<div
				v-if="shiftStore.hasOpenShift"
				class="flex-1 flex overflow-hidden relative"
				style="max-height: calc(100vh - 60px - var(--header-height, 60px))"
			>
				<!-- Icon-Only Management Slider - Always Visible -->
				<ManagementSlider
				:show-currency-exchange="posSettingsStore.enableCurrencyExchange && posSettingsStore.hasCurrencySetup"
				@menu-clicked="handleManagementMenuClick"
			/>

				<!-- Main Content Container -->
				<div
					ref="containerRef"
					class="flex-1 flex flex-col lg:flex-row overflow-hidden relative"
				>
					<!-- Mobile Tab Navigation -->
					<div
						class="lg:hidden bg-white border-b border-gray-200 flex shadow-sm sticky top-0 z-[100]"
					>
						<button
							@click="handleTabSwitch('items')"
							:class="[
								'flex-1 px-3 py-3 text-sm font-semibold transition-[color,background-color,border-color] duration-100 relative touch-manipulation',
								uiStore.mobileActiveTab === 'items'
									? 'text-blue-600 border-b-3 border-blue-600 bg-blue-50'
									: 'text-gray-600 hover:text-gray-800 hover:bg-gray-50 active:bg-gray-100',
							]"
							:aria-label="__('View items')"
							:aria-selected="uiStore.mobileActiveTab === 'items'"
							role="tab"
						>
							<div class="flex items-center justify-center gap-1.5">
								<svg
									class="w-5 h-5"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
									/>
								</svg>
								<span>{{ __("Items") }}</span>
							</div>
						</button>
						<button
							@click="handleTabSwitch('cart')"
							:class="[
								'flex-1 px-3 py-3 text-sm font-semibold transition-[color,background-color,border-color] duration-100 relative touch-manipulation',
								uiStore.mobileActiveTab === 'cart'
									? 'text-blue-600 border-b-3 border-blue-600 bg-blue-50'
									: 'text-gray-600 hover:text-gray-800 hover:bg-gray-50 active:bg-gray-100',
							]"
							:aria-label="__('View cart')"
							:aria-selected="uiStore.mobileActiveTab === 'cart'"
							role="tab"
						>
							<div class="flex items-center justify-center gap-1.5">
								<svg
									class="w-5 h-5"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
									/>
								</svg>
								<span>{{ __("Cart") }}</span>
								<span
									v-if="cartStore.itemCount > 0"
									class="bg-blue-600 text-white text-[10px] font-bold rounded-full min-w-[20px] h-5 px-1.5 flex items-center justify-center shadow-sm"
								>
									{{ cartStore.itemCount }}
								</span>
							</div>
						</button>
					</div>

					<!-- Left: Items Selector (Desktop) / Tab Content (Mobile) -->
					<keep-alive>
						<div
							v-if="uiStore.isDesktop || uiStore.mobileActiveTab === 'items'"
							:style="{
								width: uiStore.isDesktop ? uiStore.leftPanelWidth + 'px' : '100%',
							}"
							:class="[
								'flex flex-col bg-white overflow-hidden',
								uiStore.isDesktop ? 'flex-shrink-0' : 'flex-1',
							]"
							style="contain: layout style paint"
						>
							<ItemsSelector
								ref="itemsSelectorRef"
								:pos-profile="shiftStore.profileName"
								:cart-items="cartStore.invoiceItems"
								:currency="shiftStore.profileCurrency"
								@item-selected="handleItemSelected"
							/>
						</div>
					</keep-alive>

					<!-- Draggable Divider (Desktop Only) -->
					<div
						v-if="uiStore.isDesktop"
						ref="dividerRef"
						role="separator"
						aria-orientation="vertical"
						@pointerdown="startResize"
						class="w-1 bg-gray-200 hover:bg-blue-400 cursor-col-resize relative flex-shrink-0 transition-[background-color] duration-100 hidden lg:block"
						:class="{
							'bg-blue-500': uiStore.isResizing,
							'pointer-events-none opacity-0': uiStore.isAnyDialogOpen,
							'z-[1]': !uiStore.isAnyDialogOpen,
						}"
					>
						<div
							class="absolute inset-y-0 -left-2 -right-2"
							style="cursor: col-resize"
						></div>
						<div
							class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-1 h-12 bg-gray-400 rounded-full"
							:class="{
								'bg-blue-600': uiStore.isResizing,
								'bg-blue-500': !uiStore.isResizing,
							}"
							style="transition: background-color 0.1s ease; opacity: 0.8"
						></div>
					</div>

					<!-- Right: Invoice Cart (Desktop) / Tab Content (Mobile) -->
					<keep-alive>
						<div
							v-if="uiStore.isDesktop || uiStore.mobileActiveTab === 'cart'"
							:class="[
								'flex flex-col bg-gray-50 overflow-hidden',
								uiStore.isDesktop ? 'flex-1' : 'flex-1',
							]"
							style="min-width: 300px; contain: layout style paint"
						>
							<InvoiceCart
								:items="cartStore.invoiceItems"
								:customer="cartStore.customer"
								:subtotal="cartStore.subtotal"
								:tax-amount="cartStore.totalTax"
								:discount-amount="cartStore.totalDiscount"
								:grand-total="cartStore.grandTotal"
								:additional-discount="cartStore.additionalDiscount"
								:pos-profile="shiftStore.profileName"
								:currency="shiftStore.profileCurrency"
								:applied-offers="cartStore.appliedOffers"
								:warehouses="profileWarehouses"
								:selected-payment-method="selectedQuickPaymentMethod"
								:last-invoice-total="uiStore.lastInvoiceTotal"
								@update-quantity="cartStore.updateItemQuantity"
								@update-additional-discount="handleAdditionalDiscountUpdate"
								@remove-item="
									(itemCode, uom) => cartStore.removeItem(itemCode, uom)
								"
								@select-customer="handleCustomerSelected"
								@create-customer="handleCreateCustomer"
								@edit-customer="handleEditCustomer"
								@quick-cash-pay="handleQuickCashPay"
								@pay-later-all-debt="handlePayLaterAllDebt"
								@partial-payment="handlePartialPayment"
								@customer-payment="handleCustomerPayment"
								@switch-payment-method="handleSwitchPaymentMethod"
								@clear-cart="handleClearCart"
								@save-draft="handleSaveDraft"
								@apply-coupon="uiStore.showCouponDialog = true"
								@show-offers="uiStore.showOffersDialog = true"
								@remove-offer="
									(offer) =>
										cartStore.removeOffer(
											offer,
											shiftStore.currentProfile,
											offersDialogRef.value
										)
								"
								@update-uom="handleUpdateUom"
								@edit-item="handleEditItem"
								@view-shift="uiStore.showOpenShiftDialog = true"
								@show-drafts="uiStore.showDraftDialog = true"
								@show-history="uiStore.showHistoryDialog = true"
								@show-return="uiStore.showReturnDialog = true"
								@close-shift="handleCloseShift()"
								@refocus-barcode="handleRefocusBarcode"
							@print-last-invoice="handlePrintLastInvoice"
							/>
						</div>
					</keep-alive>

					<!-- Mobile Floating Cart Button -->
					<button
						v-if="
							!uiStore.isDesktop &&
							uiStore.mobileActiveTab === 'items' &&
							cartStore.itemCount > 0
						"
						@click="uiStore.setMobileTab('cart')"
						class="lg:hidden fixed bottom-20 end-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-full p-4 shadow-2xl hover:shadow-3xl hover:from-blue-700 hover:to-blue-800 active:from-blue-800 active:to-blue-900 transition-[background,box-shadow,transform] duration-200 z-50 touch-manipulation active:scale-95 ring-4 ring-blue-100"
						:aria-label="__('View cart with {0} items', [cartStore.itemCount])"
					>
						<div class="relative">
							<svg
								class="w-7 h-7"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								stroke-width="2.5"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
								/>
							</svg>
							<span
								class="absolute -top-2 -end-2 bg-red-500 text-white text-xs font-bold rounded-full min-w-[22px] h-[22px] px-1 flex items-center justify-center shadow-lg animate-pulse"
							>
								{{ cartStore.itemCount }}
							</span>
						</div>
					</button>

					<!-- PWA Install Badge (Mobile Only) -->
					<InstallAppBadge />
				</div>
			</div>

			<!-- No Shift Placeholder -->
			<div
				v-else
				class="flex-1 flex items-center justify-center bg-gray-50"
				style="max-height: calc(100vh - 60px - var(--header-height, 60px))"
			>
				<div class="text-center">
					<div
						class="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-blue-100"
					>
						<svg
							class="h-12 w-12 text-blue-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					</div>
					<h3 class="mt-4 text-lg font-medium text-gray-900">
						{{ __("Welcome to POS-ABS") }}
					</h3>
					<p class="mt-2 text-sm text-gray-500">
						{{ __("Please open a shift to start making sales") }}
					</p>
					<Button
						variant="solid"
						theme="blue"
						@click="uiStore.showOpenShiftDialog = true"
						class="mt-6"
					>
						{{ __("Open Shift") }}
					</Button>
				</div>
			</div>

			<!-- Customer Selection Dialog -->
			<CustomerDialog
				v-model="uiStore.showCustomerDialog"
				:pos-profile="shiftStore.profileName"
				@customer-selected="handleCustomerSelected"
			/>

			<!-- Shift Opening Dialog -->
			<ShiftOpeningDialog
				v-model="uiStore.showOpenShiftDialog"
				@shift-opened="handleShiftOpened"
				@after-leave="handleRefocusBarcode"
			/>

			<!-- Shift Closing Dialog -->
			<ShiftClosingDialog
				v-model="uiStore.showCloseShiftDialog"
				:opening-shift="shiftStore.currentShift?.name"
				@shift-closed="handleShiftClosed"
				@after-leave="handleRefocusBarcode"
			/>

			<!-- Draft Invoices Dialog -->
			<DraftInvoicesDialog
				v-model="uiStore.showDraftDialog"
				:currency="shiftStore.profileCurrency"
				@load-draft="handleLoadDraft"
				@drafts-updated="draftsStore.updateDraftsCount"
				@after-leave="handleRefocusBarcode"
			/>

			<!-- Return Invoice Dialog -->
			<ReturnInvoiceDialog
				v-model="uiStore.showReturnDialog"
				:pos-profile="shiftStore.profileName"
				:pos-opening-shift="shiftStore.currentShift?.name"
				:currency="shiftStore.profileCurrency"
				@return-created="handleReturnCreated"
				@after-leave="handleRefocusBarcode"
			/>

			<!-- Coupon Dialog -->
			<CouponDialog
				v-model="uiStore.showCouponDialog"
				:subtotal="cartStore.subtotal"
				:items="cartStore.invoiceItems"
				:pos-profile="shiftStore.profileName"
				:customer="cartStore.customer?.name || cartStore.customer"
				:company="shiftStore.profileCompany"
				:currency="shiftStore.profileCurrency"
				:applied-coupon="cartStore.appliedCoupon"
				@discount-applied="handleDiscountApplied"
				@discount-removed="handleDiscountRemoved"
			/>

			<!-- Offers Dialog -->
			<OffersDialog
				ref="offersDialogRef"
				v-model="uiStore.showOffersDialog"
				:subtotal="cartStore.subtotal"
				:items="cartStore.invoiceItems"
				:pos-profile="shiftStore.profileName"
				:customer="cartStore.customer?.name || cartStore.customer"
				:company="shiftStore.profileCompany"
				:currency="shiftStore.profileCurrency"
				:applied-offers="cartStore.appliedOffers"
				@apply-offer="handleApplyOffer"
				@remove-offer="
					(offer) =>
						cartStore.removeOffer(
							offer,
							shiftStore.currentProfile,
							offersDialogRef.value
						)
				"
			/>

			<!-- Batch/Serial Dialog -->
			<BatchSerialDialog
				v-model="uiStore.showBatchSerialDialog"
				:item="cartStore.pendingItem"
				:quantity="cartStore.pendingItemQty"
				:warehouse="shiftStore.profileWarehouse"
				@batch-serial-selected="handleBatchSerialSelected"
			/>

			<!-- Generic Item Selection Dialog -->
			<ItemSelectionDialog
				v-model="uiStore.showItemSelectionDialog"
				:item="cartStore.pendingItem"
				:mode="cartStore.selectionMode"
				:pos-profile="shiftStore.profileName"
				:currency="shiftStore.profileCurrency"
				@option-selected="handleOptionSelected"
			/>

			<!-- Invoice History Dialog -->
			<InvoiceHistoryDialog
				v-model="uiStore.showHistoryDialog"
				:pos-profile="shiftStore.profileName"
				:currency="shiftStore.profileCurrency"
				@create-return="handleCreateReturnFromHistory"
				@view-invoice="handleViewInvoice"
				@print-invoice="handlePrintInvoice"
				@after-leave="handleRefocusBarcode"
			/>

			<!-- Offline Invoices Dialog -->
			<OfflineInvoicesDialog
				v-model="uiStore.showOfflineInvoicesDialog"
				:is-offline="offlineStore.isOffline"
				:pending-invoices="offlineStore.pendingInvoicesList"
				:is-syncing="offlineStore.isSyncing"
				:currency="shiftStore.profileCurrency"
				@sync-all="handleSyncAll"
				@delete-invoice="handleDeleteOfflineInvoice"
				@edit-invoice="handleEditOfflineInvoice"
				@refresh="offlineStore.loadPendingInvoices"
			/>

			<!-- Create/Edit Customer Dialog -->
			<CreateCustomerDialog
				v-model="uiStore.showCreateCustomerDialog"
				:pos-profile="shiftStore.profileName"
				:initial-name="uiStore.initialCustomerName"
				:customer="editCustomer"
				@customer-created="handleCustomerCreated"
				@customer-updated="handleCustomerUpdated"
				@after-leave="handleRefocusBarcode"
			/>

			<!-- Promotion Management -->
			<PromotionManagement
				v-model="showPromotionManagement"
				:pos-profile="shiftStore.profileName"
				:company="shiftStore.profileCompany"
				:currency="shiftStore.profileCurrency"
				@promotion-saved="handlePromotionSaved"
				@after-leave="handleRefocusBarcode"
			/>

			<!-- Reports Dialog -->
			<ReportsDialog
				v-model="showReportsDialog"
				:pos-profile="shiftStore.profileName"
				:currency="shiftStore.profileCurrency"
				@after-leave="handleRefocusBarcode"
			/>

			<!-- POS Settings -->
			<POSSettings
				v-model="showPOSSettings"
				:pos-profile="shiftStore.profileName"
				:current-warehouse="shiftStore.profileWarehouse"
				@warehouse-changed="handleWarehouseChanged"
				@after-leave="handleRefocusBarcode"
			/>

			<!-- Stock Lookup Dialog (Products Menu) -->
			<WarehouseAvailabilityDialog
				v-model="showStockLookup"
				mode="search"
				:pos-profile="shiftStore.profileName"
				:company="shiftStore.profileCompany"
				@after-leave="handleRefocusBarcode"
			/>

			<!-- Invoice Management -->
			<InvoiceManagement
				v-model="showInvoiceManagement"
				:pos-profile="shiftStore.profileName"
				:currency="shiftStore.profileCurrency"
				:history-invoices="invoiceHistoryData"
				:draft-invoices="draftsStore.drafts"
				@view-invoice="handleViewInvoice"
				@print-invoice="handlePrintInvoice"
				@load-draft="handleLoadDraftFromManagement"
				@delete-draft="handleDeleteDraft"
				@refresh-history="loadInvoiceHistoryData"
			/>

			<!-- Invoice Detail Dialog -->
			<InvoiceDetailDialog
				v-model="showInvoiceDetail"
				:invoice-name="selectedInvoiceForView"
				:pos-profile="shiftStore.profileName"
				:currency="shiftStore.profileCurrency"
				@print-invoice="handlePrintInvoice"
			/>

			<!-- Currency Exchange Dialog -->
		<CurrencyExchangeDialog
			v-model="showCurrencyExchangeDialog"
			:currency-setup="posSettingsStore.currencySetup"
			:pos-opening-shift="shiftStore.currentShift?.name"
			:pos-profile="shiftStore.profileName"
			@exchange-completed="handleExchangeCompleted"
		/>

		<!-- Sales Orders Dialog -->
			<SalesOrdersDialog
				v-model="showSalesOrdersDialog"
				:pos-profile="shiftStore.profileName"
				:currency="shiftStore.profileCurrency"
				@load-order="handleLoadSalesOrder"
			/>

			<!-- Shift Password Dialog (entry verification) -->
			<ShiftPasswordDialog
				v-model="showEntryPasswordDialog"
				:pos-profile="entryPasswordProfile"
				@verified="handleEntryPasswordVerified"
				@cancelled="handleEntryPasswordCancelled"
			/>

			<!-- Shift Notes Dialog -->
			<ShiftNotesDialog
				v-model="showShiftNotesDialog"
				:opening-shift="shiftStore.currentShift?.name"
				@after-leave="handleRefocusBarcode"
			/>

			<!-- Clear Cart Confirmation Dialog -->
			<Dialog
				v-model="uiStore.showClearCartDialog"
				:options="{ title: __('Clear Cart?'), size: 'xs' }"
				@after-leave="handleRefocusBarcode"
			>
				<template #body-content>
					<div class="py-3">
						<p class="text-sm text-gray-600">
							{{ __("Remove all {0} items from cart?", [cartStore.itemCount]) }}
						</p>
					</div>
				</template>
				<template #actions>
					<div class="flex gap-2 w-full">
						<Button
							class="flex-1"
							variant="subtle"
							@click="uiStore.showClearCartDialog = false"
						>
							{{ __("Cancel") }}
						</Button>
						<Button
							class="flex-1"
							variant="solid"
							theme="red"
							@click="confirmClearCart"
						>
							{{ __("Clear All") }}
						</Button>
					</div>
				</template>
			</Dialog>

			<!-- Logout Confirmation Dialog -->
			<Dialog
				v-model="uiStore.showLogoutDialog"
				:options="{ title: __('Sign Out Confirmation'), size: 'md' }"
				:dismissable="!session.logout.loading"
			>
				<template #body-content>
					<!-- WITH SHIFT OPEN -->
					<div v-if="shiftStore.hasOpenShift" class="px-4 py-5">
						<div class="text-center mb-6">
							<div
								class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-gradient-to-br from-red-100 to-red-200 shadow-md mb-4"
							>
								<svg
									class="h-8 w-8 text-red-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
									/>
								</svg>
							</div>
							<h3 class="text-lg font-bold text-red-600 mb-2">
								{{ __("Your Shift is Still Open!") }}
							</h3>
							<p class="text-sm text-gray-600 max-w-sm mx-auto">
								{{
									__("Close your shift first to save all transactions properly")
								}}
							</p>
						</div>

						<!-- Action Buttons -->
						<div class="space-y-3 max-w-md mx-auto">
							<!-- Recommended Action - BLUE -->
							<button
								@click="logoutWithCloseShift"
								:disabled="session.logout.loading"
								class="w-full flex items-center justify-center px-5 py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg shadow-lg hover:shadow-blue-500/30 transition-[background,box-shadow,opacity,transform] duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
							>
								<svg
									class="w-5 h-5 me-2"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
									/>
								</svg>
								{{ __("Close Shift & Sign Out") }}
							</button>

							<!-- Alternative Actions -->
							<div class="grid grid-cols-2 gap-2">
								<button
									@click="confirmLogout"
									:disabled="session.logout.loading"
									class="px-4 py-3 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-semibold text-sm rounded-lg shadow-md hover:shadow-red-500/30 transition-[background,box-shadow,opacity] duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
								>
									{{ __("Skip & Sign Out") }}
								</button>
								<button
									@click="uiStore.showLogoutDialog = false"
									:disabled="session.logout.loading"
									class="px-4 py-3 bg-white hover:bg-gray-50 text-gray-700 font-semibold text-sm rounded-lg transition-[background-color,border-color,opacity] duration-200 disabled:opacity-50 disabled:cursor-not-allowed border border-gray-300 hover:border-gray-400"
								>
									{{ __("Cancel") }}
								</button>
							</div>
						</div>
					</div>

					<!-- WITHOUT SHIFT (Simple confirmation) -->
					<div v-else class="px-4 py-5">
						<div class="text-center mb-6">
							<div
								class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-gradient-to-br from-red-100 to-red-200 shadow-md mb-4"
							>
								<svg
									class="h-8 w-8 text-red-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
									/>
								</svg>
							</div>
							<h3 class="text-lg font-bold text-red-600 mb-2">
								{{ __("Sign Out?") }}
							</h3>
							<p class="text-sm text-gray-600">
								{{ __("You will be logged out of POS-ABS") }}
							</p>
						</div>

						<div class="grid grid-cols-2 gap-3 max-w-sm mx-auto">
							<button
								@click="uiStore.showLogoutDialog = false"
								:disabled="session.logout.loading"
								class="px-5 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md hover:shadow-blue-500/30 transition-[background-color,box-shadow,opacity,transform] duration-200 disabled:opacity-50 transform hover:scale-[1.02] active:scale-[0.98]"
							>
								{{ __("Cancel") }}
							</button>
							<button
								@click="confirmLogout"
								:disabled="session.logout.loading"
								class="px-5 py-4 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-semibold rounded-lg shadow-lg hover:shadow-red-500/30 transition-[background,box-shadow,opacity,transform] duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
							>
								<span v-if="!session.logout.loading">{{ __("Sign Out") }}</span>
								<span v-else class="flex items-center justify-center">
									<svg
										class="animate-spin h-5 w-5 me-2"
										fill="none"
										viewBox="0 0 24 24"
									>
										<circle
											class="opacity-25"
											cx="12"
											cy="12"
											r="10"
											stroke="currentColor"
											stroke-width="4"
										></circle>
										<path
											class="opacity-75"
											fill="currentColor"
											d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
										></path>
									</svg>
									{{ __("Signing Out...") }}
								</span>
							</button>
						</div>
					</div>
				</template>
			</Dialog>

			<!-- Success Dialog -->
			<Dialog
				v-model="uiStore.showSuccessDialog"
				:options="{ title: __('Invoice Created Successfully'), size: 'md' }"
				@after-leave="handleRefocusBarcode"
			>
				<template #body-content>
					<div class="text-center py-6">
						<div
							class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100"
						>
							<svg
								class="h-6 w-6 text-green-600"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/>
							</svg>
						</div>
						<h3 class="mt-4 text-lg font-medium text-gray-900">
							{{
								__("Invoice {0} created successfully!", [uiStore.lastInvoiceName])
							}}
						</h3>
						<p class="mt-2 text-sm text-gray-500">
							{{ __("Paid: {0}", [formatCurrency(uiStore.lastPaidAmount)]) }}
						</p>
					</div>
				</template>
				<template #actions>
					<div class="flex gap-2">
						<Button variant="subtle" @click="uiStore.showSuccessDialog = false">
							{{ __("Close") }}
						</Button>
						<Button
							variant="solid"
							theme="blue"
							@click="
								() => {
									handlePrintInvoice({ name: uiStore.lastInvoiceName });
									uiStore.showSuccessDialog = false;
								}
							"
						>
							{{ __("Print Invoice") }}
						</Button>
					</div>
				</template>
			</Dialog>

			<!-- Error Dialog -->
			<Dialog
				v-model="uiStore.showErrorDialog"
				:options="{ title: uiStore.errorDialogTitle || __('Error'), size: 'md' }"
			>
				<template #body-content>
					<div class="py-3">
						<p class="text-sm text-gray-700 whitespace-pre-line">
							{{ uiStore.errorDialogMessage || __("An unexpected error occurred.") }}
						</p>
						<div
							v-if="uiStore.errorDetails"
							class="mt-3 pt-3 border-t border-gray-200"
						>
							<p class="text-xs text-gray-500">{{ uiStore.errorDetails }}</p>
						</div>
					</div>
				</template>
				<template #actions>
					<div class="flex justify-between items-center w-full">
						<Button
							v-if="
								uiStore.errorRetryAction === 'sync' &&
								uiStore.errorRetryActionData?.failedInvoiceId
							"
							variant="outline"
							theme="red"
							@click="handleDeleteFailedInvoice"
						>
							{{ __("Delete Invoice") }}
						</Button>
						<div v-else></div>
						<div class="flex gap-2">
							<Button variant="subtle" @click="uiStore.clearError()">
								{{ __("Close") }}
							</Button>
							<Button
								v-if="uiStore.errorRetryAction"
								variant="solid"
								@click="handleErrorRetry"
							>
								{{ __("Try Again") }}
							</Button>
						</div>
					</div>
				</template>
			</Dialog>

			<!-- Customer Payment Dialog -->
			<CustomerPaymentDialog
				v-model="showCustomerPaymentDialog"
				:customer="cartStore.customer"
				:company="shiftStore.profileCompany"
				:opening-shift="shiftStore.currentShift?.name"
				:mode-of-payment="selectedQuickPaymentMethod?.mode_of_payment || 'Cash'"
				@payment-created="handleCustomerPaymentCreated"
				@after-leave="handleRefocusBarcode"
			/>

			<!-- Supplier Dialog (selection + payment) -->
			<SupplierPaymentDialog
				v-if="posSettingsStore.allowSupplierPayment"
				v-model="showSupplierPaymentDialog"
				:supplier="supplier"
				:company="shiftStore.profileCompany"
				:opening-shift="shiftStore.currentShift?.name"
				:mode-of-payment="selectedQuickPaymentMethod?.mode_of_payment || 'Cash'"
				@select-supplier="handleSupplierSelected"
				@create-supplier="handleCreateSupplier"
				@edit-supplier="handleEditSupplier"
				@payment-created="handleSupplierPaymentCreated"
				@after-leave="handleRefocusBarcode"
			/>

                        <!-- Create Supplier Dialog -->
                        <CreateSupplierDialog
                                v-model="showCreateSupplierDialog"
                                :supplier="editingSupplier"
                                :pos-profile="shiftStore.profileName"
                                :initial-name="uiStore.initialCustomerName"
                                @supplier-created="handleSupplierCreated"
                        />

			<!-- Clear Cache Overlay -->
			<ClearCacheOverlay
				ref="clearCacheOverlayRef"
				:show="showClearCacheDialog"
				@cancel="showClearCacheDialog = false"
				@confirm="confirmClearCache"
			/>

			<!-- Footer -->
			<POSFooter />
		</template>
	</div>
</template>

<script setup>
import ShiftClosingDialog from "@/components/ShiftClosingDialog.vue";
import ShiftOpeningDialog from "@/components/ShiftOpeningDialog.vue";
import ShiftPasswordDialog from "@/components/ShiftPasswordDialog.vue";
import ShiftNotesDialog from "@/components/sale/ShiftNotesDialog.vue";
import ClearCacheOverlay from "@/components/common/ClearCacheOverlay.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import POSFooter from "@/components/common/POSFooter.vue";
import ManagementSlider from "@/components/pos/ManagementSlider.vue";
import POSHeader from "@/components/pos/POSHeader.vue";
import BatchSerialDialog from "@/components/sale/BatchSerialDialog.vue";
import CouponDialog from "@/components/sale/CouponDialog.vue";
import CustomerPaymentDialog from "@/components/sale/CustomerPaymentDialog.vue";
import CreateCustomerDialog from "@/components/sale/CreateCustomerDialog.vue";
import CreateSupplierDialog from "@/components/sale/CreateSupplierDialog.vue";
import SupplierPaymentDialog from "@/components/sale/SupplierPaymentDialog.vue";
import CustomerDialog from "@/components/sale/CustomerDialog.vue";
import DraftInvoicesDialog from "@/components/sale/DraftInvoicesDialog.vue";
import InvoiceCart from "@/components/sale/InvoiceCart.vue";
import InvoiceHistoryDialog from "@/components/sale/InvoiceHistoryDialog.vue";
import ItemSelectionDialog from "@/components/sale/ItemSelectionDialog.vue";
import ItemsSelector from "@/components/sale/ItemsSelector.vue";
import OffersDialog from "@/components/sale/OffersDialog.vue";
import OfflineInvoicesDialog from "@/components/sale/OfflineInvoicesDialog.vue";
import PromotionManagement from "@/components/sale/PromotionManagement.vue";
import ReportsDialog from "@/components/sale/ReportsDialog.vue";
import ReturnInvoiceDialog from "@/components/sale/ReturnInvoiceDialog.vue";
import WarehouseAvailabilityDialog from "@/components/sale/WarehouseAvailabilityDialog.vue";
import CurrencyExchangeDialog from "@/components/sale/CurrencyExchangeDialog.vue";
import POSSettings from "@/components/settings/POSSettings.vue";
import InvoiceManagement from "@/components/invoices/InvoiceManagement.vue";
import InvoiceDetailDialog from "@/components/invoices/InvoiceDetailDialog.vue";
import SalesOrdersDialog from "@/components/invoices/SalesOrdersDialog.vue";
import { useRealtimeStock } from "@/composables/useRealtimeStock";
import { usePOSEvents } from "@/composables/usePOSEvents";
import { useLocale } from "@/composables/useLocale";
import { session } from "@/data/session";
import { useUserData } from "@/data/user";
import { parseError } from "@/utils/errorHandler";
import { offlineWorker } from "@/utils/offline/workerClient";
import { printInvoice, printInvoiceByName } from "@/utils/printInvoice";
import { Button, Dialog, createResource } from "frappe-ui";
import { call } from "@/utils/apiWrapper";
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import { useToast } from "@/composables/useToast";
import { storeToRefs } from "pinia";

import { useCustomerSearchStore } from "@/stores/customerSearch";
import { useItemSearchStore } from "@/stores/itemSearch";
import { useStockStore } from "@/stores/stock";
// Pinia Stores
import { usePOSCartStore } from "@/stores/posCart";
import { usePOSDraftsStore } from "@/stores/posDrafts";
import { usePOSPriceListStore } from "@/stores/posPriceList";
import { usePOSSettingsStore } from "@/stores/posSettings";
import { usePOSShiftStore } from "@/stores/posShift";
import { usePOSSyncStore } from "@/stores/posSync";
import { usePOSUIStore } from "@/stores/posUI";
import { useBootstrapStore } from "@/stores/bootstrap";
import { logger } from "@/utils/logger";

// Initialize stores
const cartStore = usePOSCartStore();
const shiftStore = usePOSShiftStore();
const uiStore = usePOSUIStore();
const bootstrapStore = useBootstrapStore();
const offlineStore = usePOSSyncStore();
const draftsStore = usePOSDraftsStore();
const posSettingsStore = usePOSSettingsStore();
const priceListStore = usePOSPriceListStore();
const itemStore = useItemSearchStore();
const stockStore = useStockStore();
const showCustomerPaymentDialog = ref(false);
const showSupplierPaymentDialog = ref(false);
const supplier = ref(null);
const editingSupplier = ref(null);
const selectedQuickPaymentMethod = ref(null);

// Watch bootstrap data to auto-initialize payment method if it loads after mount
watch(
	() => bootstrapStore.loaded,
	(loaded) => {
		if (loaded && !selectedQuickPaymentMethod.value) {
			const methods = bootstrapStore.getPreloadedPaymentMethods() || [];
			if (methods.length > 0) {
				selectedQuickPaymentMethod.value = methods[0];
			}
		}
	}
);

const customerSearchStore = useCustomerSearchStore();
// Note: settingsStore is an alias to posSettingsStore (same Pinia store singleton)
const settingsStore = posSettingsStore;

// Real-time stock updates
const { onStockUpdate } = useRealtimeStock();

// POS Events system
const {
	onWarehouseChanged,
	onPricingChanged,
	onStockPolicyChanged,
	onSettingsChanged,
	onSalesOperationsChanged,
} = usePOSEvents();

// Initialize toast
const { showSuccess, showError, showWarning } = useToast();

// Initialize logger
const log = logger.create("POSSale");

// User data composable
const { userName, userImage } = useUserData();

// Locale composable for RTL support
const { isRTL } = useLocale();

// Component refs
const itemsSelectorRef = ref(null);
const offersDialogRef = ref(null);
const containerRef = ref(null);
const dividerRef = ref(null);
const logoutAfterClose = ref(false);
const editCustomer = ref(null); // Customer being edited (null for create mode)
const showClearCacheDialog = ref(false);
const clearCacheOverlayRef = ref(null);
const showSuccessDialogEnabled = ref(false); // Control whether success dialog should show

// Debounce timer for offer reapplication
const offerReapplyTimer = ref(null);

// Performance: Cache previous cart state to avoid unnecessary reapplications
let previousCartHash = "";

// Helper function to compute cart hash
function computeCartHash() {
	return cartStore.invoiceItems
		.map(
			(i) =>
				`${i.item_code}-${i.quantity}-${i.rate}-${i.discount_percentage || 0}-${
					i.discount_amount || 0
				}-${i.uom || ""}-${i.warehouse || ""}`
		)
		.join("|");
}

// Promotion dialog
const showPromotionManagement = ref(false);

// Reports dialog
const showReportsDialog = ref(false);

// Settings dialog
const showPOSSettings = ref(false);

// Stock Lookup dialog (Products menu)
const showStockLookup = ref(false);

// Invoice Management dialog
const showInvoiceManagement = ref(false);

// Invoice Detail dialog
const showInvoiceDetail = ref(false);
const selectedInvoiceForView = ref(null);

// Sales Orders dialog
const showSalesOrdersDialog = ref(false);
const showCurrencyExchangeDialog = ref(false);
const showCreateSupplierDialog = ref(false);
const showShiftNotesDialog = ref(false);
const showEntryPasswordDialog = ref(false);
const entryPasswordProfile = ref("");

// Invoice history data (used by InvoiceManagement component)
const invoiceHistoryData = ref([]);

// Stock sync status
const isStockSyncActive = ref(false);

// Warehouses state and resource
const warehousesList = ref([]);

const warehousesResource = createResource({
	url: "pos_next.api.pos_profile.get_warehouses",
	makeParams() {
		return {
			pos_profile: shiftStore.profileName,
		};
	},
	auto: false,
	onSuccess(data) {
		const warehouses = data?.message || data || [];
		warehousesList.value = warehouses;
	},
	onError(error) {
		log.error("Error loading warehouses:", error);
		warehousesList.value = [];
	},
});

// Watch for profile changes to load warehouses
watch(
	() => shiftStore.profileName,
	(newProfile) => {
		if (newProfile) {
			warehousesResource.reload();
		}
	},
	{ immediate: true }
);

// Computed for warehouses - returns all warehouses for the company
const profileWarehouses = computed(() => {
	if (warehousesList.value.length > 0) {
		return warehousesList.value.map((w) => ({
			name: w.name,
			warehouse: w.warehouse_name || w.name,
		}));
	}
	// Fallback to profile warehouse if API hasn't loaded yet
	if (shiftStore.profileWarehouse) {
		return [
			{
				name: shiftStore.profileWarehouse,
				warehouse: shiftStore.profileWarehouse,
			},
		];
	}
	return [];
});

// Resize state
let resizeState = null;
let bodyStyleSnapshot = null;

onMounted(async () => {
	// Window resize listeners (passive for better performance)
	const handleResize = () => {
		uiStore.setWindowWidth(window.innerWidth);
		updateLayoutBounds();
	};
	window.addEventListener("resize", handleResize, { passive: true });

	// Set up real-time stock update listener
	const cleanup = onStockUpdate(async (stockUpdates) => {
		// Filter updates to only include items from our warehouse(s)
		const profileWarehouses = shiftStore.profileWarehouse
			? [shiftStore.profileWarehouse]
			: warehousesList.value.map((w) => w.warehouse_name || w.name);

		const relevantUpdates = stockUpdates.filter((update) =>
			profileWarehouses.includes(update.warehouse)
		);

		if (relevantUpdates.length > 0) {
			// Apply stock updates - Pinia auto-updates UI!
			stockStore.update(relevantUpdates);
			await offlineWorker.updateStockQuantities(relevantUpdates);
		}
	});

	// Set up POS events listeners
	// Listen to warehouse changes from settings
	onWarehouseChanged(async ({ newWarehouse, oldWarehouse }) => {
		log.info(`Event: Warehouse changed from ${oldWarehouse} to ${newWarehouse}`);
		await handleWarehouseChanged(newWarehouse);
	});

	// Listen to pricing changes from settings
	onPricingChanged(async ({ changes }) => {
		log.info("Event: Pricing settings changed", changes);

		// Update tax_inclusive setting if it changed
		if (changes.hasOwnProperty("tax_inclusive")) {
			const newTaxInclusive = changes.tax_inclusive.new;
			log.info(
				`Updating tax_inclusive from ${changes.tax_inclusive.old} to ${newTaxInclusive}`
			);

			// Update the cart store tax inclusive setting
			cartStore.setTaxInclusive(newTaxInclusive);

			// Reload tax rules to ensure they're applied with the new setting
			// This is critical because tax_inclusive affects how taxes are calculated
			try {
				log.info("Reloading tax rules with new tax_inclusive setting...");
				await cartStore.loadTaxRules(shiftStore.currentShift?.pos_profile, {
					tax_inclusive: newTaxInclusive,
				});
				log.info("Tax rules reloaded successfully");
			} catch (error) {
				log.error("Failed to reload tax rules:", error);
			}
		}

		// Recalculate cart items if there are any
		if (cartStore.invoiceItems.length > 0) {
			cartStore.invoiceItems.forEach((item) => {
				cartStore.recalculateItem(item);
			});
			cartStore.rebuildIncrementalCache();

			const message = changes.hasOwnProperty("tax_inclusive")
				? __("Tax mode updated. Cart recalculated with new tax settings.")
				: __("Discount settings changed. Cart recalculated.");

			showSuccess(message);
		} else if (changes.hasOwnProperty("tax_inclusive")) {
			// Show feedback even if cart is empty
			showSuccess(
				changes.tax_inclusive.new
					? __(
							"Prices are now tax-inclusive. This will apply to new items added to cart."
					  )
					: __(
							"Prices are now tax-exclusive. This will apply to new items added to cart."
					  )
			);
		}
	});

	// Listen to stock policy changes
	onStockPolicyChanged(({ changes, requiresReload }) => {
		log.info("Event: Stock policy changed", changes);

		if (changes.allow_negative_stock) {
			const isNowAllowed = changes.allow_negative_stock.new;

			const message = isNowAllowed
				? __("Negative stock sales are now allowed")
				: __("Negative stock sales are now restricted");

			showSuccess(message);
		}
	});

	// Listen to sales operations changes
	onSalesOperationsChanged(({ changes }) => {
		log.info("Event: Sales operations settings changed", changes);

		// Reload settings in the store to get fresh values
		posSettingsStore.reloadSettings();

		// Show notification for specific important changes
		const changeLabels = {
			allow_credit_sale: __("Credit Sale"),
			allow_return: __("Returns"),
			allow_write_off_change: __("Write Off Change"),
			allow_partial_payment: __("Partial Payment"),
			silent_print: __("Silent Print"),
		};

		const changedSettings = Object.keys(changes)
			.map((key) => changeLabels[key])
			.filter(Boolean)
			.join(", ");

		if (changedSettings) {
			showSuccess(__("{0} settings applied immediately", [changedSettings]));
		}
	});

	// Listen to general settings changes (catch-all for any setting change)
	onSettingsChanged(async ({ changes }) => {
		log.info("Event: Settings changed", changes);

		// Reload settings to ensure all computed properties are fresh
		await posSettingsStore.reloadSettings();
	});

	// Store cleanup function for unmount
	onUnmounted(cleanup);

	try {
		// Start timers for current time and shift duration
		shiftStore.startTimers();

		// Check for existing open shift
		const hasShift = await shiftStore.checkShift();

		if (!hasShift) {
			uiStore.showOpenShiftDialog = true;
		} else {
			// Shift is open - require password before allowing access
			entryPasswordProfile.value = shiftStore.profileName || "";
			showEntryPasswordDialog.value = true;

			// Set POS profile and load tax rules
			if (shiftStore.currentProfile) {
				cartStore.posProfile = shiftStore.profileName;
				cartStore.posOpeningShift = shiftStore.currentShift?.name;

				// Load POS Settings
				await posSettingsStore.loadSettings(shiftStore.profileName);
				log.info("POS Settings loaded:", {
					allowPartialPayment: posSettingsStore.allowPartialPayment,
					settings: posSettingsStore.settings,
				});

				// Load tax rules with tax_inclusive setting from POS Settings
				await cartStore.loadTaxRules(shiftStore.profileName, posSettingsStore.settings);

				// Set default customer from POS Profile if configured
				await cartStore.setDefaultCustomer();

				// Load customer history to get favorite customer from localStorage
				customerSearchStore.loadCustomerHistory();

				// If no customer is set and there's a favorite customer, use it
				const { favoriteCustomerObject } = storeToRefs(customerSearchStore);
				if (!cartStore.customer && favoriteCustomerObject.value) {
					cartStore.setCustomer(favoriteCustomerObject.value);
					showSuccess(__("Favorite customer {0} selected", [favoriteCustomerObject.value.customer_name]));
				}

				// Note: POS Settings already loaded above via posSettingsStore.loadSettings()
				// No need to call again since settingsStore is an alias to posSettingsStore

				// Set warehouse context in stock store for stock operations
				if (shiftStore.profileWarehouse) {
					stockStore.setWarehouse(shiftStore.profileWarehouse);

					// Note: Periodic stock sync will be configured after items load
					// See watch() on itemStore.allItems below
				}

				// Pre-load data for offline use
				if (!offlineStore.isOffline) {
					await offlineStore.preloadDataForOffline(shiftStore.currentProfile);
				} else {
					await offlineStore.checkOfflineCacheAvailability();
				}

				// Ensure bootstrap data is loaded and has payment methods.
				// If bootstrap was preloaded before shift opened, it may contain
				// stale/empty payment_methods - reload in that case.
				const methods = bootstrapStore.getPreloadedPaymentMethods() || [];
				if (!bootstrapStore.loaded || methods.length === 0) {
					if (bootstrapStore.loaded) bootstrapStore.reset();
					await bootstrapStore.loadInitialData();
				}

				// Initialize default payment method for quick pay button
				if (!selectedQuickPaymentMethod.value) {
					const freshMethods = bootstrapStore.getPreloadedPaymentMethods() || [];
					if (freshMethods.length > 0) {
						selectedQuickPaymentMethod.value = freshMethods[0];
					} else {
						log.warn("No payment methods available from bootstrap");
					}
				}

				// Load price lists for the active POS profile
				await priceListStore.loadPriceLists(shiftStore.profileName);

				// Reload items so prices reflect the persisted price list selection
				itemStore.invalidateCache();
				if (itemsSelectorRef.value) {
					await itemsSelectorRef.value.loadItems();
				}
			}
		}

		updateLayoutBounds();
		await draftsStore.updateDraftsCount();
	} catch (error) {
		log.error("Error checking shift:", error);
	} finally {
		uiStore.setLoading(false);
	}
});

watch(
	() => shiftStore.hasOpenShift,
	(value) => {
		if (value && typeof window !== "undefined") {
			updateLayoutBounds();
		}
	}
);

// Watch for cart changes to re-apply offers
// Comprehensive watcher that detects all cart changes including:
// - Items added/removed (length changes)
// - Quantity changes
// - Rate/price changes
// - Discount changes
// - Item properties that affect offers
watch(
	() => computeCartHash(),
	(newHash) => {
		// Only proceed if there are applied offers
		if (cartStore.appliedOffers.length === 0) {
			return;
		}

		// Skip if cart content hasn't actually changed
		if (newHash === previousCartHash) {
			return;
		}

		previousCartHash = newHash;

		// Clear existing timer to prevent multiple API calls
		if (offerReapplyTimer.value) {
			clearTimeout(offerReapplyTimer.value);
		}

		// Set new timer - reapply offers after 500ms of no changes
		offerReapplyTimer.value = setTimeout(async () => {
			await cartStore.reapplyOffer(shiftStore.currentProfile);
		}, 500);
	}
);

// Watch for customer changes - customer affects which offers are applicable
watch(
	() => cartStore.customer,
	(newCustomer, oldCustomer) => {
		const newCustomerName = newCustomer?.name || newCustomer;
		const oldCustomerName = oldCustomer?.name || oldCustomer;

		// Only reapply if customer actually changed
		if (newCustomerName !== oldCustomerName) {
			// Clear existing timer
			if (offerReapplyTimer.value) {
				clearTimeout(offerReapplyTimer.value);
			}

			// Reapply offers immediately when customer changes
			// This will discover newly eligible offers even if cart has no current offers
			offerReapplyTimer.value = setTimeout(async () => {
				await cartStore.reapplyOffer(shiftStore.currentProfile);
			}, 300);
		}
	},
	{ deep: true }
);

// Watch for applied offers changes - handle when offers are added/removed
watch(
	() => cartStore.appliedOffers.length,
	() => {
		// When offers are added or removed, update the cart hash to reflect new state
		if (cartStore.invoiceItems.length > 0) {
			previousCartHash = computeCartHash();
		}
	}
);

// ============================================================================
// PERIODIC STOCK SYNC - Setup when items are loaded
// ============================================================================

// Track if periodic sync has been initialized
let periodicSyncConfigured = false;
let lastSyncWarehouse = null;
let lastSyncItemSignature = "";

// Watch for items to be loaded or changed, then configure periodic stock sync
watch(
	() => {
		const items = itemStore.allItems;
		const warehouse = shiftStore.profileWarehouse;
		const count = items.length;

		// Create signature from item codes to detect catalog changes even with same count
		const signature =
			count > 0
				? `${items[0]?.item_code || ""}-${items[Math.floor(count / 2)]?.item_code || ""}-${
						items[count - 1]?.item_code || ""
				  }`
				: "";

		return { count, warehouse, signature };
	},
	async ({ count, warehouse, signature }, oldValue) => {
		// Only proceed if we have a warehouse and items are loaded
		if (!warehouse || count === 0) return;

		const warehouseChanged = warehouse !== lastSyncWarehouse;
		const itemsChanged = signature !== lastSyncItemSignature;

		// Initial configuration when items first load
		if (!periodicSyncConfigured && count > 0) {
			log.info(`Items loaded (${count}), configuring periodic stock sync`);
			await setupPeriodicStockSync(warehouse);
			periodicSyncConfigured = true;
			lastSyncWarehouse = warehouse;
			lastSyncItemSignature = signature;
		}
		// Update configuration when warehouse changes or items change (including replacements)
		else if (periodicSyncConfigured && (warehouseChanged || itemsChanged)) {
			if (warehouseChanged) {
				log.info(
					`Warehouse changed (${lastSyncWarehouse} → ${warehouse}), updating periodic stock sync`
				);
			} else {
				log.info(
					`Items changed (catalog replacement or new items), updating periodic stock sync`
				);
			}
			await updatePeriodicStockSyncItems(warehouse);
			lastSyncWarehouse = warehouse;
			lastSyncItemSignature = signature;
		}
	}
);

onUnmounted(() => {
	window.removeEventListener("resize", () => {
		uiStore.setWindowWidth(window.innerWidth);
		updateLayoutBounds();
	});
	stopResize();

	// Stop periodic stock sync on unmount
	offlineWorker.stopStockSync().catch(() => {});
});

// ============================================================================
// PERIODIC STOCK SYNC
// ============================================================================

/**
 * Setup and start periodic stock sync from worker (called when items first load)
 */
async function setupPeriodicStockSync(warehouse) {
	try {
		// Check if user has enabled stock sync in settings
		let syncEnabled = false;
		let syncIntervalMs = 60000; // Default 60 seconds

		try {
			const savedSettings = localStorage.getItem("pos_stock_sync_settings");
			if (savedSettings) {
				const parsed = JSON.parse(savedSettings);
				syncEnabled = parsed.enabled ?? false;
				syncIntervalMs = (parsed.intervalSeconds ?? 60) * 1000;
			}
		} catch (error) {
			log.error("Failed to load stock sync settings:", error);
		}

		// Get all currently loaded item codes from the item store
		const itemCodes = itemStore.allItems.map((item) => item.item_code);

		// Configure stock sync with warehouse and items
		const config = await offlineWorker.configureStockSync({
			warehouse,
			itemCodes,
			intervalMs: syncIntervalMs,
		});

		log.info("Periodic stock sync configured:", config);

		// Only start sync if user has enabled it
		if (syncEnabled) {
			const result = await offlineWorker.startStockSync();
			log.success("Periodic stock sync started:", result.status);
			isStockSyncActive.value = true;
		} else {
			log.info("Stock sync is disabled in settings (not starting)");
			isStockSyncActive.value = false;
		}

		// Listen for stock sync completion events (regardless of enabled state)
		window.addEventListener("stockSyncComplete", handleStockSyncComplete);
		window.addEventListener("stockSyncError", handleStockSyncError);

		// Poll stock sync status every 10 seconds to update the indicator
		const statusPollInterval = setInterval(async () => {
			try {
				const status = await offlineWorker.getStockSyncStatus();
				isStockSyncActive.value = status.enabled;
			} catch (error) {
				// Ignore errors
			}
		}, 10000);

		// Cleanup on unmount
		onUnmounted(() => {
			clearInterval(statusPollInterval);
		});
	} catch (error) {
		log.error("Failed to setup periodic stock sync:", error);
	}
}

/**
 * Handle stock sync completion from worker
 */
async function handleStockSyncComplete(event) {
	const { updated, total, duration } = event.detail;

	log.success(`Background stock sync: ${updated}/${total} items updated in ${duration}ms`);

	// The worker has already updated IndexedDB
	// Now we need to refresh the Pinia stock store from IndexedDB or server
	if (updated > 0) {
		// Trigger a refresh of displayed stock
		// Note: refresh() now preserves reservations internally
		try {
			await stockStore.refresh(null, shiftStore.profileWarehouse);
		} catch (err) {
			log.error("Failed to refresh stock after background sync:", err);
		}

		// Refresh cache stats to update the "Last Sync" timestamp in the tooltip
		try {
			const stats = await offlineWorker.getCacheStats();
			itemStore.cacheStats = stats;
		} catch (error) {
			log.error("Failed to refresh cache stats:", error);
		}
	}
}

/**
 * Handle stock sync errors from worker
 */
function handleStockSyncError(event) {
	const { message } = event.detail;
	log.warn("Background stock sync error:", message);
}

/**
 * Update periodic stock sync with newly loaded items
 * Called when more items are loaded dynamically (pagination, background cache)
 */
async function updatePeriodicStockSyncItems(warehouse) {
	try {
		// Get all currently loaded item codes
		const itemCodes = itemStore.allItems.map((item) => item.item_code);

		// Reconfigure worker with updated item list
		await offlineWorker.configureStockSync({
			warehouse,
			itemCodes,
			// Keep existing interval setting
		});

		log.info(`Updated periodic stock sync with ${itemCodes.length} items`);
	} catch (error) {
		log.error("Failed to update periodic stock sync items:", error);
	}
}

// Cleanup event listeners on unmount
onUnmounted(() => {
	window.removeEventListener("stockSyncComplete", handleStockSyncComplete);
	window.removeEventListener("stockSyncError", handleStockSyncError);
});

// Handlers
async function handleShiftOpened() {
	uiStore.showOpenShiftDialog = false;
	if (shiftStore.currentProfile) {
		cartStore.posProfile = shiftStore.profileName;
		cartStore.posOpeningShift = shiftStore.currentShift?.name;
		// Load POS Settings first to get tax_inclusive setting
		await posSettingsStore.loadSettings(shiftStore.profileName);
		// Load tax rules with tax_inclusive setting
		await cartStore.loadTaxRules(shiftStore.profileName, posSettingsStore.settings);

		// CRITICAL: Reload bootstrap data after shift open.
		// Bootstrap may have been preloaded before shift was opened,
		// resulting in stale/empty payment_methods. Reset and reload
		// to ensure payment methods are available for the current profile.
		try {
			bootstrapStore.reset();
			await bootstrapStore.loadInitialData();

			// Reinitialize payment methods from fresh bootstrap data
			const methods = bootstrapStore.getPreloadedPaymentMethods() || [];
			if (methods.length > 0) {
				selectedQuickPaymentMethod.value = methods[0];
			} else {
				log.warn("No payment methods available after shift open");
			}

			// Reload price lists for the new shift
			await priceListStore.loadPriceLists(shiftStore.profileName);

			// Reload items so prices reflect the persisted price list selection
			itemStore.invalidateCache();
			if (itemsSelectorRef.value) {
				await itemsSelectorRef.value.loadItems();
			}
		} catch (error) {
			log.error("Failed to reload bootstrap after shift open:", error);
		}
	}
	showSuccess(__("You can now start making sales"));
}

function handleShiftClosed() {
	uiStore.showCloseShiftDialog = false;
	showSuccess(__("Shift closed successfully"));

	// Check if logout should happen after closing shift
	if (logoutAfterClose.value) {
		logoutAfterClose.value = false;
		// Clear all dialog states to prevent stale state on next login
		uiStore.resetAllDialogs();
		session.logout.submit();
	} else {
		setTimeout(() => {
			uiStore.showOpenShiftDialog = true;
		}, 500);
	}
}

function handleEntryPasswordVerified() {
	showSuccess(__("Shift verified. Welcome back!"));
}

function handleEntryPasswordCancelled() {
	// Password cancelled - log out the user
	uiStore.resetAllDialogs();
	session.logout.submit();
}

function handleItemSelected(item, autoAdd = false) {
	// Quantity: from scale barcode (RLS1100C) API returns item.qty (weight in kg), otherwise 1
	const qty = item.qty != null && item.qty > 0 ? item.qty : 1;

	// Auto-add mode
	if (autoAdd) {
		try {
			cartStore.addItem(item, qty, true, shiftStore.currentProfile);
			clearSearchAndRefocusBarcode();
		} catch (error) {
			uiStore.showError(
				__("Insufficient Stock"),
				error.message,
				__("Item: {0}", [item.item_code])
			);
		}
		return;
	}

	// Check stock availability first (before any dialogs)
	// Skip validation for:
	// - batch/serial items (they have their own validation in the dialog)
	// - template items with variants (variants carry their own stock)
	// Product Bundles have calculated stock based on component availability
	if (
		settingsStore.shouldEnforceStockValidation() &&
		(item.is_stock_item || item.is_bundle) &&
		!item.has_serial_no &&
		!item.has_batch_no &&
		!item.has_variants
	) {
		const actualQty = Math.floor(item.actual_qty ?? item.stock_qty ?? 0);

		if (actualQty <= 0) {
			showError(
				item.is_bundle
					? __(
							'"{0}" cannot be added to cart. Bundle is out of stock. Allow Negative Stock is disabled.',
							[item.item_name]
					  )
					: __(
							'"{0}" cannot be added to cart. Item is out of stock. Allow Negative Stock is disabled.',
							[item.item_name]
					  )
			);
			return;
		}
		if (qty > actualQty) {
			showError(
				__('Insufficient stock for "{0}". Requested: {1}, Available: {2}', [
					item.item_name,
					qty,
					actualQty,
				])
			);
			return;
		}
	}

	// Check for variants
	if (item.has_variants) {
		cartStore.setPendingItem(item, qty, "variant");
		uiStore.showItemSelectionDialog = true;
		return;
	}

	// No UOM selection dialog: add with default (stock) unit directly

	// Check for batch/serial
	if (item.has_batch_no || item.has_serial_no) {
		cartStore.setPendingItem(item, qty);
		uiStore.showBatchSerialDialog = true;
		return;
	}

	// Add to cart
	try {
		cartStore.addItem(item, qty, false, shiftStore.currentProfile);
		clearSearchAndRefocusBarcode();
	} catch (error) {
		uiStore.showError(
			__("Insufficient Stock"),
			error.message,
			__("Item: {0}", [item.item_code])
		);
	}
}

function clearSearchAndRefocusBarcode() {
	itemStore.clearSearch();
	nextTick(() => {
		itemsSelectorRef.value?.focusBarcode();
	});
}

async function handleEditItem(updatedItem) {
	await cartStore.updateItemDetails(updatedItem.item_code, updatedItem);
}

function handleAdditionalDiscountUpdate(discountAmount) {
	// Update the additional discount value in the cart store
	cartStore.additionalDiscount = discountAmount;

	// Rebuild the cache to recalculate totals
	cartStore.rebuildIncrementalCache();
}

function handleCustomerSelected(selectedCustomer) {
	if (selectedCustomer) {
		cartStore.setCustomer(selectedCustomer);
		uiStore.showCustomerDialog = false;
		showSuccess(__("{0} selected", [selectedCustomer.customer_name]));
		handleRefocusBarcode();
	} else {
		cartStore.setCustomer(null);
	}
}

function handleCreateCustomer(searchValue) {
	editCustomer.value = null; // Clear edit mode
	uiStore.setInitialCustomerName(searchValue || "");
	uiStore.showCreateCustomerDialog = true;
}

function handleEditCustomer(customer) {
	editCustomer.value = customer; // Set customer for edit mode
	uiStore.setInitialCustomerName("");
	uiStore.showCreateCustomerDialog = true;
}

/** Get default cash payment method for quick pay (from bootstrap or first available) */
function getDefaultCashPaymentMethod() {
	const methods = bootstrapStore.getPreloadedPaymentMethods() || [];
	if (methods.length === 0) return null;
	// Prefer the user-selected quick payment method if still available
	if (selectedQuickPaymentMethod.value) {
		const selected = methods.find(
			(m) => m.mode_of_payment === selectedQuickPaymentMethod.value.mode_of_payment
		);
		if (selected) return selected;
	}
	const defaultMethod = methods.find((m) => m.default === 1);
	if (defaultMethod) return defaultMethod;
	const cashMethod = methods.find((m) => (m.type || "").toLowerCase() === "cash");
	if (cashMethod) return cashMethod;
	return methods[0];
}

function handleSwitchPaymentMethod() {
	const methods = bootstrapStore.getPreloadedPaymentMethods() || [];
	if (methods.length <= 1) return;
	const current = selectedQuickPaymentMethod.value;
	let nextIndex = 0;
	if (current) {
		const currentIndex = methods.findIndex(
			(m) => m.mode_of_payment === current.mode_of_payment
		);
		if (currentIndex >= 0) {
			nextIndex = (currentIndex + 1) % methods.length;
		}
	}
	selectedQuickPaymentMethod.value = methods[nextIndex];
	const translatedMop = __(methods[nextIndex].mode_of_payment);
	frappe.show_alert({
		message: __("تم تحويل طريقة الدفع إلى {0}", [translatedMop]),
		indicator: "green",
	});
}

async function handlePriceListChange(newPriceList) {
	if (!newPriceList || newPriceList === priceListStore.activePriceList) return;

	const manualItems = cartStore.invoiceItems.filter((item) => item.is_manual_price);
	let reapplyManual = true;
	if (manualItems.length > 0) {
		reapplyManual = await new Promise((resolve) => {
			window.frappe?.confirm(
				__("Some items have manually edited prices. Reapply the new price list prices?"),
				() => resolve(true),
				() => resolve(false)
			);
		});
	}

	priceListStore.setSelectedPriceList(newPriceList, shiftStore.profileName);

	if (cartStore.invoiceItems.length > 0) {
		await updateCartPricesForPriceList(reapplyManual);
		cartStore.rebuildIncrementalCache();
		previousCartHash = computeCartHash();
		await cartStore.reapplyOffer(shiftStore.currentProfile);
	}

	itemStore.invalidateCache();
	if (itemsSelectorRef.value) {
		await itemsSelectorRef.value.loadItems();
	}

	showSuccess(__("Price list updated to {0}", [newPriceList]));
}

async function updateCartPricesForPriceList(reapplyManual) {
	for (const item of cartStore.invoiceItems) {
		if (item.is_manual_price && !reapplyManual) continue;
		try {
			const details = await call("pos_next.api.items.get_item_details", {
				item_code: item.item_code,
				pos_profile: cartStore.posProfile,
				customer: cartStore.customer?.name || cartStore.customer,
				qty: item.quantity,
				uom: item.uom,
				price_list: priceListStore.activePriceList,
			});
			const newRate = details?.price_list_rate || details?.rate || 0;
			if (newRate > 0) {
				item.rate = newRate;
				item.price_list_rate = details.price_list_rate || newRate;
				if (reapplyManual) item.is_manual_price = false;
				cartStore.recalculateItem(item);
			}
		} catch (error) {
			log.error("Failed to update price for item", item.item_code, error);
		}
	}
}

function handleQuickCashPay() {
	handleQuickCashPayInternal(false);
}

async function handleQuickCashPayInternal(forcePrint) {
	if (cartStore.isEmpty) {
		showWarning(__("Please add items to cart before proceeding to payment"));
		return;
	}
	const customerValue = cartStore.customer?.name || cartStore.customer;
	if (!customerValue && !shiftStore.profileCustomer) {
		showWarning(__("Please select a customer before proceeding"));
		uiStore.showCustomerDialog = true;
		return;
	}
	const cashMethod = getDefaultCashPaymentMethod();
	if (!cashMethod) {
		showWarning(__("No payment method available."));
		return;
	}
	const grandTotal = cartStore.grandTotal;
	const paymentData = {
		payments: [
			{
				mode_of_payment: cashMethod.mode_of_payment,
				amount: grandTotal,
				type: cashMethod.type || "Cash",
			},
		],
		change_amount: 0,
		is_partial_payment: false,
		paid_amount: grandTotal,
		outstanding_amount: 0,
		sales_team: null,
		delivery_date: null,
	};
	await handlePaymentCompleted(paymentData, { forcePrint });
}

async function handlePayLaterAllDebt() {
	if (cartStore.isEmpty) {
		showWarning(__("Please add items to cart before proceeding"));
		return;
	}
	const customerValue = cartStore.customer?.name || cartStore.customer;
	if (!customerValue && !shiftStore.profileCustomer) {
		showWarning(__("Please select a customer before proceeding"));
		uiStore.showCustomerDialog = true;
		return;
	}
	// Pay later with all debt - credit sale (no immediate payment)
	const grandTotal = cartStore.grandTotal;
	const paymentData = {
		payments: [], // No payments - full amount on credit
		change_amount: 0,
		is_partial_payment: false,
		is_credit_sale: true, // Mark as credit sale
		paid_amount: 0, // Nothing paid yet
		outstanding_amount: grandTotal, // Full amount is outstanding
		sales_team: null,
		delivery_date: null,
	};
	await handlePaymentCompleted(paymentData, { forcePrint: false });
}

async function handlePartialPayment(amount) {
	if (cartStore.isEmpty) {
		showWarning(__("Please add items to cart before proceeding to payment"));
		return;
	}
	const customerValue = cartStore.customer?.name || cartStore.customer;
	if (!customerValue && !shiftStore.profileCustomer) {
		showWarning(__("Please select a customer before proceeding"));
		uiStore.showCustomerDialog = true;
		return;
	}
	// Validate amount
	if (!amount || amount <= 0) {
		showWarning(__("Please enter a valid amount"));
		return;
	}
	if (amount >= cartStore.grandTotal) {
		showWarning(__("Partial payment amount must be less than total"));
		return;
	}
	// Get default cash payment method
	const cashMethod = getDefaultCashPaymentMethod();
	if (!cashMethod) {
		showWarning(__("No payment method available"));
		return;
	}
	// Process partial payment directly
	const grandTotal = cartStore.grandTotal;
	const outstandingAmount = grandTotal - amount;
	const paymentData = {
		payments: [
			{
				mode_of_payment: cashMethod.mode_of_payment,
				amount: amount,
				type: cashMethod.type || "Cash",
			},
		],
		change_amount: 0,
		is_partial_payment: true,
		paid_amount: amount,
		outstanding_amount: outstandingAmount,
		sales_team: null,
		delivery_date: null,
	};
	await handlePaymentCompleted(paymentData, { forcePrint: false });
}

async function handleDeleteFailedInvoice() {
	if (!uiStore.errorRetryActionData?.failedInvoiceId) return;

	const invoiceId = uiStore.errorRetryActionData.failedInvoiceId;
	uiStore.clearError();

	try {
		await offlineStore.deleteOfflineInvoice(invoiceId);
	} catch (error) {
		// Error is handled in the store
	}
}

async function handleErrorRetry() {
	uiStore.clearError();
	if (uiStore.errorRetryAction === "sync") {
		await offlineStore.loadPendingInvoices();
		setTimeout(() => {
			handleSyncClick();
		}, 300);
	}
}

async function handlePaymentCompleted(paymentData, options = {}) {
	try {
		let customerValue = cartStore.customer?.name || cartStore.customer;
		if (!customerValue && !shiftStore.profileCustomer) {
			const favCustomer = customerSearchStore.favoriteCustomerObject;
			if (favCustomer) {
				cartStore.setCustomer(favCustomer);
				customerValue = favCustomer.name;
				showSuccess(__('Favorite customer {0} selected', [favCustomer.customer_name]));
			} else {
				showWarning(__("Please select a customer before proceeding"));
				uiStore.showCustomerDialog = true;
				return;
			}
		}
		const forcePrint = options.forcePrint === true;

		cartStore.payments = [];
		if (paymentData.payments && Array.isArray(paymentData.payments)) {
			paymentData.payments.forEach((p) => {
				cartStore.payments.push({
					mode_of_payment: p.mode_of_payment,
					amount: p.amount,
					type: p.type,
				});
			});
		}

		// Store sales team data if provided
		if (paymentData.sales_team && Array.isArray(paymentData.sales_team)) {
			cartStore.salesTeam = paymentData.sales_team;
		} else {
			cartStore.salesTeam = [];
		}

		// Set delivery date for Sales Orders
		if (paymentData.delivery_date) {
			cartStore.setDeliveryDate(paymentData.delivery_date);
		}

		// Delete draft if it exists (since we're submitting/saving invoice)
		const draftIdToDelete = cartStore.currentDraftId;

		if (offlineStore.isOffline) {
			// Use the same item transformation as online flow for consistency
			// This ensures rate, discount_percentage, discount_amount, and pricing_rules
			// are all correctly formatted for ERPNext
			const preparedItems = cartStore.formatItemsForSubmission(cartStore.invoiceItems);

			const invoiceData = {
				pos_profile: cartStore.posProfile,
				posa_pos_opening_shift: cartStore.posOpeningShift,
				customer: customerValue || shiftStore.profileCustomer,
				items: preparedItems,
				payments: JSON.parse(JSON.stringify(cartStore.payments)),
				sales_team: JSON.parse(JSON.stringify(cartStore.salesTeam || [])),
				grand_total: cartStore.grandTotal,
				total_tax: cartStore.totalTax,
				total_discount: cartStore.totalDiscount,
			};

			await offlineStore.saveInvoiceOffline(invoiceData);
			if (showSuccessDialogEnabled.value) {
				uiStore.showSuccess(
					`OFFLINE-${Date.now()}`,
					cartStore.grandTotal,
					paymentData.paid_amount
				);
			}
			await cartStore.clearCart();
			// Set favorite customer after payment
			await setFavoriteCustomerIfExists();
			// Reset cart hash after successful payment
			previousCartHash = "";

			// Delete draft after successful save
			if (draftIdToDelete) {
				draftsStore.deleteDraft(draftIdToDelete);
			}

			showSuccess(__("Invoice saved offline. Will sync when online"));
			if (!showSuccessDialogEnabled.value) {
				handleRefocusBarcode();
			}
		} else {
			// Get item codes from cart before clearing
			const soldItemCodes = cartStore.invoiceItems.map((item) => item.item_code);

			const result = await cartStore.submitInvoice();

			if (result) {
				const invoiceName = result.name || result.message?.name || __("Unknown");
				const invoiceTotal = result.grand_total || result.total || 0;
				const paidAmount = paymentData.paid_amount || invoiceTotal;

				await cartStore.clearCart();
				// Set favorite customer after payment
				await setFavoriteCustomerIfExists();
				// Reset cart hash after successful payment
				previousCartHash = "";

				// Delete draft after successful submission
				if (draftIdToDelete) {
					draftsStore.deleteDraft(draftIdToDelete);
				}

				// Refresh stock - Direct API (50-200ms), no Socket.IO lag!
				await stockStore.refresh(soldItemCodes, shiftStore.profileWarehouse);

				if (shiftStore.autoPrintEnabled || forcePrint) {
					try {
						await handlePrintInvoice({ name: invoiceName });
						showSuccess(__("Invoice {0} created and sent to printer", [invoiceName]));
					} catch (error) {
						log.error("Auto-print error:", error);
						showWarning(__("Invoice {0} created but print failed", [invoiceName]));
					}
				} else {
					if (showSuccessDialogEnabled.value) {
						uiStore.showSuccess(invoiceName, invoiceTotal, paidAmount);
					}
					showSuccess(__("Invoice {0} created successfully", [invoiceName]));
				}
				if (!showSuccessDialogEnabled.value || shiftStore.autoPrintEnabled || forcePrint) {
					handleRefocusBarcode();
				}
			}
		}

		// Reset quick payment method to default after successful payment
		const allMethods = bootstrapStore.getPreloadedPaymentMethods() || [];
		if (allMethods.length > 0) {
			const defaultMethod = allMethods.find((m) => m.default) || allMethods[0];
			selectedQuickPaymentMethod.value = defaultMethod;
		}
	} catch (error) {
		log.error("Error submitting invoice:", error);

		const errorContext = parseError(error);
		uiStore.showError(
			errorContext.title || __("Error"),
			errorContext.message || __("An unexpected error occurred"),
			errorContext.technicalDetails || null
		);

		if (errorContext.type === "error") {
			showError(errorContext.message);
		} else if (errorContext.type === "warning") {
			showWarning(errorContext.message);
		} else {
			showWarning(errorContext.message);
		}
	}
}

function handleClearCart() {
	if (cartStore.isEmpty) return;
	uiStore.showClearCartDialog = true;
}

async function setFavoriteCustomerIfExists() {
	// Set favorite customer after cart is cleared/payment completed
	try {
		const favoriteCustomerId = localStorage.getItem("pos_favorite_customer");
		if (favoriteCustomerId) {
			const favoriteId = JSON.parse(favoriteCustomerId);
			if (favoriteId) {
				// Ensure customers are loaded
				await customerSearchStore.loadAllCustomers(shiftStore.profileName);
				// Find and set favorite customer
				const favoriteCustomer = customerSearchStore.allCustomers.find(
					(c) => c.name === favoriteId
				);
				if (favoriteCustomer) {
					cartStore.setCustomer({ ...favoriteCustomer });
				}
			}
		}
	} catch (error) {
		// Silent fail - favorite customer is optional
	}
}

async function confirmClearCart() {
	await cartStore.clearCart();
	// Set favorite customer after clearing cart
	await setFavoriteCustomerIfExists();
	// Reset cart hash when cart is cleared
	previousCartHash = "";
	uiStore.showClearCartDialog = false;
	showSuccess(__("All items removed from cart"));
	handleRefocusBarcode();
}

async function handleOptionSelected(option) {
	if (!cartStore.pendingItem) return;

	try {
		if (option.type === "variant") {
			const variant = option.data;

			// Stock validation for variants (same as regular items)
			if (
				settingsStore.shouldEnforceStockValidation() &&
				variant.is_stock_item &&
				!variant.has_serial_no &&
				!variant.has_batch_no
			) {
				const actualQty = Math.floor(variant.actual_qty ?? 0);
				if (actualQty <= 0) {
					showError(
						__('"{0}" cannot be added to cart. Item is out of stock. Allow Negative Stock is disabled.', [variant.item_name])
					);
					return;
				}
			}

			// No UOM selection: add variant with default (stock) unit directly
			if (variant.item_uoms && variant.item_uoms.length > 0) {
				try {
					cartStore.addItem(
						variant,
						cartStore.pendingItemQty,
						false,
						shiftStore.currentProfile
					);
					uiStore.showItemSelectionDialog = false;
					cartStore.clearPendingItem();
					clearSearchAndRefocusBarcode();
					showSuccess(__("{0} added to cart", [variant.item_name]));
				} catch (error) {
					showError(error.message);
				}
				return;
			}

			if (variant.has_batch_no || variant.has_serial_no) {
				cartStore.setPendingItem(variant, cartStore.pendingItemQty);
				uiStore.showItemSelectionDialog = false;
				uiStore.showBatchSerialDialog = true;
			} else {
				try {
					cartStore.addItem(
						variant,
						cartStore.pendingItemQty,
						false,
						shiftStore.currentProfile
					);
					uiStore.showItemSelectionDialog = false;
					cartStore.clearPendingItem();
					clearSearchAndRefocusBarcode();
					showSuccess(__("{0} added to cart", [variant.item_name]));
				} catch (error) {
					showError(error.message);
				}
			}
		} else if (option.type === "uom") {
			const qty = option.quantity || cartStore.pendingItemQty;
			const itemDetails = await cartStore.getItemDetailsResource.submit({
				item_code: cartStore.pendingItem.item_code,
				pos_profile: cartStore.posProfile,
				customer: cartStore.customer?.name || cartStore.customer,
				qty: qty,
				uom: option.uom,
			});

			const itemToAdd = {
				...cartStore.pendingItem,
				uom: option.uom,
				conversion_factor: option.conversion_factor,
				rate: itemDetails.price_list_rate || itemDetails.rate,
				price_list_rate: itemDetails.price_list_rate,
			};

			if (itemToAdd.has_batch_no || itemToAdd.has_serial_no) {
				cartStore.setPendingItem(itemToAdd, qty);
				uiStore.showItemSelectionDialog = false;
				uiStore.showBatchSerialDialog = true;
			} else {
				try {
					cartStore.addItem(itemToAdd, qty, false, shiftStore.currentProfile);
					uiStore.showItemSelectionDialog = false;
					cartStore.clearPendingItem();
					clearSearchAndRefocusBarcode();
					showSuccess(__("{0} ({1}) added to cart", [itemToAdd.item_name, option.uom]));
				} catch (error) {
					showError(error.message);
				}
			}
		}
	} catch (error) {
		log.error("Error handling option selection:", error);
		showError(__("Failed to process selection. Please try again."));
	}
}

function handleCloseShift() {
	uiStore.showCloseShiftDialog = true;
}

async function handleUpdateUom(itemCode, newUom, oldUom) {
	await cartStore.changeItemUOM(itemCode, newUom, oldUom);
	handleRefocusBarcode();
}

function handleRefocusBarcode() {
	console.log('handleRefocusBarcode called, ref:', itemsSelectorRef.value);
	// Delay to let the browser/dialog focus restoration settle before refocusing barcode
	setTimeout(() => {
		console.log('delayed refocus, activeElement before:', document.activeElement);
		itemsSelectorRef.value?.focusBarcode();
		console.log('delayed refocus, activeElement after:', document.activeElement);
	}, 150);
}

function formatCurrency(amount) {
	return Number.parseFloat(amount || 0).toFixed(2);
}

function confirmLogout() {
	logoutAfterClose.value = false;
	// Clear cart to prevent stale items on next login
	cartStore.clearCart();
	// Clear all dialog states to prevent stale state on next login
	uiStore.resetAllDialogs();
	session.logout.submit();
}

function logoutWithCloseShift() {
	// Open close shift dialog and remember to logout after closing
	logoutAfterClose.value = true;
	uiStore.showLogoutDialog = false;
	uiStore.showCloseShiftDialog = true;
}

async function handleSaveDraft() {
	const savedDraft = await draftsStore.saveDraftInvoice(
		cartStore.invoiceItems,
		cartStore.customer,
		cartStore.posProfile,
		cartStore.appliedOffers,
		cartStore.currentDraftId,
		cartStore.draftNote
	);
	if (savedDraft) {
		cartStore.clearCart();
		// Reset cart hash when cart is saved as draft and cleared
		previousCartHash = "";
		// Set favorite customer after saving draft
		await setFavoriteCustomerIfExists();
		// Focus on barcode input after saving draft
		nextTick(() => {
			const barcodeInput = document.getElementById("item-search");
			if (barcodeInput) barcodeInput.focus();
		});
	}
}

async function handleLoadDraft(draft) {
	try {
		// If current cart has items, save it as draft before loading new one
		if (!cartStore.isEmpty) {
			const saved = await draftsStore.saveDraftInvoice(
				cartStore.invoiceItems,
				cartStore.customer,
				cartStore.posProfile,
				cartStore.appliedOffers,
				cartStore.currentDraftId
			);

			if (!saved) {
				showError(
					__(
						"Failed to save current cart. Draft loading cancelled to prevent data loss."
					)
				);
				return;
			}
			// No need to clear here as we're about to overwrite cart contents
		}

		const draftData = await draftsStore.loadDraft(draft);
		cartStore.invoiceItems = draftData.items;
		cartStore.setCustomer(draftData.customer);
		cartStore.currentDraftId = draft.draft_id; // Set current draft ID
		cartStore.draftNote = draftData.note || ""; // Restore draft note

		// Rebuild incremental cache to recalculate totals
		cartStore.rebuildIncrementalCache();

		// Restore applied offers if they were saved
		if (draftData.applied_offers && draftData.applied_offers.length > 0) {
			cartStore.appliedOffers = draftData.applied_offers;
			// Trigger offer reapplication to ensure they apply to all items
			await cartStore.reapplyOffer(shiftStore.currentProfile);
		}

		// Initialize cart hash for the loaded cart so watchers work correctly
		previousCartHash = computeCartHash();

		uiStore.showDraftDialog = false;
	} catch (error) {
		log.error("Error loading draft:", error);
	}
}

function handleReturnCreated(returnInvoice) {
	showSuccess(__("Return invoice {0} created successfully", [returnInvoice.name]));
}

function handleDiscountApplied(discount) {
	cartStore.applyDiscountToCart(discount);
	uiStore.showCouponDialog = false;
}

function handleDiscountRemoved() {
	cartStore.removeDiscountFromCart();
}

async function handleApplyOffer(offer) {
	const success = await cartStore.applyOffer(
		offer,
		shiftStore.currentProfile,
		offersDialogRef.value
	);
	if (success) {
		uiStore.showOffersDialog = false;
	}
}

function handleBatchSerialSelected(batchSerial) {
	if (cartStore.pendingItem) {
		// Use quantity from batchSerial if provided (for multiple serial numbers), otherwise use pendingItemQty
		const qty = batchSerial.quantity || cartStore.pendingItemQty;
		const itemToAdd = {
			...cartStore.pendingItem,
			quantity: qty,
			...batchSerial,
		};
		try {
			cartStore.addItem(itemToAdd, qty, false, shiftStore.currentProfile);
			cartStore.clearPendingItem();
			clearSearchAndRefocusBarcode();
		} catch (error) {
			showError(error.message);
		}
	}
}

function handleCreateReturnFromHistory(invoice) {
	uiStore.showReturnDialog = true;
	showWarning(__("Creating return for invoice {0}", [invoice.name]));
}

async function handleCustomerCreated(newCustomer) {
	cartStore.setCustomer(newCustomer);
	uiStore.showCreateCustomerDialog = false;
	editCustomer.value = null; // Clear edit mode

	// Add new customer to IndexedDB cache for instant search availability
	await customerSearchStore.addCustomerToCache(newCustomer);

	showSuccess(__("{0} created and selected", [newCustomer.customer_name]));
	handleRefocusBarcode();
}

async function handleCustomerUpdated(updatedCustomer) {
	cartStore.setCustomer(updatedCustomer);
	uiStore.showCreateCustomerDialog = false;
	editCustomer.value = null; // Clear edit mode

	// Update customer in IndexedDB cache for instant search availability
	await customerSearchStore.addCustomerToCache(updatedCustomer);

	showSuccess(__("{0} updated", [updatedCustomer.customer_name]));
	handleRefocusBarcode();
}

function handleSupplierSelected(selectedSupplier) {
	supplier.value = selectedSupplier;
	if (selectedSupplier) {
		showSuccess(__("{0} selected", [selectedSupplier.supplier_name || selectedSupplier.name]));
	}
}

function handleCreateSupplier(searchValue) {
	uiStore.setInitialCustomerName(searchValue || "");
	editingSupplier.value = null;
	showCreateSupplierDialog.value = true;
}

function handleEditSupplier(sup) {
	editingSupplier.value = sup || null;
	showCreateSupplierDialog.value = true;
}

function handleSupplierPayment(sup) {
	showSupplierPaymentDialog.value = true;
}

async function handleSupplierCreated(newSupplier) {
	supplier.value = newSupplier;
	showCreateSupplierDialog.value = false;
	showSuccess(__("{0} created and selected", [newSupplier.supplier_name || newSupplier.name]));
}

async function handleRefresh() {
	try {
		log.info("Clearing cache and reloading page...");

		// Import the clear functions from db.js
		const { clearCachedData, clearBrowserCache } = await import("@/utils/offline/db.js");

		// Clear IndexedDB cache (preserves invoices, drafts, and settings)
		await clearCachedData({
			preserveInvoices: true,
			preserveDrafts: true,
			preserveSettings: true,
		});

		// Clear browser localStorage and sessionStorage
		clearBrowserCache();

		log.success("Cache cleared, reloading page...");

		// Reload the page to start fresh
		window.location.reload();
	} catch (error) {
		log.error("Error clearing cache before reload:", error);
		// Still try to reload even if cache clear failed
		window.location.reload();
	}
}

function handleClearCache() {
	showClearCacheDialog.value = true;
}

async function confirmClearCache() {
	try {
		// Keep overlay open to show clearing animation
		log.info("Clearing cached data...");

		// Import the clear functions from db.js
		const { clearCachedData, clearBrowserCache } = await import("@/utils/offline/db.js");

		// Clear IndexedDB cache (preserves invoices, drafts, and settings by default)
		const dbResult = await clearCachedData({
			preserveInvoices: true,
			preserveDrafts: true,
			preserveSettings: true,
		});

		// Clear browser localStorage and sessionStorage
		const browserResult = clearBrowserCache();

		if (dbResult.success && browserResult.success) {
			log.success("Cache cleared successfully", {
				db: dbResult.cleared,
				browser: browserResult.cleared,
			});

			// Invalidate item store cache
			itemStore.invalidateCache();

			// Reload items to fetch fresh data
			if (itemsSelectorRef.value) {
				await itemsSelectorRef.value.loadItems();
			}

			// Refresh stock
			await stockStore.refresh(null, shiftStore.profileWarehouse);

			// Update cache stats
			const stats = await offlineWorker.getCacheStats();
			itemStore.cacheStats = stats;

			// Close overlay and reset state
			showClearCacheDialog.value = false;
			if (clearCacheOverlayRef.value) {
				clearCacheOverlayRef.value.reset();
			}

			showSuccess(__("All cached data has been cleared successfully"));
		} else {
			throw new Error("Failed to clear cache completely");
		}
	} catch (error) {
		log.error("Error clearing cache:", error);

		// Close overlay on error
		showClearCacheDialog.value = false;
		if (clearCacheOverlayRef.value) {
			clearCacheOverlayRef.value.reset();
		}

		showError(__("Failed to clear cache. Please try again."));
	}
}

async function handleEditOfflineInvoice(invoice) {
	try {
		cartStore.clearCart();

		const invoiceData = invoice.data;

		if (invoiceData.customer) {
			cartStore.setCustomer(invoiceData.customer);
		}

		if (invoiceData.items && invoiceData.items.length > 0) {
			for (const item of invoiceData.items) {
				// Use autoAdd=true to skip stock validation when loading saved invoices
				// Check both quantity and qty fields since items are stored with 'quantity'
				cartStore.addItem(
					item,
					item.quantity || item.qty || 1,
					true,
					shiftStore.currentProfile
				);
			}
		}

		// Initialize cart hash for the loaded cart so watchers work correctly
		previousCartHash = computeCartHash();

		await offlineStore.deleteOfflineInvoice(invoice.id);

		showSuccess(__("Invoice loaded to cart for editing"));
	} catch (error) {
		log.error("Error editing offline invoice:", error);
	}
}

async function handleDeleteOfflineInvoice(invoiceId) {
	try {
		await offlineStore.deleteOfflineInvoice(invoiceId);
	} catch (error) {
		log.error("Error deleting offline invoice:", error);
	}
}

async function handleSyncClick() {
	if (offlineStore.hasPendingInvoices) {
		await offlineStore.loadPendingInvoices();
		uiStore.showOfflineInvoicesDialog = true;
		return;
	}

	showSuccess(__("No pending invoices to sync"));
}

async function handleSyncAll() {
	if (offlineStore.isOffline) {
		showWarning(__("Cannot sync while offline"));
		return;
	}

	try {
		const result = await offlineStore.syncAllPending();

		// Refresh stock after successful sync (when online)
		if (result.success > 0 && itemsSelectorRef.value) {
			await itemsSelectorRef.value.loadItems();
		}

		if (result.failed > 0 && result.errors && result.errors.length > 0) {
			const firstError = result.errors[0];
			const errorContext = parseError(firstError.error);

			uiStore.showError(
				errorContext.title,
				__(
					"Failed to sync invoice for {0}\n\n${1}\n\nYou can delete this invoice from the offline queue if you don't need it.",
					[firstError.customer, errorContext.message]
				),
				errorContext.technicalDetails || __("Invoice ID: {0}", [firstError.invoiceId]),
				"sync",
				{ failedInvoiceId: firstError.invoiceId }
			);
		} else if (result.failed > 0) {
			showWarning(__("{0} invoice(s) failed to sync", [result.failed]));
		}
	} catch (error) {
		log.error("Sync error:", error);
		const errorContext = parseError(error);
		uiStore.showError(
			errorContext.title,
			errorContext.message,
			errorContext.technicalDetails,
			"sync"
		);
	}
}

// Resizable layout helpers
function updateLayoutBounds() {
	if (!containerRef.value) return;
	const containerWidth = containerRef.value.offsetWidth;
	uiStore.updateLayoutBounds(containerWidth);
}

function startResize(event) {
	if (!containerRef.value || !dividerRef.value) {
		return;
	}
	if (event.isPrimary === false) {
		return;
	}
	if (event.button !== undefined && event.button !== 0 && event.pointerType !== "touch") {
		return;
	}

	updateLayoutBounds();

	resizeState = {
		pointerId: event.pointerId,
		startX: event.clientX,
		startWidth: uiStore.leftPanelWidth,
		containerWidth: containerRef.value?.offsetWidth ?? 1120,
	};

	uiStore.setResizing(true);

	bodyStyleSnapshot = {
		cursor: document.body.style.cursor,
		userSelect: document.body.style.userSelect,
	};

	// Add document-level event listeners for dragging
	document.addEventListener("pointermove", handleResize);
	document.addEventListener("pointerup", stopResize);
	document.addEventListener("pointercancel", stopResize);

	dividerRef.value.setPointerCapture?.(event.pointerId);
	document.body.style.cursor = "col-resize";
	document.body.style.userSelect = "none";
	event.preventDefault();
}

function handleResize(event) {
	if (
		!uiStore.isResizing ||
		!resizeState ||
		(event.pointerId ?? resizeState.pointerId) !== resizeState.pointerId
	) {
		return;
	}

	event.preventDefault();

	const containerWidth = containerRef.value?.offsetWidth ?? resizeState.containerWidth;
	resizeState.containerWidth = containerWidth;

	const deltaX = event.clientX - resizeState.startX;
	// In RTL, dragging right should decrease width, so invert deltaX
	const adjustedDelta = isRTL.value ? -deltaX : deltaX;
	const rawWidth = resizeState.startWidth + adjustedDelta;

	uiStore.setLeftPanelWidth(rawWidth, containerWidth);
}

function stopResize(event) {
	if (!uiStore.isResizing || !resizeState) {
		return;
	}

	if (event?.pointerId !== undefined && event.pointerId !== resizeState.pointerId) {
		return;
	}

	if (event?.preventDefault) {
		event.preventDefault();
	}

	// Remove document-level event listeners
	document.removeEventListener("pointermove", handleResize);
	document.removeEventListener("pointerup", stopResize);
	document.removeEventListener("pointercancel", stopResize);

	if (dividerRef.value?.hasPointerCapture?.(resizeState.pointerId)) {
		dividerRef.value.releasePointerCapture(resizeState.pointerId);
	}

	uiStore.setResizing(false);
	resizeState = null;
	restoreBodyStyles();
	updateLayoutBounds();
}

function restoreBodyStyles() {
	if (!bodyStyleSnapshot) {
		return;
	}

	document.body.style.cursor = bodyStyleSnapshot.cursor || "";
	document.body.style.userSelect = bodyStyleSnapshot.userSelect || "";
	bodyStyleSnapshot = null;
}

// Management and Promotion handlers
function handleExchangeCompleted(result) {
	log.info('Currency exchange completed:', result);
}

function handleManagementMenuClick(menuItem) {
	if (menuItem === "promotions") {
		showPromotionManagement.value = true;
	} else if (menuItem === "reports") {
		showReportsDialog.value = true;
	} else if (menuItem === "settings") {
		showPOSSettings.value = true;
	} else if (menuItem === "invoices") {
		// Load invoice history data before showing
		loadInvoiceHistoryData();
		// Load drafts data
		draftsStore.loadDrafts();
		showInvoiceManagement.value = true;
	} else if (menuItem === "products") {
		// Open Stock Lookup dialog in search mode (only if stock lookup is allowed)
		if (posSettingsStore.allowStockLookup) {
			showStockLookup.value = true;
		}
	} else if (menuItem === "sales-orders") {
		// Open Sales Orders dialog
		showSalesOrdersDialog.value = true;
	} else if (menuItem === "currency-exchange") {
		showCurrencyExchangeDialog.value = true;
	} else if (menuItem === "supplier") {
		// Open unified supplier dialog (selection + payment) only if enabled
		if (posSettingsStore.allowSupplierPayment) {
			showSupplierPaymentDialog.value = true;
		}
	} else if (menuItem === "shift-notes") {
		showShiftNotesDialog.value = true;
	}
}

// Load invoice history data
async function loadInvoiceHistoryData() {
	log.info("Loading invoice history data for profile:", shiftStore.profileName);

	// Also reload drafts
	await draftsStore.loadDrafts();

	try {
		// Use custom API from pos_next.api.invoices
		const result = await call("pos_next.api.invoices.get_invoices", {
			pos_profile: shiftStore.profileName,
			limit: 100,
		});

		invoiceHistoryData.value = result || [];
		log.info("Loaded invoice history:", invoiceHistoryData.value.length, "invoices");
	} catch (error) {
		log.error("Error loading invoice history:", error);
		invoiceHistoryData.value = [];
	}
}

// Handle invoice actions from InvoiceManagement
function handleViewInvoice(invoice) {
	selectedInvoiceForView.value = invoice.name || invoice;
	showInvoiceDetail.value = true;
}

async function handlePrintLastInvoice() {
	if (uiStore.lastInvoiceName) {
		await handlePrintInvoice({ name: uiStore.lastInvoiceName });
	}
}

// Centralized print handler - uses printInvoice.js utilities
async function handlePrintInvoice(invoiceData) {
	try {
		// If invoiceData is a full document with items, use printInvoice directly
		if (invoiceData.items && Array.isArray(invoiceData.items)) {
			await printInvoice(invoiceData);
		} else {
			// If it's just an invoice object with name, fetch and print
			// printInvoiceByName will automatically fetch the print format from the invoice's POS Profile
			await printInvoiceByName(invoiceData.name);
		}
	} catch (error) {
		log.error("Error printing invoice:", error);
		window.frappe?.msgprint({
			title: "Error",
			message: "Failed to print invoice",
			indicator: "red",
		});
	}
}

// Note: handleLoadDraft already exists above, will delegate to it
function handleLoadDraftFromManagement(draft) {
	handleLoadDraft(draft);
	showInvoiceManagement.value = false;
}

function handleDeleteDraft(draftId) {
	draftsStore.deleteDraft(draftId);
}

// Handler for loading sales order into cart
async function handleLoadSalesOrder(order) {
	try {
		// If current cart has items, confirm before replacing
		if (!cartStore.isEmpty) {
			const confirmed = await new Promise((resolve) => {
				window.frappe?.confirm(
					__("Current cart will be cleared. Load sales order {0}?", [order.name]),
					() => resolve(true),
					() => resolve(false)
				);
			});
			if (!confirmed) return;
		}

		// Check if order is in draft status and submit it first
		if (order.status === 'Draft') {
			try {
				const submitResult = await call("pos_next.api.sales_order_utils.submit_sales_order", {
					sales_order_name: order.name
				});
				
				if (submitResult.success) {
					showSuccess(__("Sales order {0} submitted successfully", [order.name]));
					// Update order status in the dialog
					order.status = submitResult.status;
				} else {
					showError(submitResult.message || __("Failed to submit sales order"));
					return;
				}
			} catch (error) {
				console.error("Error submitting sales order:", error);
				showError(error.message || __("Failed to submit sales order"));
				return;
			}
		}

		// Clear current cart
		cartStore.clearCart();

		// Fetch full order details (refresh after submission)
		const orderDetails = await call("pos_next.api.sales_orders.get_sales_order_details", {
			name: order.name,
		});

		// Set customer
		if (orderDetails.customer) {
			const customerData = {
				name: orderDetails.customer,
				customer_name: orderDetails.customer_name || orderDetails.customer,
			};
			cartStore.setCustomer(customerData);
		}

		// Add items to cart
		if (orderDetails.items && orderDetails.items.length > 0) {
			for (const item of orderDetails.items) {
				// Prepare item for cart
				const cartItem = {
					item_code: item.item_code,
					item_name: item.item_name,
					qty: item.qty,
					uom: item.uom,
					rate: item.rate,
					discount_percentage: item.discount_percentage || 0,
					discount_amount: item.discount_amount || 0,
					warehouse: item.warehouse || shiftStore.profileWarehouse,
					is_stock_item: item.is_stock_item,
					has_batch_no: item.has_batch_no,
					has_serial_no: item.has_serial_no,
					// Store sales order reference for linking
					against_sales_order: order.name,
					so_detail: item.so_detail,
				};

				try {
					cartStore.addItem(cartItem, item.qty, true, shiftStore.currentProfile);
				} catch (error) {
					console.warn("Failed to add item:", item.item_code, error);
				}
			}
		}

		// Apply additional discount if any
		if (orderDetails.discount_amount && orderDetails.discount_amount > 0) {
			cartStore.additionalDiscount = orderDetails.discount_amount;
			cartStore.rebuildIncrementalCache();
		}

		showSuccess(__("Sales order {0} loaded successfully", [order.name]));
	} catch (error) {
		console.error("Error loading sales order:", error);
		showError(error.message || __("Failed to load sales order"));
	}
}

async function handleWarehouseChanged(newWarehouse) {
	log.info("Warehouse changed to:", newWarehouse);

	try {
		// Update the shift store with new warehouse
		if (shiftStore.currentProfile) {
			shiftStore.currentProfile.warehouse = newWarehouse;
		}

		// Clear item search cache to force reload from new warehouse
		itemStore.invalidateCache();

		// Reload items with new warehouse stock quantities
		if (itemsSelectorRef.value) {
			await itemsSelectorRef.value.loadItems();
		}

		showSuccess(__("Switched to {0}. Stock quantities refreshed.", [newWarehouse]));
	} catch (error) {
		log.error("Error handling warehouse change:", error);
		showWarning(__("Warehouse updated but failed to reload stock. Please refresh manually."));
	}
}

function handlePromotionSaved(data) {
	showSuccess(data.message || __("Promotion saved successfully"));
}
function handleCustomerPayment(customer) {
	console.log("=== Customer Payment Clicked ===", customer);
	cartStore.setCustomer(customer);
	console.log("Setting dialog to true, current value:", showCustomerPaymentDialog.value);
	showCustomerPaymentDialog.value = true;
	console.log("Dialog should now be visible");
}

function handleCustomerPaymentCreated(result) {
	showSuccess(__("Payment completed and balance updated"));
}

function handleSupplierPaymentCreated(result) {
	showSuccess(__("Supplier payment created: {0}", [result?.payment_entry || result?.name]));
	showSupplierPaymentDialog.value = false;
}

// Optimized tab switching for mobile with RAF for smooth transitions
function handleTabSwitch(tab) {
	// Use requestAnimationFrame to ensure smooth transitions
	requestAnimationFrame(() => {
		uiStore.setMobileTab(tab);
	});
}
</script>
