<template>
  <div class="min-h-screen bg-white flex flex-col justify-center">
    <!-- Login Header -->
    <div class="flex flex-col mx-auto gap-3 items-center">
      <FrappeHRLogo class="h-8 w-8" />

      <div class="text-3xl font-semibold text-gray-900 text-center">
        {{ __("Login to Frappe HR") }}
      </div>
    </div>

    <!-- Login Form -->
    <div class="mx-auto mt-10 w-full px-8 sm:w-96">
      <form class="flex flex-col space-y-4" @submit.prevent="submit">
        <Input
          :label="__('Email')"
          :placeholder="__('johndoe@mail.com')"
          v-model="email"
          type="text"
          autocomplete="username"
        />

        <Input
          :label="__('Password')"
          type="password"
          placeholder="••••••"
          v-model="password"
          autocomplete="current-password"
        />

        <ErrorMessage :message="errorMessage" />

        <Button
          :loading="session.login.loading"
          variant="solid"
          class="disabled:bg-gray-700 disabled:text-white !mt-6"
        >
          {{ __("Login") }}
        </Button>
      </form>

      <!-- OAuth Providers -->
      <template v-if="authProviders.data?.length">
        <div class="text-center text-sm text-gray-600 my-4">or</div>

        <div class="space-y-4">
          <a
            v-for="provider in authProviders.data"
            :key="provider.name"
            class="flex items-center justify-center gap-2 transition-colors focus:outline-none text-gray-800 bg-gray-100 hover:bg-gray-200 active:bg-gray-300 focus-visible:ring focus-visible:ring-gray-400 h-10 text-base px-3 rounded"
            :href="provider.auth_url"
          >
            <img
              class="h-4 w-4"
              :src="provider.icon"
              :alt="provider.provider_name"
            />

            <span>
              Login with {{ provider.provider_name }}
            </span>
          </a>
        </div>
      </template>
    </div>

    <!-- Reset Password Dialog -->
    <Dialog v-model="resetPassword.showDialog">
      <template #body-title>
        <h2 class="text-lg font-bold">
          {{ __("Reset Password") }}
        </h2>
      </template>

      <template #body-content>
        <p>
          {{
            __("Your password has expired. Please reset your password to continue")
          }}
        </p>
      </template>

      <template #actions>
        <a
          class="inline-flex items-center justify-center gap-2 text-white bg-gray-900 hover:bg-gray-800 h-10 px-4 rounded"
          :href="resetPassword.link"
          target="_blank"
        >
          {{ __("Go to Reset Password page") }}
        </a>
      </template>
    </Dialog>

    <!-- OTP Dialog -->
    <Dialog v-model="otp.showDialog">
      <template #body-title>
        <h2 class="text-lg font-bold">
          {{ __("OTP Verification") }}
        </h2>
      </template>

      <template #body-content>
        <p class="mb-4" v-if="otp.verification.prompt">
          {{ otp.verification.prompt }}
        </p>

        <form class="flex flex-col space-y-4" @submit.prevent="submit">
          <Input
            :label="__('OTP Code')"
            type="text"
            placeholder="000000"
            v-model="otp.code"
            autocomplete="one-time-code"
          />

          <ErrorMessage :message="errorMessage" />

          <Button
            :loading="session.otp.loading"
            variant="solid"
            class="disabled:bg-gray-700 disabled:text-white !mt-6"
          >
            {{ __("Verify") }}
          </Button>
        </form>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { inject, reactive, ref } from "vue"
import {
  Input,
  Button,
  ErrorMessage,
  Dialog,
  createResource,
} from "frappe-ui"

import FingerprintJS from "@fingerprintjs/fingerprintjs"
import FrappeHRLogo from "@/components/icons/FrappeHRLogo.vue"

const email = ref("")
const password = ref("")
const errorMessage = ref("")

const session = inject("$session")
const __ = inject("$translate")

const resetPassword = reactive({
  showDialog: false,
  link: "",
})

const otp = reactive({
  showDialog: false,
  tmp_id: "",
  code: "",
  verification: {},
})

async function getDeviceId() {
  let id = localStorage.getItem("hrms_device_id")

  if (id) return id

  const fp = await FingerprintJS.load()
  const result = await fp.get()

  id = result.visitorId

  localStorage.setItem("hrms_device_id", id)

  return id
}

async function submit() {
  errorMessage.value = ""

  try {
    const deviceId = await getDeviceId()
    let response

    if (otp.showDialog) {
      response = await session.otp(otp.tmp_id, otp.code)
    } else {
      const r = await fetch("/api/method/hrms.api.custom_login.login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email.value,
          password: password.value,
          device_id: deviceId,
        }),
      })

      const json = await r.json()

      if (json._server_messages) {
        try {
          const msgList = JSON.parse(json._server_messages)
          const firstMsg = JSON.parse(msgList[0])
          errorMessage.value = firstMsg.message
        } catch {
          errorMessage.value = "Login failed."
        }
        return
      }

      if (json.exc || json.exception) {
        errorMessage.value =
          json.message || "Something went wrong."
        return
      }

      if (
        json.message &&
        typeof json.message === "string"
      ) {
        if (
          json.message.includes("Invalid credentials") ||
          json.message.includes("already logged in")
        ) {
          errorMessage.value = json.message
          return
        }
      }

      if (json.exc_type === "ValidationError") {
        errorMessage.value = json.message
        return
      }

      response = json.message
    }

    if (response.message === "Password Reset") {
      resetPassword.showDialog = true
      resetPassword.link = response.redirect_to
    } else {
      resetPassword.showDialog = false
      resetPassword.link = ""
    }

    if (response.verification) {
      if (response.verification.setup) {
        otp.showDialog = true
        otp.tmp_id = response.tmp_id
        otp.verification = response.verification
      } else {
        window.open(
          "/login?redirect-to=" +
            encodeURIComponent(window.location.pathname),
          "_blank"
        )
      }
    }

    if (
      response.status === "first_login" ||
      response.status === "device_match"
    ) {
      window.location.href = "/hrms/home"
    }
  } catch (error) {
    if (error.messages) {
      errorMessage.value = error.messages.join("\n")
    } else {
      errorMessage.value = "Login failed. Try again."
    }
  }
}

const authProviders = createResource({
  url: "hrms.api.oauth.oauth_providers",
  auto: true,
})
</script>