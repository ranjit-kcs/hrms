<template>
	<ion-app>
		<InstallPrompt />
		<ion-router-outlet id="main-content" />
		<Toasts />

		
	</ion-app>
</template>

<script setup>
import { onMounted } from "vue"
import { IonApp, IonRouterOutlet } from "@ionic/vue"

import { Toasts } from "frappe-ui"

import InstallPrompt from "@/components/InstallPrompt.vue"
import { showNotification } from "@/utils/pushNotifications"

onMounted(() => {
	window?.frappePushNotification?.onMessage((payload) => {
		showNotification(payload)
	})
})
window.addEventListener("beforeinstallprompt", (e) => {
	e.preventDefault()
	window.__deferredPrompt = e
})

</script>
