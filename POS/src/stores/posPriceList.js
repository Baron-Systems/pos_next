import { defineStore } from "pinia"
import { computed, ref } from "vue"
import { logger } from "@/utils/logger"

const log = logger.create("PriceList")

const STORAGE_KEY = "pos_selected_price_list"

function getStorageKey(profileName) {
	return profileName ? `${STORAGE_KEY}_${profileName}` : STORAGE_KEY
}

export const usePOSPriceListStore = defineStore("posPriceList", () => {
	// State
	const allowedPriceLists = ref([])
	const selectedPriceList = ref(null)
	const defaultPriceList = ref(null)
	const loaded = ref(false)

	// Computed
	const hasMultiplePriceLists = computed(() => allowedPriceLists.value.length > 1)
	const priceListOptions = computed(() => allowedPriceLists.value)
	const activePriceList = computed(
		() => selectedPriceList.value || defaultPriceList.value || null
	)

	/**
	 * Load allowed price lists from bootstrap data and resolve the active one.
	 * The last selected price list is persisted per POS profile in localStorage.
	 */
	async function loadPriceLists(profileName) {
		const { useBootstrapStore } = await import("@/stores/bootstrap")
		const bootstrapStore = useBootstrapStore()

		if (!bootstrapStore.loaded) {
			try {
				await bootstrapStore.loadInitialData()
			} catch (error) {
				log.error("Failed to load bootstrap data for price lists", error)
			}
		}

		allowedPriceLists.value = bootstrapStore.getPreloadedAllowedPriceLists() || []
		defaultPriceList.value = bootstrapStore.getPreloadedDefaultPriceList() || null

		if (allowedPriceLists.value.length === 0 && defaultPriceList.value) {
			// Fallback: create a single option from the legacy default price list
			allowedPriceLists.value = [
				{ price_list: defaultPriceList.value, is_default: 1 },
			]
		}

		const savedPriceList = localStorage.getItem(getStorageKey(profileName))
		const priceListNames = new Set(
			allowedPriceLists.value.map((row) => row.price_list)
		)

		if (savedPriceList && priceListNames.has(savedPriceList)) {
			selectedPriceList.value = savedPriceList
		} else {
			selectedPriceList.value = defaultPriceList.value
		}

		loaded.value = true
		log.info("Price lists loaded", {
			allowed: allowedPriceLists.value.map((r) => r.price_list),
			active: activePriceList.value,
		})
	}

	/**
	 * Set the active price list and persist it for the current POS profile.
	 */
	function setSelectedPriceList(priceList, profileName) {
		selectedPriceList.value = priceList || defaultPriceList.value
		if (profileName) {
			localStorage.setItem(getStorageKey(profileName), selectedPriceList.value || "")
		}
		log.info("Price list changed", { priceList: selectedPriceList.value })
	}

	/**
	 * Reset state (e.g. on logout or shift close).
	 */
	function reset() {
		allowedPriceLists.value = []
		selectedPriceList.value = null
		defaultPriceList.value = null
		loaded.value = false
	}

	return {
		allowedPriceLists,
		selectedPriceList,
		defaultPriceList,
		loaded,
		hasMultiplePriceLists,
		priceListOptions,
		activePriceList,
		loadPriceLists,
		setSelectedPriceList,
		reset,
	}
})
