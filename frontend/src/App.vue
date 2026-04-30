<template>
  <div id="app">
    <router-view />
    <Toasts />
    <InstallPrompt />
  </div>
</template>

<script setup>
import { onMounted } from "vue"
import { Toasts } from "frappe-ui"
import InstallPrompt from "@/components/InstallPrompt.vue"
import { showNotification } from "@/utils/pushNotifications"

onMounted(() => {
  window?.frappePushNotification?.onMessage((payload) => {
    showNotification(payload)
  })
})
</script>