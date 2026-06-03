<template>
	<Dialog v-model="show" :options="{ title: isEditMode ? __('Edit Customer') : __('Create New Customer'), size: 'md' }">
		<template #body-content>
			<div class="flex flex-col gap-6">
				<!-- Customer Name (Required) -->
				<div>
					<label class="block text-start text-sm font-medium text-gray-700 mb-2">
						{{ __("Customer Name") }} <span class="text-red-500">*</span>
					</label>
					<Input
						v-model="customerData.customer_name"
						type="text"
						:placeholder="__('Enter customer name')"
						required
					/>
				</div>

				<!-- Mobile Number with Country Code Selector -->
				<div>
					<label class="block text-start text-sm font-medium text-gray-700 mb-2">
						{{ __("Mobile Number") }}
					</label>
					<div class="flex gap-2">
						<!-- Country Code Dropdown -->
						<div class="relative" ref="dropdownRef">
							<button
								type="button"
								@click="showCountryDropdown = !showCountryDropdown"
								class="flex items-center gap-1 w-24 ps-2 pe-1 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white hover:bg-gray-50"
							>
								<img
									:src="`https://flagcdn.com/h24/${currentCountryCode}.png`"
									:alt="currentCountryCode"
									class="w-6 h-auto rounded-sm"
									@error="handleFlagError"
								/>
								<span class="flex-1 text-start">{{ selectedCountryCode || "+20" }}</span>
								<svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
								</svg>
							</button>

							<!-- Country Search Dropdown -->
							<div
								v-if="showCountryDropdown"
								class="absolute start-0 z-50 mt-1 w-80 max-h-80 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden"
							>
								<div class="sticky top-0 bg-white border-b border-gray-200 p-2">
									<input
										ref="countrySearchRef"
										v-model="countrySearchQuery"
										type="text"
										:placeholder="__('Search country or code...')"
										class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
										@keydown.escape="showCountryDropdown = false"
									/>
								</div>
								<div class="overflow-y-auto max-h-64">
									<button
										v-for="country in filteredCountries"
										:key="country.code"
										type="button"
										@click="selectCountry(country)"
										class="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-gray-50 transition-colors text-start"
										:class="{ 'bg-blue-50': selectedCountryCode === country.isd }"
									>
										<img
											:src="`https://flagcdn.com/h24/${country.code.toLowerCase()}.png`"
											:alt="country.name"
											class="w-6 h-auto rounded-sm shadow-sm"
											@error="(e) => (e.target.style.display = 'none')"
										/>
										<span class="flex-1 text-sm font-medium text-gray-700">{{ country.name }}</span>
										<span class="text-sm text-gray-500">{{ country.isd }}</span>
									</button>
									<div v-if="filteredCountries.length === 0" class="px-4 py-8 text-center text-sm text-gray-500">
										{{ __("No countries found") }}
									</div>
								</div>
							</div>
						</div>

						<!-- Phone Number Input -->
						<input
							v-model="phoneNumber"
							type="tel"
							:placeholder="__('Enter phone number')"
							class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-start"
							@input="updateMobileNumber"
						/>
					</div>
					<!-- Debug info (remove in production) -->
					<div v-if="showDebugInfo" class="text-xs text-gray-400 mt-1">
						ISD: {{ selectedCountryCode }} | Number: {{ phoneNumber }} | Full: {{ customerData.mobile_no }}
					</div>
				</div>

				<!-- Email -->
				<div>
					<label class="block text-start text-sm font-medium text-gray-700 mb-2">
						{{ __("Email") }}
					</label>
					<Input v-model="customerData.email_id" type="email" :placeholder="__('Enter email address')" />
				</div>

				<!-- Customer Group -->
				<div>
					<label class="block text-start text-sm font-medium text-gray-700 mb-2">
						{{ __("Customer Group") }}
					</label>
					<select
						v-model="customerData.customer_group"
						class="w-full px-8 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					>
						<option value="">{{ __("Select Customer Group") }}</option>
						<option v-for="group in customerGroups" :key="group" :value="group">
							{{ group }}
						</option>
					</select>
				</div>

				<!-- Territory -->
				<div>
					<label class="block text-start text-sm font-medium text-gray-700 mb-2">
						{{ __("Territory") }}
					</label>
					<select
						v-model="customerData.territory"
						class="w-full px-8 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					>
						<option value="">{{ __("Select Territory") }}</option>
						<option v-for="territory in territories" :key="territory" :value="territory">
							{{ territory }}
						</option>
					</select>
				</div>
			</div>
		</template>

		<template #actions>
			<div class="flex flex-col gap-2">
				<!-- Permission Warning -->
				<div v-if="!hasPermission" class="px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg">
					<div class="flex items-start gap-2">
						<svg class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
								clip-rule="evenodd"
							/>
						</svg>
						<div class="flex-1">
							<p class="text-sm font-medium text-amber-900">{{ __("Permission Required") }}</p>
							<p class="text-xs text-amber-700 mt-0.5">
								{{ __("You don't have permission to create customers. Contact your administrator.") }}
							</p>
						</div>
					</div>
				</div>

				<div class="flex gap-2">
					<Button
						variant="solid"
						@click="handleSubmit"
						:loading="createCustomerResource.loading || updateCustomerResource.loading || checkingPermission"
						:disabled="!customerData.customer_name || !hasPermission"
					>
						{{ isEditMode ? __("Save Changes") : __("Create Customer") }}
					</Button>
					<Button variant="subtle" @click="handleCancel">
						{{ __("Cancel") }}
					</Button>
				</div>

				<!-- Debug Toggle (remove in production) -->
				<button
					@click="showDebugInfo = !showDebugInfo"
					class="text-xs text-gray-400 hover:text-gray-600"
					type="button"
				>
					{{ showDebugInfo ? __('Hide Debug') : __('Show Debug') }}
				</button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
