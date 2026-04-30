<template>
  <div class="flex flex-col h-screen">
    <div class="flex-1 overflow-y-auto">
      <router-view />
    </div>
    <BottomTabs />
  </div>
</template>

<script setup>
import BottomTabs from "@/components/BottomTabs.vue"
</script>