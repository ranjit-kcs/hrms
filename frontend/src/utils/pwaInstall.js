import { ref } from "vue"

export const deferredPrompt = ref(null)
export const canInstall = ref(false)

window.addEventListener("beforeinstallprompt", (e) => {
	e.preventDefault()
	deferredPrompt.value = e
	canInstall.value = true
	console.log("PWA install prompt captured")
})
