<template>
  <!-- Bottom Sheet Modal -->
  <div
    v-if="isOpen || showModal"
    class="fixed inset-0 z-[10000] !mt-0 flex items-end justify-center"
  >
    <!-- Backdrop -->
    <div
      class="absolute inset-0 bg-black opacity-30 cursor-pointer"
      @click="closeModal"
    />

    <!-- Sheet Content -->
    <div class="relative w-full sm:w-96 bg-white rounded-t-xl z-10">
      <slot name="actionSheet" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue"

const props = defineProps({
  trigger: {
    type: String,
    required: false,
  },
  isOpen: {
    type: Boolean,
    required: false,
    default: false,
  },
})

const emit = defineEmits(["did-dismiss"])
const showModal = ref(false)

// Support trigger-based opening via button id
function handleTriggerClick() {
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  emit("did-dismiss")
}

// Watch external isOpen prop
watch(
  () => props.isOpen,
  (val) => {
    if (!val) {
      showModal.value = false
      emit("did-dismiss")
    }
  }
)

// Attach click listener to trigger element by id (if provided)
watch(
  () => props.trigger,
  (triggerId) => {
    if (!triggerId) return
    const el = document.getElementById(triggerId)
    if (el) {
      el.addEventListener("click", handleTriggerClick)
    }
  },
  { immediate: true }
)

defineExpose({ closeModal })
</script>