/**
 * CreateCustomerDialog v2.0 - Enhanced with Contact Integration
 *
 * Features:
 * - Synchronized Customer + Contact updates
 * - Smart phone number parsing with auto country detection
 * - Comprehensive logging for debugging
 * - Race condition protection
 * - Backward compatible
 */

import { usePOSPermissions } from "@/composables/usePermissions"
import { useToast } from "@/composables/useToast"
import { useCountriesStore } from "@/stores/countries"
import { logger } from "@/utils/logger"
import { parsePhoneNumber, formatPhoneNumber, detectCountryCode, extractLocalNumber, extractCountryCode } from "@/utils/phoneNumber"
import { Button, Dialog, Input, createResource } from "frappe-ui"
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue"

const log = logger.create("CreateCustomerDialog")

// =============================================================================
// Composables & Stores
// =============================================================================

const countriesStore = useCountriesStore()
const { canCreateCustomer } = usePOSPermissions()
const { showSuccess, showError } = useToast()

// =============================================================================
// Props & Emits
// =============================================================================

const props = defineProps({
	modelValue: Boolean,
	posProfile: String,
	initialName: String,
	customer: Object, // Customer object for edit mode
})

const emit = defineEmits(["update:modelValue", "customer-created", "customer-updated"])

// =============================================================================
// State
// =============================================================================

const hasPermission = ref(true)
const checkingPermission = ref(false)
const selectedCountryCode = ref("")
const phoneNumber = ref("")
const showCountryDropdown = ref(false)
const countrySearchQuery = ref("")
const dropdownRef = ref(null)
const countrySearchRef = ref(null)
const showDebugInfo = ref(false)
const isSubmitting = ref(false)

// Prevent race conditions
const isLoadingCustomerData = ref(false)

const customerGroups = ref(["Commercial", "Individual", "Non Profit", "Government"])
const territories = ref(["All Territories"])

const customerData = ref({
	customer_name: "",
	mobile_no: "",
	email_id: "",
	customer_group: "Individual",
	territory: "All Territories",
})

// Store original values for comparison
const originalCustomerData = ref(null)

// =============================================================================
// Computed
// =============================================================================

const show = computed({
	get: () => props.modelValue,
	set: (val) => emit("update:modelValue", val),
})

const isEditMode = computed(() => !!props.customer?.name)

const currentCountryCode = computed(() => {
	const country = countriesStore.countries.find((c) => c.isd === selectedCountryCode.value)
	return country?.code.toLowerCase() || "eg"
})

const filteredCountries = computed(() => {
	if (!countrySearchQuery.value) return countriesStore.countries

	const query = countrySearchQuery.value.toLowerCase()
	return countriesStore.countries.filter(
		(c) =>
			c.name.toLowerCase().includes(query) ||
			c.isd.includes(query) ||
			c.code.toLowerCase().includes(query)
	)
})

// =============================================================================
// Country & Territory Methods
// =============================================================================

const handleFlagError = (e) => (e.target.style.display = "none")

const selectCountry = (country) => {
	log.info(`Country selected: ${country.name} (${country.isd})`)
	selectedCountryCode.value = country.isd
	showCountryDropdown.value = false
	countrySearchQuery.value = ""
	updateMobileNumber()
}

