/**
 * Phone Number Utilities for POS Next
 * Handles parsing, formatting, and validation of international phone numbers
 */

// Common country codes for automatic detection
const COMMON_COUNTRY_CODES = [
	{ code: "US", isd: "+1", name: "United States" },
	{ code: "GB", isd: "+44", name: "United Kingdom" },
	{ code: "SA", isd: "+966", name: "Saudi Arabia" },
	{ code: "AE", isd: "+971", name: "United Arab Emirates" },
	{ code: "QA", isd: "+974", name: "Qatar" },
	{ code: "KW", isd: "+965", name: "Kuwait" },
	{ code: "BH", isd: "+973", name: "Bahrain" },
	{ code: "OM", isd: "+968", name: "Oman" },
	{ code: "EG", isd: "+20", name: "Egypt" },
	{ code: "JO", isd: "+962", name: "Jordan" },
	{ code: "IQ", isd: "+964", name: "Iraq" },
	{ code: "PS", isd: "+970", name: "Palestine" },
	{ code: "LB", isd: "+961", name: "Lebanon" },
	{ code: "SY", isd: "+963", name: "Syria" },
	{ code: "TR", isd: "+90", name: "Turkey" },
	{ code: "IN", isd: "+91", name: "India" },
	{ code: "PK", isd: "+92", name: "Pakistan" },
	{ code: "BD", isd: "+880", name: "Bangladesh" },
	{ code: "DE", isd: "+49", name: "Germany" },
	{ code: "FR", isd: "+33", name: "France" },
	{ code: "IT", isd: "+39", name: "Italy" },
	{ code: "ES", isd: "+34", name: "Spain" },
	{ code: "NL", isd: "+31", name: "Netherlands" },
	{ code: "BE", isd: "+32", name: "Belgium" },
	{ code: "CH", isd: "+41", name: "Switzerland" },
	{ code: "AT", isd: "+43", name: "Austria" },
	{ code: "SE", isd: "+46", name: "Sweden" },
	{ code: "NO", isd: "+47", name: "Norway" },
	{ code: "DK", isd: "+45", name: "Denmark" },
	{ code: "FI", isd: "+358", name: "Finland" },
	{ code: "RU", isd: "+7", name: "Russia" },
	{ code: "CN", isd: "+86", name: "China" },
	{ code: "JP", isd: "+81", name: "Japan" },
	{ code: "KR", isd: "+82", name: "South Korea" },
	{ code: "BR", isd: "+55", name: "Brazil" },
	{ code: "AR", isd: "+54", name: "Argentina" },
	{ code: "MX", isd: "+52", name: "Mexico" },
	{ code: "ZA", isd: "+27", name: "South Africa" },
	{ code: "NG", isd: "+234", name: "Nigeria" },
	{ code: "KE", isd: "+254", name: "Kenya" },
	{ code: "GH", isd: "+233", name: "Ghana" },
	{ code: "MA", isd: "+212", name: "Morocco" },
	{ code: "TN", isd: "+216", name: "Tunisia" },
	{ code: "DZ", isd: "+213", name: "Algeria" },
	{ code: "LY", isd: "+218", name: "Libya" },
	{ code: "SD", isd: "+249", name: "Sudan" },
	{ code: "ET", isd: "+251", name: "Ethiopia" },
	{ code: "TZ", isd: "+255", name: "Tanzania" },
	{ code: "UG", isd: "+256", name: "Uganda" },
	{ code: "ZW", isd: "+263", name: "Zimbabwe" },
	{ code: "ZM", isd: "+260", name: "Zambia" },
	{ code: "MW", isd: "+265", name: "Malawi" },
	{ code: "MZ", isd: "+258", name: "Mozambique" },
	{ code: "MG", isd: "+261", name: "Madagascar" },
	{ code: "MU", isd: "+230", name: "Mauritius" },
	{ code: "SC", isd: "+248", name: "Seychelles" },
	{ code: "KM", isd: "+269", name: "Comoros" },
	{ code: "DJ", isd: "+253", name: "Djibouti" },
	{ code: "ER", isd: "+291", name: "Eritrea" },
	{ code: "SO", isd: "+252", name: "Somalia" },
]

/**
 * Create a lookup map for country codes by ISD
 */
const isdToCountryMap = COMMON_COUNTRY_CODES.reduce((acc, country) => {
	acc[country.isd] = country
	return acc
}, {})

/**
 * Parse phone number in various formats
 * Handles: +966-0555123456, +9660555123456, 0555123456, +966 555 123 456
 *
 * @param {string} phoneNumber - Raw phone number
 * @returns {Object} Parsed result with isd, number, and fullNumber
 */
export function parsePhoneNumber(phoneNumber) {
	if (!phoneNumber || typeof phoneNumber !== "string") {
		return { isd: "", number: "", fullNumber: "", isValid: false }
	}

	const cleaned = phoneNumber.trim()

	// Already has correct format with dash
	if (cleaned.startsWith("+") && cleaned.includes("-")) {
		const dashIndex = cleaned.indexOf("-")
		const isd = cleaned.substring(0, dashIndex)
		const number = cleaned.substring(dashIndex + 1)
		return {
			isd,
			number,
			fullNumber: cleaned,
			isValid: true,
		}
	}

	// Starts with + but no dash - detect country code
	if (cleaned.startsWith("+")) {
		const digitsOnly = cleaned.substring(1).replace(/\D/g, "")

		// Try to find matching country code (longest first)
		const sortedCodes = Object.keys(isdToCountryMap).sort((a, b) => b.length - a.length)

		for (const isd of sortedCodes) {
			const codeWithoutPlus = isd.substring(1) // Remove + for comparison
			if (digitsOnly.startsWith(codeWithoutPlus)) {
				const number = digitsOnly.substring(codeWithoutPlus.length)
				return {
					isd,
					number,
					fullNumber: `${isd}-${number}`,
					isValid: true,
				}
			}
		}

		// Fallback: assume first 3 digits are country code
		if (digitsOnly.length > 3) {
			const isd = `+${digitsOnly.substring(0, 3)}`
			const number = digitsOnly.substring(3)
			return {
				isd,
				number,
				fullNumber: `${isd}-${number}`,
				isValid: true,
			}
		}
	}

	// No country code provided - return as local number
	const digitsOnly = cleaned.replace(/\D/g, "")
	return {
		isd: "",
		number: digitsOnly,
		fullNumber: digitsOnly,
		isValid: digitsOnly.length >= 7,
	}
}

