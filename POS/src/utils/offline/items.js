import { db, getSetting, setSetting } from "./db";

// Bump this when the shape of cached item data changes (e.g. new barcode_uoms field)
export const CACHE_DATA_VERSION = 2

export const isCacheDataVersionCurrent = async () => {
	const v = await getSetting("cache_data_version", 0)
	return v >= CACHE_DATA_VERSION
}

export const setCacheDataVersion = async (version = CACHE_DATA_VERSION) => {
	await setSetting("cache_data_version", version)
}

// Cache items in IndexedDB
export const cacheItems = async (items, priceList = null) => {
	try {
		if (!items || items.length === 0) return;

		const extractBarcodes = (item) => {
			if (Array.isArray(item.barcodes)) {
				return item.barcodes
					.map((b) => (typeof b === "object" && b ? b.barcode : b))
					.filter(Boolean);
			}
			if (item.barcode) return [item.barcode];
			if (item.item_barcode) {
				if (Array.isArray(item.item_barcode)) {
					return item.item_barcode
						.map((b) => (typeof b === "object" && b ? b.barcode : b))
						.filter(Boolean);
				}
				return [item.item_barcode];
			}
			return [];
		};

		const extractBarcodeUoms = (item) => {
			const uoms = { ...(item.barcode_uoms || {}) };
			if (Array.isArray(item.barcodes)) {
				item.barcodes.forEach((b) => {
					if (b && typeof b === "object" && b.barcode) {
						uoms[b.barcode] = b.uom || item.stock_uom;
					}
				});
			}
			return uoms;
		};

		// Process items with barcodes and UOM mapping
		const processedItems = items.map((item) => ({
			...item,
			barcodes: extractBarcodes(item),
			barcode_uoms: extractBarcodeUoms(item),
		}));

		// Save to items table
		await db.items.bulkPut(processedItems);

		// Save prices if price list is provided
		if (priceList) {
			const prices = items.map((item) => ({
				price_list: priceList,
				item_code: item.item_code,
				rate: item.rate || item.price_list_rate || 0,
				timestamp: Date.now(),
			}));
			await db.item_prices.bulkPut(prices);
		}

		// Update last sync time
		await setSetting("items_last_sync", Date.now());

		console.log(`Cached ${items.length} items`);
		return true;
	} catch (error) {
		console.error("Error caching items:", error);
		return false;
	}
};

// Get cached items
export const getCachedItems = async (limit = 100) => {
	try {
		const items = await db.items.limit(limit).toArray();
		return items;
	} catch (error) {
		console.error("Error getting cached items:", error);
		return [];
	}
};

// Fuzzy search: matches if any search word is contained in item text
export const searchCachedItems = async (searchTerm, limit = 50) => {
	try {
		if (!searchTerm) {
			return await db.items.limit(limit).toArray();
		}

		const term = searchTerm.toLowerCase().trim();
		const searchWords = term.split(/\s+/).filter(Boolean);
		const allItems = await db.items.limit(limit * 10).toArray();

		// Filter and score items
		const results = allItems
			.map((item) => {
				const searchable = `${item.item_code || ""} ${item.item_name || ""} ${item.description || ""}`.toLowerCase();

				// Word-order independent: all words must appear somewhere
				if (!searchWords.every(word => searchable.includes(word))) return null;

				// Score: prefer exact and prefix matches
				let score = 0;
				if (item.item_name?.toLowerCase() === term) score = 1000;
				else if (item.item_code?.toLowerCase() === term) score = 900;
				else if (item.item_name?.toLowerCase().startsWith(term)) score = 500;
				else if (item.item_code?.toLowerCase().startsWith(term)) score = 400;
				else score = 100;

				return { item, score };
			})
			.filter(Boolean)
			.sort((a, b) => b.score - a.score)
			.slice(0, limit)
			.map(({ item }) => item);

		return results;
	} catch (error) {
		console.error("Error searching cached items:", error);
		return [];
	}
};

// Get item by barcode
export const getItemByBarcode = async (barcode) => {
	try {
		const item = await db.items.where("barcodes").equals(barcode).first();
		return item;
	} catch (error) {
		console.error("Error getting item by barcode:", error);
		return null;
	}
};

// Get cached variants for a template item
export const getCachedVariants = async (templateItemCode) => {
	try {
		if (!templateItemCode) return [];

		// Query items where variant_of equals the template item code
		const variants = await db.items
			.where("variant_of")
			.equals(templateItemCode)
			.toArray();

		return variants;
	} catch (error) {
		console.error("Error getting cached variants:", error);
		return [];
	}
};

// Get item with price
export const getItemWithPrice = async (itemCode, priceList) => {
	try {
		const item = await db.items.get(itemCode);
		if (!item) return null;

		if (priceList) {
			const price = await db.item_prices.get({
				price_list: priceList,
				item_code: itemCode,
			});
			if (price) {
				item.rate = price.rate;
				item.price_list_rate = price.rate;
			}
		}

		return item;
	} catch (error) {
		console.error("Error getting item with price:", error);
		return null;
	}
};

// Cache customers
export const cacheCustomers = async (customers) => {
	try {
		if (!customers || customers.length === 0) return;

		await db.customers.bulkPut(customers);
		await setSetting("customers_last_sync", Date.now());

		console.log(`Cached ${customers.length} customers`);
		return true;
	} catch (error) {
		console.error("Error caching customers:", error);
		return false;
	}
};