const updateMobileNumber = () => {
	const oldValue = customerData.value.mobile_no
	customerData.value.mobile_no = formatPhoneNumber(selectedCountryCode.value, phoneNumber.value)
	log.debug(`Mobile number updated: ${oldValue} -> ${customerData.value.mobile_no}`)
}

const handleClickOutside = (event) => {
	if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
		showCountryDropdown.value = false
		countrySearchQuery.value = ""
	}
}

const setCountryFromName = (countryName) => {
	if (!countryName) {
		selectedCountryCode.value = "+20"
		return
	}

	const isd = countriesStore.countryNameToISDMap[countryName]
	if (isd) {
		selectedCountryCode.value = isd
		log.info(`Set country code to ${isd} for ${countryName}`)
	} else {
		log.warn(`Country "${countryName}" not found, defaulting to +20`)
		selectedCountryCode.value = "+20"
	}
}

/** Auto-set territory based on selected country (exact or fuzzy match) */
const updateTerritoryFromCountry = () => {
	if (!territories.value.length) return

	const country = countriesStore.countries.find((c) => c.isd === selectedCountryCode.value)
	if (!country) return

	// Try exact match first
	if (territories.value.includes(country.name)) {
		customerData.value.territory = country.name
		log.info(`Territory set to: ${country.name}`)
		return
	}

	// Try fuzzy match
	const fuzzyMatch = territories.value.find(
		(t) =>
			t.toLowerCase().includes(country.name.toLowerCase()) ||
			country.name.toLowerCase().includes(t.toLowerCase())
	)

	if (fuzzyMatch) {
		customerData.value.territory = fuzzyMatch
		log.info(`Territory set to fuzzy match: ${fuzzyMatch}`)
	}
}

// =============================================================================
// Customer Data Loading (Edit Mode)
// =============================================================================

/**
 * Load customer data for editing
 * This is the critical fix - properly parse phone numbers in all formats
 */
const loadCustomerData = async (customer) => {
	if (!customer?.name) {
		log.warn("No customer data provided for edit mode")
		return
	}

	isLoadingCustomerData.value = true
	log.info(`Loading customer data for: ${customer.name}`, customer)

	try {
		// Fetch fresh customer data to ensure we have latest email, phone, etc.
		let freshCustomer = customer
		try {
			const { call } = await import("frappe-ui")
			const result = await call("frappe.client.get", {
				doctype: "Customer",
				name: customer.name,
			})
			if (result) {
				freshCustomer = result
				log.info(`Fetched fresh customer data:`, freshCustomer)
			}
		} catch (fetchError) {
			log.warn(`Could not fetch fresh customer data, using cached: ${fetchError.message}`)
		}

		// Set basic customer info from fresh data
		customerData.value.customer_name = freshCustomer.customer_name || ""
		customerData.value.email_id = freshCustomer.email_id || ""
		customerData.value.customer_group = freshCustomer.customer_group || "Individual"
		customerData.value.territory = freshCustomer.territory || "All Territories"

		// Handle phone number parsing from fresh data
		const mobileNo = freshCustomer.mobile_no || ""
		log.info(`Parsing mobile_no: "${mobileNo}"`)

		if (mobileNo) {
			// Use smart phone number parser
			const parsed = parsePhoneNumber(mobileNo)
			log.info(`Parsed phone result:`, parsed)

			if (parsed.isd) {
				// Number had country code
				selectedCountryCode.value = parsed.isd
				phoneNumber.value = parsed.number
				customerData.value.mobile_no = parsed.fullNumber
				log.info(`Set phone: ISD=${parsed.isd}, Number=${parsed.number}`)
			} else {
				// Number without country code - try to detect or use default
				const detectedISD = detectCountryCode(mobileNo)
				if (detectedISD) {
					selectedCountryCode.value = detectedISD
					phoneNumber.value = parsed.number
					log.info(`Detected country code: ${detectedISD}`)
				} else {
					// Use default from POS Profile or +20
					await setDefaultCountryFromProfile()
					phoneNumber.value = parsed.number
					log.info(`Using default country code: ${selectedCountryCode.value}`)
				}
			}
		} else {
			// No phone number - set default country
			await setDefaultCountryFromProfile()
			phoneNumber.value = ""
			log.info("No phone number, set default country")
		}

		// Store original data for comparison
		originalCustomerData.value = { ...customerData.value }

		log.info(`Customer data loaded successfully for: ${customer.name}`)
	} catch (error) {
		log.error("Error loading customer data:", error)
		showError(__("Error loading customer data"))
	} finally {
		isLoadingCustomerData.value = false
	}
}