/**
 * Format phone number with country code
 *
 * @param {string} countryISD - Country code with + (e.g., "+966")
 * @param {string} phoneNumber - Phone number without country code
 * @returns {string} Formatted phone number (+XXX-XXXXXXXX)
 */
export function formatPhoneNumber(countryISD, phoneNumber) {
	if (!phoneNumber) return ""

	// Clean the phone number (keep only digits)
	const cleanNumber = phoneNumber.replace(/\D/g, "")

	// Remove leading zero if country code is provided
	const normalizedNumber = countryISD ? cleanNumber.replace(/^0+/, "") : cleanNumber

	if (!normalizedNumber) return ""

	return countryISD ? `${countryISD}-${normalizedNumber}` : normalizedNumber
}

/**
 * Detect country code from phone number
 *
 * @param {string} phoneNumber - Phone number (e.g., "+9660555123456" or "009660555123456")
 * @returns {string|null} Country ISD code or null
 */
export function detectCountryCode(phoneNumber) {
	if (!phoneNumber) return null

	const cleaned = phoneNumber.trim()

	// Remove leading 00 or +
	let digitsOnly
	if (cleaned.startsWith("00")) {
		digitsOnly = cleaned.substring(2).replace(/\D/g, "")
	} else if (cleaned.startsWith("+")) {
		digitsOnly = cleaned.substring(1).replace(/\D/g, "")
	} else {
		digitsOnly = cleaned.replace(/\D/g, "")
	}

	// Try to find matching country code (longest first)
	const sortedCodes = Object.keys(isdToCountryMap).sort((a, b) => b.length - a.length)

	for (const isd of sortedCodes) {
		const codeWithoutPlus = isd.substring(1)
		if (digitsOnly.startsWith(codeWithoutPlus)) {
			return isd
		}
	}

	return null
}

/**
 * Validate phone number format
 *
 * @param {string} phoneNumber - Phone number to validate
 * @param {boolean} allowEmpty - Whether empty is valid
 * @returns {boolean} Is valid
 */
export function validatePhoneNumber(phoneNumber, allowEmpty = true) {
	if (!phoneNumber || phoneNumber.trim() === "") {
		return allowEmpty
	}

	const parsed = parsePhoneNumber(phoneNumber)
	const digitsOnly = (parsed.number || "").replace(/\D/g, "")

	// Phone numbers should be between 7-15 digits
	return digitsOnly.length >= 7 && digitsOnly.length <= 15
}

/**
 * Get country code from country name
 *
 * @param {string} countryName - Country name (e.g., "Saudi Arabia")
 * @returns {string|null} ISD code or null
 */
export function getCountryCodeByName(countryName) {
	if (!countryName) return null

	const normalized = countryName.toLowerCase().trim()
	const country = COMMON_COUNTRY_CODES.find(
		(c) =>
			c.name.toLowerCase() === normalized ||
			c.code.toLowerCase() === normalized ||
			c.name.toLowerCase().includes(normalized) ||
			normalized.includes(c.name.toLowerCase())
	)

	return country?.isd || null
}

/**
 * Get country info by ISD code
 *
 * @param {string} isd - ISD code (e.g., "+966")
 * @returns {Object|null} Country info
 */
export function getCountryByISD(isd) {
	if (!isd) return null
	return isdToCountryMap[isd] || null
}

/**
 * Smart phone number normalization
 * Tries to convert any format to standard format
 *
 * @param {string} phoneNumber - Any phone number format
 * @param {string} defaultCountryISD - Default country code if not detectable
 * @returns {string} Normalized phone number
 */
export function normalizePhoneNumber(phoneNumber, defaultCountryISD = "+20") {
	if (!phoneNumber) return ""

	const parsed = parsePhoneNumber(phoneNumber)

	if (parsed.isd) {
		return parsed.fullNumber
	}

	// No country code detected, use default
	if (defaultCountryISD) {
		return formatPhoneNumber(defaultCountryISD, parsed.number)
	}

	return parsed.fullNumber
}

/**
 * Extract local number (without country code)
 *
 * @param {string} phoneNumber - Full phone number
 * @returns {string} Local number
 */
export function extractLocalNumber(phoneNumber) {
	const parsed = parsePhoneNumber(phoneNumber)
	return parsed.number || phoneNumber
}

/**
 * Extract country code from full number
 *
 * @param {string} phoneNumber - Full phone number
 * @returns {string} Country ISD code
 */
export function extractCountryCode(phoneNumber) {
	const parsed = parsePhoneNumber(phoneNumber)
	return parsed.isd || ""
}

export default {
	parsePhoneNumber,
	formatPhoneNumber,
	detectCountryCode,
	validatePhoneNumber,
	getCountryCodeByName,
	getCountryByISD,
	normalizePhoneNumber,
	extractLocalNumber,
	extractCountryCode,
	COMMON_COUNTRY_CODES,
}