// Search cached customers
export const searchCachedCustomers = async (searchTerm, limit = 20) => {
        try {
                if (!searchTerm) {
                        return limit > 0
                                ? await db.customers.limit(limit).toArray()
                                : await db.customers.toArray();
                }

		const term = searchTerm.toLowerCase();

                const query = db.customers
                        .where("customer_name")
                        .startsWithIgnoreCase(term)
                        .or("mobile_no")
                        .startsWithIgnoreCase(term)
                        .or("email_id")
                        .startsWithIgnoreCase(term);

                const results = await (limit > 0
                        ? query.limit(limit).toArray()
                        : query.toArray());

		return results;
	} catch (error) {
		console.error("Error searching cached customers:", error);
		return [];
	}
};

// Get items last sync time
export const getItemsLastSync = async () => {
	return await getSetting("items_last_sync", null);
};

// Get customers last sync time
export const getCustomersLastSync = async () => {
	return await getSetting("customers_last_sync", null);
};

// Check if cache is fresh (less than 24 hours old)
export const isCacheFresh = async (type = "items") => {
	const lastSync = type === "items" ? await getItemsLastSync() : await getCustomersLastSync();

	if (!lastSync) return false;

	const hoursSinceSync = (Date.now() - lastSync) / (1000 * 60 * 60);
	return hoursSinceSync < 24;
};

// Clear cache
export const clearItemsCache = async () => {
	try {
		await db.items.clear();
		await db.item_prices.clear();
		await setSetting("items_last_sync", null);
		console.log("Items cache cleared");
		return true;
	} catch (error) {
		console.error("Error clearing items cache:", error);
		return false;
	}
};

export const clearCustomersCache = async () => {
	try {
		await db.customers.clear();
		await setSetting("customers_last_sync", null);
		console.log("Customers cache cleared");
		return true;
	} catch (error) {
		console.error("Error clearing customers cache:", error);
		return false;
	}
};

// RLS1100C scale barcode (EAN-13 with weight) support
const SCALE_BARCODE_PREFIXES = ["02", "21"];
const SCALE_BARCODE_LEN = 13;
const SCALE_PLU_START = 2;
const SCALE_PLU_LEN = 5;
const SCALE_WEIGHT_START = 7;
const SCALE_WEIGHT_LEN = 5;

function computeEAN13CheckDigit(first12) {
	let s = 0;
	for (let i = 0; i < 12; i++) {
		const d = Number.parseInt(first12[i], 10);
		if ((11 - i) % 2 === 0) {
			s += d;
		} else {
			s += d * 3;
		}
	}
	return (10 - (s % 10)) % 10;
}

export const parseScaleBarcode = (barcode) => {
	const b = (barcode || "").trim();
	if (b.length !== SCALE_BARCODE_LEN || !/^\d+$/.test(b)) return null;
	const prefix = SCALE_BARCODE_PREFIXES.find((p) => b.startsWith(p));
	if (!prefix) return null;
	const plu = b.slice(SCALE_PLU_START, SCALE_PLU_START + SCALE_PLU_LEN);
	const weightStr = b.slice(SCALE_WEIGHT_START, SCALE_WEIGHT_START + SCALE_WEIGHT_LEN);
	const weightGrams = Number.parseInt(weightStr, 10) || 0;
	const base12 = prefix + plu + "0".repeat(SCALE_WEIGHT_LEN);
	const check = computeEAN13CheckDigit(base12);
	const baseBarcode = base12 + String(check);
	return {
		plu,
		weightGrams,
		baseBarcode,
		weightKgs: weightGrams / 1000,
	};
};

function buildUomItem(item, matchedBarcode, weightKgs) {
	const stockUom = item.stock_uom;
	const uom = item.barcode_uoms?.[matchedBarcode] || stockUom;
	let conversionFactor = 1;
	if (uom && uom !== stockUom) {
		const uomData = item.item_uoms?.find((u) => u.uom === uom);
		conversionFactor = uomData?.conversion_factor || 1;
	}

	const uomPrice = item.uom_prices?.[uom];
	const baseRate = item.rate ?? item.price_list_rate ?? 0;
	const basePriceListRate = item.price_list_rate ?? item.rate ?? 0;
	let rate = baseRate;
	let priceListRate = basePriceListRate;

	if (uom && uom !== stockUom) {
		if (uomPrice != null) {
			rate = Number.parseFloat(uomPrice);
			priceListRate = rate;
		} else if (conversionFactor !== 1) {
			rate = baseRate * conversionFactor;
			priceListRate = basePriceListRate * conversionFactor;
		}
	}

	return {
		item: {
			...item,
			uom,
			conversion_factor: conversionFactor,
			price_list_rate: priceListRate,
			rate,
		},
		weightKgs,
	};
}

export const searchCachedItemByBarcode = async (barcode) => {
	const exact = await getItemByBarcode(barcode);
	if (exact) return buildUomItem(exact, barcode, null);

	const parsed = parseScaleBarcode(barcode);
	if (!parsed) return { item: null, weightKgs: null };

	let item = await getItemByBarcode(parsed.baseBarcode);
	let matched = parsed.baseBarcode;
	if (!item) {
		item = await getItemByBarcode(parsed.plu);
		matched = parsed.plu;
	}
	if (item) {
		return buildUomItem(item, matched, parsed.weightKgs);
	}
	return { item: null, weightKgs: null };
};