const setDefaultCountryFromProfile = async () => {
	if (props.posProfile) {
		try {
			const result = await posProfileResource.reload()
			// setCountryFromName will set selectedCountryCode
		} catch (err) {
			selectedCountryCode.value = "+20"
		}
	} else {
		selectedCountryCode.value = "+20"
	}
}

// =============================================================================
// API Resources - Using new Contact-integrated endpoints
// =============================================================================

/**
 * Create customer with Contact synchronization (ERPNext v16 compatible)
 * Uses phone_nos child table for storing phone numbers
 */
const createCustomerResource = createResource({
	url: "pos_next.api.customer_contact_v16.create_customer_v16_api",
	makeParams: () => {
		const params = {
			customer_name: customerData.value.customer_name,
			mobile_no: customerData.value.mobile_no,
			email_id: customerData.value.email_id || "",
			customer_group: customerData.value.customer_group || "Individual",
			territory: customerData.value.territory || "All Territories",
			company: null, // Could be added from POS Profile
		}
		log.info("Create customer v16 params:", params)
		return params
	},
	onSuccess: (data) => {
		log.info("Customer created successfully (v16):", data)
		if (data.contact) {
			log.info("Contact created with phone_nos:", data.contact.phone_nos)
		}
		showSuccess(__("Customer {0} created successfully", [data.customer_name]))
		emit("customer-created", data)
		resetForm()
		show.value = false
	},
	onError: (error) => {
		log.error("Error creating customer v16:", error)
		showError(error.message || __("Failed to create customer"))
	},
})

/**
 * Update customer with Contact synchronization (ERPNext v16 compatible)
 * Uses phone_nos child table for updating phone numbers
 */
const updateCustomerResource = createResource({
	url: "pos_next.api.customer_contact_v16.update_customer_v16_api",
	makeParams: () => {
		const params = {
			customer_id: props.customer?.name,
			customer_name: customerData.value.customer_name,
			mobile_no: customerData.value.mobile_no,
			email_id: customerData.value.email_id || "",
			customer_group: customerData.value.customer_group || "Individual",
			territory: customerData.value.territory || "All Territories",
		}
		log.info("Update customer v16 params:", params)
		return params
	},
	onSuccess: (data) => {
		log.info("Customer updated successfully (v16):", data)
		if (data.contact) {
			log.info("Contact updated with phone_nos:", data.contact.phone_nos)
		}
		showSuccess(__("Customer {0} updated successfully", [data.customer_name]))
		emit("customer-updated", data)
		resetForm()
		show.value = false
	},
	onError: (error) => {
		log.error("Error updating customer v16:", error)
		showError(error.message || __("Failed to update customer"))
	},
})

/** Helper to create list fetch resources */
const createListResource = (doctype, onSuccess) =>
	createResource({
		url: "frappe.client.get_list",
		makeParams: () => ({
			doctype,
			fields: ["name"],
			filters: doctype === "Customer Group" ? { is_group: 0 } : {},
			limit_page_length: 500,
		}),
		auto: false,
		onSuccess: (data) => data?.length && onSuccess(data.map((d) => d.name)),
		onError: (err) => log.error(`Error loading ${doctype}`, err),
	})

const customerGroupsResource = createListResource("Customer Group", (names) => (customerGroups.value = names))
const territoriesResource = createListResource("Territory", (names) => (territories.value = names))

const posProfileResource = createResource({
	url: "frappe.client.get_value",
	makeParams: () => ({
		doctype: "POS Profile",
		filters: { name: props.posProfile },
		fieldname: ["country"],
	}),
	auto: false,
	onSuccess: (data) => {
		setCountryFromName(data?.country || "Egypt")
		log.info(`POS Profile country loaded: ${data?.country || "Egypt"}`)
	},
	onError: (err) => {
		log.error("Error loading POS Profile:", err)
		selectedCountryCode.value = "+20"
	},
})

// =============================================================================
// Dialog Lifecycle
// =============================================================================

const loadDialogData = async () => {
	log.info("Loading dialog data...")

	// Lazy load countries (non-blocking)
	countriesStore.loadCountries()

	// Load form options
	await Promise.all([territoriesResource.fetch(), customerGroupsResource.fetch()])

	// Check permissions
	await checkPermissions()

	// Set country from POS Profile (or edit mode customer)
	if (isEditMode.value && props.customer) {
		// In edit mode, customer data loading is handled by loadCustomerData
		await loadCustomerData(props.customer)
	} else if (props.posProfile) {
		await posProfileResource.fetch()
	} else {
		selectedCountryCode.value = "+20"
	}

	log.info("Dialog data loading completed")
}

