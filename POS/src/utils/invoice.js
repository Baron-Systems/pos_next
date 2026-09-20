/**
 * Invoice utility functions
 * Common helpers for invoice-related operations across the application
 */

/**
 * Standard rounding to the nearest 0.5 (round half up).
 * Mirrors the server-side _round_pos_amount logic in pos_next/overrides/sales_invoice.py.
 * Examples: 18.24 -> 18.0, 18.25 -> 18.5, 18.74 -> 18.5, 18.75 -> 19.0
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
	const rounded = Math.floor(Math.abs(value) * 2 + 0.5) / 2

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
