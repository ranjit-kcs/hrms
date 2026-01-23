<template>
	<!-- BLOCK APP UNTIL INSTALLED -->
	<div
		v-if="showInstallPrompt"
		class="fixed inset-0 z-[9999] flex flex-col justify-center items-center px-4 bg-gray-50"
	>
		<h2 class="text-lg font-bold mb-2">
			{{ __("Install Frappe HR") }}
		</h2>

		<p class="text-sm text-gray-700 text-center mb-6">
			{{ __("You must install this app to continue.") }}
		</p>

		<!-- ANDROID / DESKTOP INSTALL -->
		<Button
			v-if="canInstall && !isIos"
			variant="solid"
			class="py-5 w-full max-w-sm"
			@click="install"
		>
			<template #prefix>
				<FeatherIcon name="download" class="w-4" />
			</template>
			{{ __("Install App") }}
		</Button>

		<!-- iOS MESSAGE -->
		<div
			v-if="isIos"
			class="mt-6 w-full max-w-sm rounded py-5 bg-blue-100 drop-shadow-xl"
		>
			<div class="px-3 mb-2 font-bold text-gray-900">
				{{ __("Install on iPhone") }}
			</div>

			<div class="text-xs text-gray-800 px-3 flex flex-col gap-2">
				<span>
					{{ __("Get the app on your iPhone for easy access & a better experience") }}
				</span>
				<span class="inline-flex items-center">
					<span>Tap&nbsp;</span>
					<FeatherIcon name="share" class="h-4 w-4 text-blue-600" />
					<span>&nbsp;and then “Add to Home Screen”</span>
				</span>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { Button, FeatherIcon } from "frappe-ui"
import { deferredPrompt, canInstall } from "@/utils/pwaInstall"

// State
const showInstallPrompt = ref(true)

// Detect iOS
const isIos = /iphone|ipad|ipod/i.test(navigator.userAgent)

// Detect standalone
const isInstalled = () =>
	window.matchMedia("(display-mode: standalone)").matches ||
	window.navigator.standalone === true

onMounted(() => {
	// If already installed → unlock app
	if (isInstalled()) {
		showInstallPrompt.value = false
	}

	// When app gets installed
	window.addEventListener("appinstalled", () => {
		showInstallPrompt.value = false
		canInstall.value = false
	})
})

async function install() {
	if (!deferredPrompt.value) return

	await deferredPrompt.value.prompt()
	const result = await deferredPrompt.value.userChoice

	if (result.outcome === "accepted") {
		showInstallPrompt.value = false
	}
}
</script>