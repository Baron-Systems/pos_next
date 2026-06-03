/**
 * Composable for favorite/pinned items in POS.
 * Persists item codes in localStorage so favorites appear first and can be toggled per item.
 */
import { ref, computed, onMounted } from "vue"

const STORAGE_KEY = "pos_next_favorite_items"

const favoriteCodes = ref(new Set())

function load() {
	if (typeof window === "undefined" || !window.localStorage) return
	try {
		const raw = localStorage.getItem(STORAGE_KEY)
		if (raw) {
			const arr = JSON.parse(raw)
			favoriteCodes.value = new Set(Array.isArray(arr) ? arr : [])
		}
	} catch (_) {
		favoriteCodes.value = new Set()
	}
}

function save() {
	if (typeof window === "undefined" || !window.localStorage) return
	try {
		localStorage.setItem(STORAGE_KEY, JSON.stringify([...favoriteCodes.value]))
	} catch (_) {}
}

/**
 * @returns { { isFavorite: (itemCode: string) => boolean, toggleFavorite: (itemCode: string) => void, favoriteItemCodes: import('vue').Ref<Set<string>> } }
 */
export function useFavoriteItems() {
	load() // load once so favorites are available before first render
	onMounted(load)

	const isFavorite = (itemCode) => Boolean(itemCode && favoriteCodes.value.has(itemCode))

	const toggleFavorite = (itemCode) => {
		if (!itemCode) return
		if (favoriteCodes.value.has(itemCode)) {
			favoriteCodes.value.delete(itemCode)
			favoriteCodes.value = new Set(favoriteCodes.value)
		} else {
			favoriteCodes.value.add(itemCode)
			favoriteCodes.value = new Set(favoriteCodes.value)
		}
		save()
	}

	const favoriteItemCodes = computed(() => favoriteCodes.value)

	return {
		isFavorite,
		toggleFavorite,
		favoriteItemCodes,
	}
}
