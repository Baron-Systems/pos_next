<template>
	<!-- Main Dialog -->
	<Dialog
		v-model="show"
		:options="{ title: __('Draft Invoices'), size: 'xl' }"
	>
		<template #body-content>
			<div class="flex flex-col gap-3">
				<!-- Empty State -->
				<div v-if="drafts.length === 0" class="text-center py-10">
					<div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
						<svg class="h-10 w-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
						</svg>
					</div>
					<p class="text-lg font-medium text-gray-900">{{ __('No draft invoices') }}</p>
					<p class="text-sm text-gray-500 mt-1">{{ __('Save invoices as drafts to continue later') }}</p>
				</div>

				<!-- Drafts List -->
				<div v-else class="flex flex-col gap-3 max-h-[28rem] overflow-y-auto">
					<div
						v-for="draft in drafts"
						:key="draft.draft_id"
						class="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-400 hover:shadow-sm transition-all cursor-pointer"
						@click="$emit('load-draft', draft)"
					>
						<div class="flex items-start justify-between mb-3">
							<div class="flex-1">
								<h4 class="text-base font-semibold text-gray-900">
									{{ draft.draft_id }}
								</h4>
								<p v-if="draft.customer" class="text-sm text-gray-500 mt-1">
									{{ __('Customer: {0}', [(draft.customer?.customer_name || draft.customer?.name || draft.customer)]) }}
								</p>
								<p class="text-sm text-gray-400 mt-1">
									{{ formatDateTime(draft.created_at) }}
								</p>
							</div>
							<div class="flex items-center gap-2">
								<button
									@click.stop="handlePrintDraft(draft)"
									class="text-gray-400 hover:text-blue-600 transition-colors p-2"
									:title="__('Print draft')"
								>
									<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
									</svg>
								</button>
								<button
									@click.stop="openNoteDialog(draft)"
									class="text-gray-400 hover:text-amber-600 transition-colors p-2"
									:title="__('Note')"
								>
									<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
									</svg>
								</button>
								<button
									@click.stop="handleDeleteDraft(draft.draft_id)"
									class="text-gray-400 hover:text-red-600 transition-colors p-2"
									:title="__('Delete draft')"
								>
									<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
									</svg>
								</button>
							</div>
						</div>

						<!-- Note Preview -->
						<div v-if="draft.note" class="mb-3">
							<p class="text-sm text-amber-800 bg-amber-50 px-3 py-2 rounded leading-snug line-clamp-2">
								{{ draft.note }}
							</p>
						</div>

						<!-- Items Preview -->
						<div class="flex items-center justify-between text-sm">
							<span class="text-gray-600">
								{{ __('{0} item(s)', [draft.items?.length || 0]) }}
							</span>
							<span class="font-bold text-base text-blue-600">
								{{ formatCurrency(calculateTotal(draft.items)) }}
							</span>
						</div>

						<!-- Items List (condensed) -->
						<div v-if="draft.items && draft.items.length > 0" class="mt-3 pt-3 border-t border-gray-100">
							<div class="flex flex-wrap gap-2">
								<span
									v-for="(item, idx) in draft.items.slice(0, 3)"
									:key="idx"
									class="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
								>
									{{ item.item_name }} ({{ item.quantity || item.qty }})
								</span>
								<span
									v-if="draft.items.length > 3"
									class="text-xs text-gray-500 px-2 py-1"
								>
									{{ __('+{0} more', [draft.items.length - 3]) }}
								</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</template>
		<template #actions>
			<div class="flex justify-between items-center w-full">
				<Button
					v-if="drafts.length > 0"
					variant="subtle"
					theme="red"
					@click="showClearAllDialog = true"
				>
					{{ __('Clear All') }}
				</Button>
				<Button variant="subtle" @click="show = false">
					{{ __('Close') }}
				</Button>
			</div>
		</template>
	</Dialog>

	<!-- Edit Note Dialog -->
	<Dialog
		v-model="showNoteDialog"
		:options="{ title: __('Edit Note'), size: 'sm' }"
	>
		<template #body-content>
			<div class="py-2">
				<textarea
					v-model="noteText"
					rows="3"
					class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
					:placeholder="__('Enter note for this draft invoice...')"
				></textarea>
			</div>
		</template>
		<template #actions>
			<div class="flex gap-2 w-full">
				<Button class="flex-1" variant="subtle" @click="showNoteDialog = false">
					{{ __('Cancel') }}
				</Button>
				<Button class="flex-1" variant="solid" theme="blue" @click="saveNote">
					{{ __('Save') }}
				</Button>
			</div>
		</template>
	</Dialog>

	<!-- Delete Single Draft Confirmation -->
	<Dialog
		v-model="showDeleteDialog"
		:options="{ title: __('Delete Draft?'), size: 'xs' }"
	>
		<template #body-content>
			<div class="py-3">
				<p class="text-sm text-gray-600">
					{{ __('Permanently delete this draft invoice?') }}
				</p>
			</div>
		</template>
		<template #actions>
			<div class="flex gap-2 w-full">
				<Button class="flex-1" variant="subtle" @click="showDeleteDialog = false">
					{{ __('Cancel') }}
				</Button>
				<Button class="flex-1" variant="solid" theme="red" @click="confirmDeleteDraft">
					{{ __('Delete') }}
				</Button>
			</div>
		</template>
	</Dialog>

	<!-- Clear All Drafts Confirmation -->
	<Dialog
		v-model="showClearAllDialog"
		:options="{ title: __('Clear All Drafts?'), size: 'xs' }"
	>
		<template #body-content>
			<div class="py-3">
				<p class="text-sm text-gray-600">
					{{ __('Permanently delete all {0} draft invoices?', [drafts.length]) }}
				</p>
			</div>
		</template>
		<template #actions>
			<div class="flex gap-2 w-full">
				<Button class="flex-1" variant="subtle" @click="showClearAllDialog = false">
					{{ __('Cancel') }}
				</Button>
				<Button class="flex-1" variant="solid" theme="red" @click="confirmClearAll">
					{{ __('Clear All') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"
import { clearAllDrafts, deleteDraft, getAllDrafts, updateDraftNote } from "@/utils/draftManager"
import { printInvoiceCustom } from "@/utils/printInvoice"
import { useToast } from "@/composables/useToast"
import { usePOSShiftStore } from "@/stores/posShift"
import { Button, Dialog } from "frappe-ui"
import { onMounted, ref, watch } from "vue"

const { showSuccess, showError } = useToast()
const shiftStore = usePOSShiftStore()

const props = defineProps({
	modelValue: Boolean,
	currency: {
		type: String,
		default: "USD",
	},
})

const emit = defineEmits(["update:modelValue", "load-draft", "drafts-updated"])

const show = ref(props.modelValue)
const drafts = ref([])
const showDeleteDialog = ref(false)
const showClearAllDialog = ref(false)
const draftToDelete = ref(null)
const showNoteDialog = ref(false)
const noteDraftId = ref(null)
const noteText = ref("")

watch(
	() => props.modelValue,
	(val) => {
		show.value = val
		if (val) {
			loadDrafts()
		}
	},
)

watch(show, (val) => {
	emit("update:modelValue", val)
})

onMounted(() => {
	loadDrafts()
})

async function loadDrafts() {
	try {
		drafts.value = await getAllDrafts()
	} catch (error) {
		console.error("Error loading drafts:", error)
		showError(__("Failed to load draft invoices"))
	}
}

function handlePrintDraft(draft) {
	try {
		const invoiceData = {
			name: draft.draft_id,
			company: shiftStore.profileCompany,
			items: draft.items,
			payments: [],
			grand_total: calculateTotal(draft.items),
			posting_date: draft.created_at,
			customer_name:
				draft.customer?.customer_name ||
				draft.customer?.name ||
				draft.customer,
			status: "Draft",
			note: draft.note,
		}
		printInvoiceCustom(invoiceData)
	} catch (error) {
		console.error("Error printing draft:", error)
		showError(__("Failed to print draft"))
	}
}

function openNoteDialog(draft) {
	noteDraftId.value = draft.draft_id
	noteText.value = draft.note || ""
	showNoteDialog.value = true
}

async function saveNote() {
	try {
		await updateDraftNote(noteDraftId.value, noteText.value)
		await loadDrafts()
		showNoteDialog.value = false
		noteDraftId.value = null
		noteText.value = ""
		showSuccess(__("Note saved"))
	} catch (error) {
		console.error("Error saving note:", error)
		showError(__("Failed to save note"))
	}
}

function handleDeleteDraft(draftId) {
	draftToDelete.value = draftId
	showDeleteDialog.value = true
}

async function confirmDeleteDraft() {
	try {
		await deleteDraft(draftToDelete.value)
		await loadDrafts()
		showDeleteDialog.value = false
		draftToDelete.value = null

		// Notify parent to update count
		emit("drafts-updated")

		showSuccess(__("Draft invoice deleted"))
	} catch (error) {
		console.error("Error deleting draft:", error)
		showError(__("Failed to delete draft"))
	}
}

async function confirmClearAll() {
	try {
		await clearAllDrafts()
		await loadDrafts()
		showClearAllDialog.value = false

		// Notify parent to update count
		emit("drafts-updated")

		showSuccess(__("All draft invoices deleted"))
	} catch (error) {
		console.error("Error clearing drafts:", error)
		showError(__("Failed to clear drafts"))
	}
}

function formatDateTime(dateStr) {
	const date = new Date(dateStr)
	return date.toLocaleString("en-US", {
		month: "short",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
	})
}

function formatCurrency(amount) {
	return formatCurrencyUtil(Number.parseFloat(amount || 0), props.currency)
}

function calculateTotal(items) {
	if (!items || items.length === 0) return 0
	return items.reduce((sum, item) => {
		const qty = item.quantity || item.qty || 1
		const rate = item.rate || 0
		return sum + qty * rate
	}, 0)
}
</script>
