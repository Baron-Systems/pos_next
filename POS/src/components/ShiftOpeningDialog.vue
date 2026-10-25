<template>
  <Dialog v-model="open" :options="{ title: step === 3 ? __('ملخص الوردية') : __('Open POS Shift'), size: 'xl' }" @after-leave="$emit('after-leave')">
    <template #body-content>
      <div class="flex flex-col gap-6">
        <!-- Step 1: Select POS Profile -->
        <div v-if="step === 1" class="flex flex-col gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2 text-start">
              {{ __('Select POS Profile') }}
            </label>
            <div v-if="profilesResource.loading" class="text-center py-4">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
            <div v-else-if="profilesResource.data && profilesResource.data.length > 0" class="grid grid-cols-1 gap-3">
              <div
                v-for="profile in profilesResource.data"
                :key="profile.name"
                @click="selectPosProfile(profile)"
                :class="[
                  'p-4 border rounded-lg cursor-pointer transition-all',
                  selectedProfile?.name === profile.name
                    ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500'
                    : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                ]"
              >
                <div class="flex justify-between items-start">
                  <div class="text-start">
                    <h3 class="font-medium text-gray-900">{{ profile.name }}</h3>
                    <p class="text-sm text-gray-500 mt-1">{{ profile.company }}</p>
                  </div>
                  <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                    {{ profile.currency }}
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <p>{{ __('No POS Profiles available. Please contact your administrator.') }}</p>
            </div>
          </div>

          <div v-if="profilesResource.error" class="rounded-md bg-red-50 p-4">
            <p class="text-sm text-red-800">{{ profilesResource.error }}</p>
          </div>
        </div>

        <!-- Step 2: Enter Opening Balances -->
        <div v-if="step === 2" class="flex flex-col gap-4">
          <div class="mb-4">
            <div class="flex items-center justify-between">
              <div class="text-start">
                <h3 class="font-medium text-gray-900">{{ selectedProfile?.name }}</h3>
                <p class="text-sm text-gray-500">{{ selectedProfile?.company }}</p>
              </div>
              <Button variant="subtle" @click="step = 1">{{ __('Change Profile') }}</Button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3 text-start">
              {{ __('Opening Balance (Optional)') }}
            </label>

            <div v-if="dialogDataResource.loading" class="text-center py-4">
              <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>

            <div v-else-if="paymentMethods.length > 0" class="flex flex-col gap-3">
              <div
                v-for="method in paymentMethods"
                :key="method.name"
                class="flex items-center gap-3 p-3 border rounded-lg"
              >
                <div class="flex-1 text-start">
                  <label class="text-sm font-medium text-gray-700">
                    {{ method.mode_of_payment }}
                  </label>
                </div>
                <div class="w-32">
                  <Input
                    v-model="openingBalances[method.mode_of_payment]"
                    type="number"
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                  />
                </div>
              </div>
            </div>

            <div v-else class="text-center py-4 text-gray-500">
              <p class="text-sm">{{ __('No payment methods configured for this POS Profile') }}</p>
            </div>
          </div>

          <div v-if="hasCurrencySetup" class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-3 text-start">
              {{ __('Currency Opening Balances') }}
            </label>
            <div class="flex flex-col gap-3">
              <div
                v-for="cs in currencySetup"
                :key="cs.currency"
                class="flex items-center gap-3 p-3 border rounded-lg"
              >
                <div class="flex-1 text-start">
                  <label class="text-sm font-medium text-gray-700">
                    {{ cs.currency }}
                  </label>
                  <p class="text-xs text-gray-500">{{ cs.cash_account }}</p>
                </div>
                <div class="w-32">
                  <Input
                    v-model="currencyOpeningBalances[cs.currency]"
                    type="number"
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                  />
                </div>
              </div>
            </div>
          </div>

          <div v-if="dialogDataResource.error" class="rounded-md bg-red-50 p-4">
            <p class="text-sm text-red-800">{{ dialogDataResource.error }}</p>
          </div>

          <div v-if="createShiftResource.error" class="rounded-md bg-red-50 p-4">
            <p class="text-sm text-red-800">{{ createShiftResource.error }}</p>
          </div>
        </div>

        <!-- Step 3: Open shift summary + Resume or Open New -->
        <div v-if="step === 3" class="flex flex-col gap-4 text-start">
          <!-- Shift info -->
          <div v-if="existingShift" class="flex flex-wrap items-center justify-between gap-2 bg-gray-50 rounded-lg p-3 text-sm">
            <div>
              <div class="font-semibold text-gray-900">{{ existingShift.pos_profile?.name }}</div>
              <div class="text-xs text-gray-500">{{ existingShift.pos_opening_shift?.name }}</div>
            </div>
            <div class="text-end">
              <div class="text-xs text-gray-500">{{ __('بداية الوردية') }}</div>
              <div class="font-medium text-gray-900" dir="ltr">{{ formatDateTime(existingShift.pos_opening_shift?.period_start_date) }}</div>
            </div>
          </div>

          <div v-if="summaryResource.loading" class="text-center py-6">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>

          <div v-else-if="summaryResource.error" class="rounded-md bg-red-50 p-3">
            <p class="text-sm text-red-800">{{ __('تعذر تحميل ملخص الوردية') }}</p>
          </div>

          <template v-else-if="summary">
            <!-- Blind closing: expected amounts are hidden by POS settings -->
            <div v-if="hideExpectedAmount" class="rounded-lg border border-gray-200 bg-gray-50 p-3 text-sm text-gray-600">
              {{ __('عرض المبالغ مخفي حسب إعدادات نقطة البيع') }}
              <div class="mt-1 text-gray-900 font-medium">
                {{ __('عدد الفواتير: {0} · عدد المرتجعات: {1}', [summary.sales_count, summary.returns_count]) }}
              </div>
            </div>

            <template v-else>
              <!-- Cash in drawer (highlight) -->
              <div class="rounded-xl border-2 border-green-300 bg-green-50 p-4 flex items-center justify-between gap-3">
                <div>
                  <div class="text-sm font-medium text-green-800">{{ __('النقد المتوقع في الصندوق') }}</div>
                  <div class="text-xs text-green-700">{{ summary.cash_mode_of_payment }}</div>
                </div>
                <div class="text-2xl font-bold text-green-900" dir="ltr">{{ formatCurrency(expectedCash) }}</div>
              </div>

              <!-- Sales figures -->
              <div class="grid grid-cols-2 gap-3">
                <div class="rounded-lg border border-blue-200 bg-blue-50 p-3">
                  <div class="text-xs font-medium text-blue-700">{{ __('المبيعات') }}</div>
                  <div class="text-lg font-bold text-blue-900" dir="ltr">{{ formatCurrency(summary.sales_total) }}</div>
                  <div class="text-xs text-blue-600">{{ __('{0} فاتورة', [summary.sales_count]) }}</div>
                </div>
                <div class="rounded-lg border border-red-200 bg-red-50 p-3">
                  <div class="text-xs font-medium text-red-700">{{ __('المرتجعات') }}</div>
                  <div class="text-lg font-bold text-red-800" dir="ltr">{{ summary.returns_total ? '-' : '' }}{{ formatCurrency(summary.returns_total) }}</div>
                  <div class="text-xs text-red-600">{{ __('{0} مرتجع', [summary.returns_count]) }}</div>
                </div>
                <div class="rounded-lg border border-gray-200 bg-white p-3">
                  <div class="text-xs font-medium text-gray-600">{{ __('صافي المبيعات') }}</div>
                  <div class="text-lg font-bold text-gray-900" dir="ltr">{{ formatCurrency(summary.grand_total) }}</div>
                  <div class="text-xs text-gray-500">{{ __('المبيعات - المرتجعات') }}</div>
                </div>
                <div class="rounded-lg border border-gray-200 bg-white p-3">
                  <div class="text-xs font-medium text-gray-600">{{ __('المبيعات النقدية') }}</div>
                  <div class="text-lg font-bold text-gray-900" dir="ltr">{{ formatCurrency(summary.cash_sales_total) }}</div>
                  <div class="text-xs text-gray-500">{{ __('بعد خصم الباقي') }}</div>
                </div>
                <div v-if="summary.total_expenses" class="col-span-2 rounded-lg border border-rose-200 bg-rose-50 p-3 flex items-center justify-between">
                  <div class="text-xs font-medium text-rose-700">{{ __('مصاريف الوردية') }}</div>
                  <div class="text-base font-bold text-rose-800" dir="ltr">-{{ formatCurrency(summary.total_expenses) }}</div>
                </div>
              </div>

              <!-- Per payment method -->
              <div v-if="summary.payment_reconciliation?.length" class="rounded-lg border border-gray-200 overflow-hidden">
                <div class="grid grid-cols-3 gap-2 bg-gray-50 px-3 py-2 text-xs font-semibold text-gray-600">
                  <div>{{ __('طريقة الدفع') }}</div>
                  <div class="text-end">{{ __('رصيد الافتتاح') }}</div>
                  <div class="text-end">{{ __('المتوقع') }}</div>
                </div>
                <div
                  v-for="pay in summary.payment_reconciliation"
                  :key="pay.mode_of_payment"
                  class="grid grid-cols-3 gap-2 px-3 py-2 text-sm border-t border-gray-100"
                >
                  <div class="text-gray-900 truncate">{{ pay.mode_of_payment }}</div>
                  <div class="text-end text-gray-600" dir="ltr">{{ formatCurrency(pay.opening_amount) }}</div>
                  <div class="text-end font-semibold text-gray-900" dir="ltr">{{ formatCurrency(pay.expected_amount) }}</div>
                </div>
              </div>
            </template>

            <!-- Printed drafts are submitted (and counted) only at closing -->
            <div v-if="summary.pending_printed_count > 0" class="rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
              {{ __('يوجد {0} فاتورة مطبوعة غير مرحّلة، غير محسوبة في الأرقام أعلاه وسيتم ترحيلها عند إغلاق الوردية', [summary.pending_printed_count]) }}
            </div>
          </template>

          <div class="flex gap-3 justify-center pt-2">
            <Button variant="solid" theme="blue" @click="resumeShift">
              {{ __('Resume Shift') }}
            </Button>
            <Button
              variant="subtle"
              theme="gray"
              @click="closeAndOpenNew"
              :disabled="closingExistingShift"
            >
              {{ __('Close & Open New') }}
            </Button>
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex justify-between w-full">
        <Button v-if="step > 1 && step !== 3" variant="subtle" @click="step--">
          {{ __('Back') }}
        </Button>
        <div v-else></div>

        <div class="flex gap-2">
          <Button variant="subtle" @click="closeDialog('cancelled')" :disabled="createShiftResource.loading">
            {{ __('Cancel') }}
          </Button>
          <Button
            v-if="step === 1"
            variant="solid"
            theme="blue"
            @click="nextStep"
            :disabled="!selectedProfile"
          >
            {{ __('Next') }}
          </Button>
          <Button
            v-if="step === 2"
            variant="solid"
            theme="blue"
            @click="openShift"
            :loading="createShiftResource.loading"
          >
            {{ __('Open Shift') }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>

  <ShiftClosingDialog
    v-if="existingShift"
    v-model="showClosingDialog"
    :opening-shift="existingShift?.pos_opening_shift?.name"
    @shift-closed="handleExistingShiftClosed"
  />

  <ShiftPasswordDialog
    v-model="showPasswordDialog"
    :pos-profile="passwordProfileName"
    @verified="handlePasswordVerified"
    @cancelled="handlePasswordCancelled"
  />
</template>

<script setup>
import { Button, Dialog, Input } from "frappe-ui"
import { createResource } from "frappe-ui"
import { computed, ref, watch } from "vue"
import { useShift } from "../composables/useShift"
import { useFormatters } from "../composables/useFormatters"
import ShiftClosingDialog from "./ShiftClosingDialog.vue"
import ShiftPasswordDialog from "./ShiftPasswordDialog.vue"
import { usePOSSettingsStore } from "@/stores/posSettings"

const props = defineProps({
	modelValue: Boolean,
})

const emit = defineEmits(["update:modelValue", "shift-opened", "dialog-closed", "after-leave"])

const open = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

const { createOpeningShift, getOpeningDialogData, checkOpeningShift } =
	useShift()
const { formatDateTime, formatCurrency } = useFormatters()
const posSettingsStore = usePOSSettingsStore()
const hideExpectedAmount = computed(() => posSettingsStore.hideExpectedAmount)

const step = ref(1)
const selectedProfile = ref(null)
const openingBalances = ref({})
const currencyOpeningBalances = ref({})
const existingShift = ref(null)
const showClosingDialog = ref(false)
const closingExistingShift = ref(false)
const restartProfileName = ref(null)
const showPasswordDialog = ref(false)
const passwordProfileName = ref("")
const pendingAction = ref(null)

// Get POS Profiles
const profilesResource = createResource({
	url: "pos_next.api.pos_profile.get_pos_profiles",
	auto: false,
})

// Get dialog data (payment methods)
const dialogDataResource = createResource({
	url: "pos_next.api.shifts.get_opening_dialog_data",
	auto: false,
})

// Read-only summary of the open shift (same figures as closing)
const summaryResource = createResource({
	url: "pos_next.api.shifts.get_shift_summary",
	auto: false,
})

const summary = computed(() => summaryResource.data || null)

const expectedCash = computed(() => {
	const pay = summary.value?.payment_reconciliation?.find(
		(p) => p.mode_of_payment === summary.value.cash_mode_of_payment,
	)
	return pay?.expected_amount ?? 0
})

function loadShiftSummary() {
	const openingShift = existingShift.value?.pos_opening_shift?.name
	if (!openingShift) return
	summaryResource.submit({ opening_shift: openingShift }).catch((error) => {
		console.error("Error loading shift summary:", error)
	})
}

// Create shift resource
const createShiftResource = createOpeningShift

// Computed payment methods for selected profile
const paymentMethods = computed(() => {
	if (!dialogDataResource.data || !selectedProfile.value) return []

	return (dialogDataResource.data.payments_method || []).filter(
		(method) => method.parent === selectedProfile.value.name,
	)
})

// Computed currency setup for selected profile
const currencySetup = computed(() => {
	if (!dialogDataResource.data || !selectedProfile.value) return []

	const setups = dialogDataResource.data.profile_currency_setups || {}
	return setups[selectedProfile.value.name] || []
})

const hasCurrencySetup = computed(() => currencySetup.value.length > 0)

// Watch dialog open state
// Use { immediate: true } to ensure initDialog runs even when
// the component mounts with open already true (e.g., after logout with dialog open)
watch(
	open,
	(isOpen) => {
		if (isOpen) {
			initDialog()
		} else {
			resetDialog()
		}
	},
	{ immediate: true },
)

watch(showClosingDialog, (isOpen) => {
	closingExistingShift.value = isOpen
	if (!isOpen && existingShift.value) {
		restartProfileName.value = null
	}
})

async function initDialog() {
	step.value = 1
	selectedProfile.value = null
	existingShift.value = null
	openingBalances.value = {}
	dialogDataResource.reset()

	try {
		// Await profile fetch to ensure data is loaded before proceeding
		await profilesResource.fetch()

		// Check if user already has an open shift
		const checkResult = await checkOpeningShift.fetch()
		if (checkResult) {
			existingShift.value = checkResult
			step.value = 3
			loadShiftSummary()
		}
	} catch (error) {
		console.error("Error initializing shift dialog:", error)
		// Error will be displayed via profilesResource.error in the UI
	}
}

function resetDialog() {
	step.value = 1
	selectedProfile.value = null
	openingBalances.value = {}
	currencyOpeningBalances.value = {}
	existingShift.value = null
	profilesResource.reset()
	summaryResource.reset()
	dialogDataResource.reset()
	createShiftResource.reset()
}

function selectPosProfile(profile) {
	selectedProfile.value = profile
}

async function nextStep() {
	if (step.value === 1 && selectedProfile.value) {
		await dialogDataResource.fetch()
		step.value = 2
	}
}

async function openShift() {
	if (!selectedProfile.value) return

	passwordProfileName.value = selectedProfile.value.name
	pendingAction.value = "open"
	showPasswordDialog.value = true
}

async function openShiftAfterPassword() {
	if (!selectedProfile.value) return

	// Prepare balance details
	const balance_details = paymentMethods.value.map((method) => ({
		mode_of_payment: method.mode_of_payment,
		opening_amount: Number.parseFloat(
			openingBalances.value[method.mode_of_payment] || 0,
		),
	}))

	// Prepare currency opening balances
	const currency_opening_balances = currencySetup.value.map((cs) => ({
		currency: cs.currency,
		account: cs.cash_account,
		opening_amount: Number.parseFloat(
			currencyOpeningBalances.value[cs.currency] || 0,
		),
	}))

	try {
		await createShiftResource.submit({
			pos_profile: selectedProfile.value.name,
			company: selectedProfile.value.company,
			balance_details,
			currency_opening_balances: currency_opening_balances.length > 0 ? currency_opening_balances : null,
		})

		emit("shift-opened")
		closeDialog("shift-opened")
	} catch (error) {
		console.error("Error opening shift:", error)
	}
}

function resumeShift() {
	passwordProfileName.value = existingShift.value?.pos_profile?.name || ""
	pendingAction.value = "resume"
	showPasswordDialog.value = true
}

function resumeShiftAfterPassword() {
	emit("shift-opened")
	closeDialog("resumed")
}

function closeAndOpenNew() {
	if (!existingShift.value?.pos_opening_shift?.name) {
		return
	}

	restartProfileName.value = existingShift.value.pos_profile?.name || null
	showClosingDialog.value = true
}

function closeDialog(reason) {
	open.value = false
	emit("dialog-closed", { reason })
}

function handlePasswordVerified() {
	const action = pendingAction.value
	pendingAction.value = null
	if (action === "open") {
		openShiftAfterPassword()
	} else if (action === "resume") {
		resumeShiftAfterPassword()
	}
}

function handlePasswordCancelled() {
	pendingAction.value = null
}

async function handleExistingShiftClosed() {
	showClosingDialog.value = false
	const profileToRestore = restartProfileName.value
	restartProfileName.value = null
	existingShift.value = null
	step.value = 1
	openingBalances.value = {}

	await checkOpeningShift.fetch()

	if (!profilesResource.data || profilesResource.data.length === 0) {
		await profilesResource.fetch()
	}

	if (profileToRestore) {
		const matchedProfile = profilesResource.data?.find(
			(profile) => profile.name === profileToRestore,
		)

		if (matchedProfile) {
			selectedProfile.value = matchedProfile
			await dialogDataResource.fetch()
			step.value = 2
		}
	}
}
</script>
