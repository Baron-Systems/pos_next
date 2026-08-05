<template>
  <Dialog
    v-model="open"
    :options="{ title: __('رمز الوردية'), size: 'sm' }"
    :dismissable="!loading"
    @after-leave="$emit('after-leave')"
  >
    <template #body-content>
      <div class="flex flex-col gap-4 py-2">
        <div class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 mb-3">
            <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <p class="text-sm text-gray-600">
            {{ __('أدخل رمز الوردية للمتابعة') }}
          </p>
        </div>

        <div>
          <Input
            ref="passwordInputRef"
            v-model="password"
            type="password"
            :placeholder="__('أدخل الرمز')"
            @keyup.enter="verify"
            class="w-full"
          />
        </div>

        <div v-if="errorMsg" class="rounded-md bg-red-50 p-3">
          <p class="text-sm text-red-800">{{ errorMsg }}</p>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex gap-2 w-full">
        <Button
          variant="subtle"
          class="flex-1"
          @click="cancel"
          :disabled="loading"
        >
          {{ __('إلغاء') }}
        </Button>
        <Button
          variant="solid"
          theme="blue"
          class="flex-1"
          @click="verify"
          :loading="loading"
          :disabled="!password"
        >
          {{ __('تأكيد') }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { Button, Dialog, Input, createResource } from "frappe-ui"
import { computed, ref, watch, nextTick } from "vue"

const props = defineProps({
  modelValue: Boolean,
  posProfile: { type: String, default: "" },
})

const emit = defineEmits(["update:modelValue", "verified", "cancelled", "after-leave"])

const open = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
})

const password = ref("")
const errorMsg = ref("")
const loading = ref(false)
const passwordInputRef = ref(null)

const verifyResource = createResource({
  url: "pos_next.api.shifts.verify_shift_password",
  auto: false,
})

watch(open, async (isOpen) => {
  if (isOpen) {
    password.value = ""
    errorMsg.value = ""
    await nextTick()
    passwordInputRef.value?.focus?.()
  }
})

async function verify() {
  if (!password.value) return

  loading.value = true
  errorMsg.value = ""

  try {
    const result = await verifyResource.submit({
      pos_profile: props.posProfile,
      password: password.value,
    })

    if (result?.verified) {
      emit("verified")
      open.value = false
    } else {
      errorMsg.value = result?.message || __("الرمز غير صحيح")
    }
  } catch (error) {
    errorMsg.value = error?.message || __("فشل التحقق من الرمز")
  } finally {
    loading.value = false
  }
}

function cancel() {
  emit("cancelled")
  open.value = false
}
</script>
