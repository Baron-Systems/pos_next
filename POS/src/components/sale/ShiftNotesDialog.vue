<template>
	<Dialog
		v-model="show"
		:options="{ title: __('ملاحظات الوردية'), size: 'lg' }"
		@after-leave="$emit('after-leave')"
	>
		<template #body-content>
			<div class="flex flex-col gap-5" dir="rtl">
				<!-- Header / Counter -->
				<div class="flex items-center justify-between bg-amber-50 border border-amber-100 rounded-xl px-4 py-3">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
							<svg class="h-5 w-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
							</svg>
						</div>
						<div>
							<p class="text-sm font-semibold text-gray-900">{{ __('ملاحظات محفوظة') }}</p>
							<p class="text-xs text-gray-600">{{ __('{0} ملاحظة', [notes.length]) }}</p>
						</div>
					</div>
					<span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-amber-200 text-amber-800 text-sm font-bold">
						{{ notes.length }}
					</span>
				</div>

				<!-- Add/Edit Form -->
				<div class="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
					<div class="flex items-center gap-2 mb-4">
						<div class="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
							<svg v-if="!editingNote" class="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
							</svg>
							<svg v-else class="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
							</svg>
						</div>
						<h4 class="text-base font-semibold text-gray-900">
							{{ editingNote ? __('تعديل الملاحظة') : __('إضافة ملاحظة جديدة') }}
						</h4>
					</div>
					<div class="flex flex-col gap-4">
						<FormControl
							v-model="form.title"
							type="text"
							:placeholder="__('مثال: عطل في الطابعة')"
							:label="__('عنوان الملاحظة')"
						/>
						<FormControl
							v-model="form.description"
							type="textarea"
							:placeholder="__('اكتب تفاصيل الملاحظة هنا...')"
							:label="__('الوصف (اختياري)')"
							:rows="3"
						/>
						<div class="flex gap-2">
							<Button
								v-if="editingNote"
								variant="subtle"
								class="flex-1 h-10"
								@click="cancelEdit"
							>
								{{ __('إلغاء') }}
							</Button>
							<Button
								variant="solid"
								theme="blue"
								class="flex-1 h-10"
								:loading="saving"
								:disabled="!form.title.trim()"
								@click="saveNote"
							>
								<span class="inline-flex items-center gap-1.5">
									<svg v-if="!editingNote" class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
									</svg>
									<span>{{ editingNote ? __('حفظ التعديلات') : __('إضافة الملاحظة') }}</span>
								</span>
							</Button>
						</div>
					</div>
				</div>

				<!-- Loading State -->
				<div v-if="loading" class="text-center py-10">
					<div class="inline-block animate-spin rounded-full h-10 w-10 border-4 border-amber-200 border-t-amber-500"></div>
					<p class="mt-3 text-sm text-gray-500">{{ __('جاري تحميل الملاحظات...') }}</p>
				</div>

				<!-- Empty State -->
				<div v-else-if="notes.length === 0" class="text-center py-12">
					<div class="w-20 h-20 bg-amber-50 rounded-full flex items-center justify-center mx-auto mb-4">
						<svg class="h-10 w-10 text-amber-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
						</svg>
					</div>
					<p class="text-lg font-semibold text-gray-900">{{ __('لا توجد ملاحظات بعد') }}</p>
					<p class="text-sm text-gray-500 mt-2 max-w-xs mx-auto leading-relaxed">{{ __('استخدم النموذج أعلاه لإضافة ملاحظات تهمك عن هذه الوردية') }}</p>
				</div>

				<!-- Notes List -->
				<div v-else class="flex flex-col gap-3 max-h-[22rem] overflow-y-auto p-1">
					<div
						v-for="note in notes"
						:key="note.name"
						class="group bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md hover:border-amber-300 transition-all"
					>
						<div class="flex items-start justify-between gap-4">
							<div class="flex-1 min-w-0">
								<div class="flex items-center gap-2 mb-1">
									<div class="w-2 h-2 rounded-full bg-amber-400 flex-shrink-0"></div>
									<h4 class="text-base font-semibold text-gray-900 break-words">
										{{ note.title }}
									</h4>
								</div>
								<p v-if="note.description" class="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap pe-4">
									{{ note.description }}
								</p>
							</div>
							<div class="flex items-center gap-0.5 flex-shrink-0 opacity-60 group-hover:opacity-100 transition-opacity">
								<button
									@click="startEdit(note)"
									class="text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors p-2"
									:title="__('تعديل الملاحظة')"
								>
									<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
									</svg>
								</button>
								<button
									@click="confirmDelete(note)"
									class="text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors p-2"
									:title="__('حذف الملاحظة')"
								>
									<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
									</svg>
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</template>
		<template #actions>
			<Button variant="subtle" @click="show = false">
				{{ __('إغلاق') }}
			</Button>
		</template>
	</Dialog>

	<!-- Delete Confirmation -->
	<Dialog
		v-model="showDeleteDialog"
		:options="{ title: __('حذف الملاحظة؟'), size: 'xs' }"
	>
		<template #body-content>
			<div class="text-center py-2" dir="rtl">
				<div class="w-14 h-14 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-3">
					<svg class="h-7 w-7 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
					</svg>
				</div>
				<p class="text-base font-semibold text-gray-900 mb-1">{{ __('حذف الملاحظة') }}</p>
				<p class="text-sm text-gray-500">{{ __('هل أنت متأكد من حذف هذه الملاحظة؟') }}</p>
			</div>
		</template>
		<template #actions>
			<div class="flex gap-2 w-full" dir="rtl">
				<Button variant="subtle" class="flex-1" @click="showDeleteDialog = false">
					{{ __('إلغاء') }}
				</Button>
				<Button
					variant="solid"
					theme="red"
					class="flex-1"
					:loading="deleting"
					@click="deleteNote"
				>
					{{ __('حذف') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { Button, Dialog, FormControl } from "frappe-ui"
import { computed, ref, watch } from "vue"
import { call } from "@/utils/apiWrapper"
import { useToast } from "@/composables/useToast"

const props = defineProps({
	modelValue: {
		type: Boolean,
		required: true,
	},
	openingShift: {
		type: String,
		default: null,
	},
})

const emit = defineEmits(["update:modelValue", "after-leave", "notes-updated"])

const show = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

const { showSuccess, showError } = useToast()

const notes = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editingNote = ref(null)
const showDeleteDialog = ref(false)
const noteToDelete = ref(null)

const form = ref({
	title: "",
	description: "",
})

watch(
	() => props.modelValue,
	(isOpen) => {
		if (isOpen) {
			loadNotes()
		} else {
			resetForm()
		}
	}
)

async function loadNotes() {
	if (!props.openingShift) {
		notes.value = []
		return
	}

	loading.value = true
	try {
		const result = await call("pos_next.api.shifts.get_shift_notes", {
			opening_shift: props.openingShift,
		})
		notes.value = result || []
	} catch (error) {
		showError(__('فشل تحميل ملاحظات الوردية'), error.message)
		notes.value = []
	} finally {
		loading.value = false
	}
}

function resetForm() {
	form.value = { title: "", description: "" }
	editingNote.value = null
}

function cancelEdit() {
	resetForm()
}

function startEdit(note) {
	editingNote.value = note
	form.value = {
		title: note.title,
		description: note.description || "",
	}
}

async function saveNote() {
	const title = form.value.title.trim()
	if (!title) return

	saving.value = true
	try {
		if (editingNote.value) {
			await call("pos_next.api.shifts.update_shift_note", {
				note_id: editingNote.value.name,
				title,
				description: form.value.description,
			})
			showSuccess(__('تم تحديث الملاحظة بنجاح'))
		} else {
			await call("pos_next.api.shifts.add_shift_note", {
				opening_shift: props.openingShift,
				title,
				description: form.value.description,
			})
			showSuccess(__('تم إضافة الملاحظة بنجاح'))
		}
		await loadNotes()
		resetForm()
		emit("notes-updated", notes.value)
	} catch (error) {
		showError(__('فشل حفظ الملاحظة'), error.message)
	} finally {
		saving.value = false
	}
}

function confirmDelete(note) {
	noteToDelete.value = note
	showDeleteDialog.value = true
}

async function deleteNote() {
	if (!noteToDelete.value) return

	deleting.value = true
	try {
		await call("pos_next.api.shifts.delete_shift_note", {
			note_id: noteToDelete.value.name,
		})
		showSuccess(__('تم حذف الملاحظة بنجاح'))
		await loadNotes()
		emit("notes-updated", notes.value)
	} catch (error) {
		showError(__('فشل حذف الملاحظة'), error.message)
	} finally {
		deleting.value = false
		showDeleteDialog.value = false
		noteToDelete.value = null
	}
}
</script>

<style scoped>
:deep(textarea) {
	resize: none;
}
</style>
