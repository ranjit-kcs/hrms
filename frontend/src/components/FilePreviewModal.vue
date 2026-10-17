<template>
  <div class="fixed inset-0 z-[10000] flex flex-col bg-white">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b bg-white shadow-sm">
      <h2 class="text-sm font-semibold text-gray-800 truncate">
        {{ filename }} - {{ __("File Preview") }}
      </h2>
      <button
        class="text-sm text-blue-600 font-medium"
        @click="emit('close')"
      >
        {{ __("Close") }}
      </button>
    </div>

    <!-- Content -->
    <div class="bg-white flex-1 w-full overflow-auto touch-pinch-zoom">
      <img v-if="isImageFile" :src="src" class="h-auto image-preview" />
      <iframe v-else :src="src" class="w-full h-full"></iframe>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, inject } from "vue"

const __ = inject("$translate")

const props = defineProps({
  file: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(["close"])

const filename = computed(() => {
  return props.file.file_name || props.file.name
})

const src = computed(() => {
  return props.file.file_url
    ? props.file.file_url
    : URL.createObjectURL(props.file)
})

const isImageFile = computed(() => {
  return /\.(gif|jpg|jpeg|tiff|png|svg)$/i.test(filename.value)
})

onBeforeUnmount(() => {
  URL.revokeObjectURL(src.value)
})
</script>

<style scoped>
.image-preview {
  image-orientation: from-image;
}
</style>