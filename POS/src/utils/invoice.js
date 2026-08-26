/**
 * Invoice utility functions
 * Common helpers for invoice-related operations across the application
 */

/**
 * POS rounding to the nearest 0.5 using thresholds.
 * Mirrors the server-side _round_pos_amount logic in pos_next/overrides/sales_invoice.py:
 * - fractional part >= 0.80  -> round up to next whole number
 * - fractional part >= 0.40  -> round to .5
 * - fractional part <  0.40  -> round down to whole number
 *
 * @param {number} amount - The amount to round
 * @param {number} precision - Decimal precision (default 2)
 * @returns {number} Rounded amount
 */
export function roundPosAmount(amount, precision = 2) {
	const value = Number(amount) || 0
	if (!value) {
		return Number((0).toFixed(precision))
	}

	const sign = value >= 0 ? 1 : -1
	const absValue = Math.abs(value)
	const integerPart = Math.floor(absValue)
	const fractional = absValue - integerPart

	let rounded
	if (fractional >= 0.8) {
		rounded = integerPart + 1
	} else if (fractional >= 0.4) {
		rounded = integerPart + 0.5
	} else {
		rounded = integerPart
	}

	return Number((sign * rounded).toFixed(precision))
}

/**
 * Get the appropriate CSS classes for invoice status badge
 * @param {Object} invoice - Invoice object with status and docstatus fields
 * @returns {string} Tailwind CSS classes for the status badge
 */
export function getInvoiceStatusColor(invoice) {
	const status = invoice.status?.toLowerCase()

	// Red for overdue, cancelled
	if (status === 'overdue' || invoice.docstatus === 2) {
		return 'bg-red-100 text-red-800'
	}

	// Orange for partly paid (partial payment received)
	if (status === 'partly paid' || status === 'partially paid') {
		return 'bg-orange-100 text-orange-800'
	}

	// Yellow for unpaid
	if (status === 'unpaid') {
		return 'bg-yellow-100 text-yellow-800'
	}

	// Blue for credit note issued
	if (status === 'credit note issued') {
		return 'bg-blue-100 text-blue-800'
	}

	// Green for paid, submitted
	if (status === 'paid' || invoice.docstatus === 1) {
		return 'bg-green-100 text-green-800'
	}

	// Gray for draft and others
	return 'bg-gray-100 text-gray-800'
}

/**
 * Get status color theme name for use with Badge component
 * @param {string} status - Invoice status string
 * @returns {string} Theme name (red, yellow, blue, green, gray)
 */
export function getInvoiceStatusTheme(status) {
	const statusLower = status?.toLowerCase()

	if (statusLower === 'overdue' || statusLower === 'cancelled') {
		return 'red'
	}

	if (statusLower === 'partly paid' || statusLower === 'partially paid') {
		return 'orange'
	}

	if (statusLower === 'unpaid') {
		return 'yellow'
	}

	if (statusLower === 'credit note issued') {
		return 'blue'
	}

	if (statusLower === 'paid') {
		return 'green'
	}

	return 'gray'
}