const checkPermissions = async () => {
	checkingPermission.value = true
	try {
		hasPermission.value = await canCreateCustomer()
		log.info(`Permission check result: ${hasPermission.value}`)
	} catch (err) {
		log.error("Permission check failed:", err)
		hasPermission.value = false
	} finally {
		checkingPermission.value = false
	}
}

const handleSubmit = async () => {
	// Prevent double submission
	if (isSubmitting.value) {
		log.warn("Submission already in progress, ignoring")
		return
	}

	if (!customerData.value.customer_name) {
		return showError(__("Customer Name is required"))
	}

	// Validate phone if provided
	if (customerData.value.mobile_no) {
		const parsed = parsePhoneNumber(customerData.value.mobile_no)
		if (!parsed.isValid) {
			log.warn(`Invalid phone number: ${customerData.value.mobile_no}`)
			// Don't block - just warn
		}
	}

	isSubmitting.value = true
	log.info(`Submitting customer form - Mode: ${isEditMode.value ? 'EDIT' : 'CREATE'}`, customerData.value)

	try {
		if (isEditMode.value) {
			await updateCustomerResource.submit()
		} else {
			await createCustomerResource.submit()
		}
	} catch (error) {
		log.error("Form submission failed:", error)
	} finally {
		isSubmitting.value = false
	}
}

const handleCancel = () => {
	log.info("Dialog cancelled by user")
	resetForm()
	show.value = false
}

const resetForm = () => {
	log.info("Resetting form...")

	// Don't reset if we're in the middle of loading
	if (isLoadingCustomerData.value) {
		log.warn("Skipping reset - customer data is loading")
		return
	}

	customerData.value = {
		customer_name: "",
		mobile_no: "",
		email_id: "",
		customer_group: "Individual",
		territory: "All Territories",
	}

	// Only reset country code if not in edit mode
	if (!isEditMode.value) {
		selectedCountryCode.value = "+20"
	}

	phoneNumber.value = ""
	originalCustomerData.value = null

	log.info("Form reset completed")
}

// =============================================================================
// Watchers - Carefully ordered to prevent race conditions
// =============================================================================

// Watch initial name (for create mode)
watch(
	() => props.initialName,
	(name) => {
		if (name && !isEditMode.value) {
			log.info(`Setting initial customer name: ${name}`)
			customerData.value.customer_name = name
		}
	}
)

// Watch customer prop changes (edit mode) - NOT immediate to prevent race
watch(
	() => props.customer,
	(newCustomer, oldCustomer) => {
		// Only reload if customer actually changed
		if (newCustomer?.name && newCustomer.name !== oldCustomer?.name) {
			log.info(`Customer prop changed: ${newCustomer.name}`)
			loadCustomerData(newCustomer)
		}
	},
	{ immediate: false } // Changed from true to prevent race condition
)

// Watch dialog open/close
watch(
	() => props.modelValue,
	async (isOpen) => {
		show.value = isOpen
		if (isOpen) {
			log.info("Dialog opened")
			await loadDialogData()
		} else {
			log.info("Dialog closed")
			// Delay reset to allow animations to complete
			setTimeout(() => resetForm(), 300)
		}
	}
)

// Watch show for two-way binding
watch(show, (val) => emit("update:modelValue", val))

// Watch country code changes for territory auto-selection
watch(selectedCountryCode, async () => {
	await nextTick()
	updateTerritoryFromCountry()
})

// Watch country dropdown for focus management
watch(showCountryDropdown, async (isOpen) => {
	if (isOpen) {
		await nextTick()
		countrySearchRef.value?.focus()
	}
})

// =============================================================================
// Lifecycle Hooks
// =============================================================================

onMounted(() => {
	log.info("Component mounted")
	document.addEventListener("click", handleClickOutside)
})

onBeforeUnmount(() => {
	log.info("Component unmounting")
	document.removeEventListener("click", handleClickOutside)
})
</script>

<style scoped>
.sr-only {
	position: absolute;
	width: 1px;
	height: 1px;
	padding: 0;
	margin: -1px;
	overflow: hidden;
	clip: rect(0, 0, 0, 0);
	white-space: nowrap;
	border-width: 0;
}
</style>
