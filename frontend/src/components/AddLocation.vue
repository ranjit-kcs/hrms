<template>
  <div class="flex flex-col bg-white rounded w-full py-6 px-4 border-none">
    <h2 class="text-lg font-bold text-gray-900">
      {{ __("Add New Location") }}
    </h2>

    <div class="font-medium text-sm text-gray-500 mt-1.5">
      {{ __("Add new client or Other locations") }}
    </div>

    <Button
      class="mt-4 mb-1 drop-shadow-sm py-5 text-base"
      @click="openDialog"
    >
      <template #prefix>
        <FeatherIcon name="map-pin" class="w-4" />
      </template>

      {{ __("Add Location") }}
    </Button>

    <!-- Popup -->
    <div
      v-if="showDialog"
      class="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-xl w-[90%] max-w-md p-5 shadow-xl">
        <h3 class="text-lg font-bold text-gray-900 mb-4">
          {{ __("Add New Location") }}
        </h3>

        <!-- Location Name -->
        <div class="mb-2">
          <label class="text-sm font-medium text-gray-700">
            {{ __("Location Name") }}
          </label>

          <!-- <input
            v-model="location"
            type="text"
            class="w-full border rounded-lg px-3 py-2 mt-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            :placeholder="__('Enter location name')"
          /> -->
          <FormControl type="text" size="sm" variant="outline" placeholder="Enter Location Name" v-model="location" :input-class="inputCls" />

        </div>

        <!-- Latitude -->
        <div class="mb-2">
          <label class="text-sm font-medium text-gray-700">
            {{ __("Latitude") }}
          </label>

          <!-- <input
            v-model="latitude"
            type="text"
            readonly
            class="w-full border rounded-lg px-3 py-2 mt-1 bg-gray-100"
          /> -->
          <FormControl type="text" size="sm" variant="outline" placeholder="Enter Latitude" v-model="latitude" :input-class="inputCls" />

        </div>

        <!-- Longitude -->
        <div class="mb-4">
          <label class="text-sm font-medium text-gray-700">
            {{ __("Longitude") }}
          </label>

          <!-- <input
            v-model="longitude"
            type="text"
            readonly
            class="w-full border rounded-lg px-3 py-2 mt-1 bg-gray-100"
          /> -->
          <FormControl type="text" size="sm" variant="outline" placeholder="Enter Longitude" v-model="longitude" :input-class="inputCls" />
              
        </div>

        <!-- Buttons -->
        <div class="flex justify-end gap-3 mt-6">
          <Button appearance="secondary" @click="closeDialog">
            {{ __("Cancel") }}
          </Button>

          <Button @click="createLocation" :loading="loading">
            {{ __("Add") }}
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon, toast } from "frappe-ui"
import { ref,inject } from "vue"
import { useRouter } from "vue-router"
import { FormControl } from "frappe-ui"

const __ = inject("$translate")

const showDialog = ref(false)

const location = ref("")
const latitude = ref("")
const longitude = ref("")

const loading = ref(false)

function openDialog() {
  showDialog.value = true
  fetchCurrentLocation()
}

function closeDialog() {
  showDialog.value = false

  location.value = ""
  latitude.value = ""
  longitude.value = ""
}

function fetchCurrentLocation() {
  if (!navigator.geolocation) {
    toast({
      title: __("Error"),
      text: __("Geolocation is not supported"),
      icon: "x-circle",
      position: "top-center",
    })

    return
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      latitude.value = position.coords.latitude
      longitude.value = position.coords.longitude
    },
    () => {
      toast({
        title: __("Error"),
        text: __("Unable to fetch current location"),
        icon: "x-circle",
        position: "top-center",
      })
    }
  )
}

async function createLocation() {
  if (!location.value) {
    toast({
      title: __("Required"),
      text: __("Please enter location name"),
      icon: "x-circle",
      position: "top-center",
    })

    return
  }

  if (!latitude.value || !longitude.value) {
    toast({
      title: __("Required"),
      text: __("Latitude and Longitude missing"),
      icon: "x-circle",
      position: "top-center",
    })

    return
  }

  loading.value = true

  try {
    const response = await fetch(
      "/api/method/hrms.api.hr_api.create_location",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          location: location.value,
          latitude: latitude.value,
          longitude: longitude.value,
        }),
      }
    )

    const data = await response.json()

    if (data.message) {
      toast({
        title: __("Success"),
        text: __("Location created successfully"),
        icon: "check-circle",
        position: "top-center",
      })

      closeDialog()
    } else {
      throw new Error()
    }
  } catch (e) {
    toast({
      title: __("Error"),
      text: __("Failed to create location"),
      icon: "x-circle",
      position: "top-center",
    })
  } finally {
    loading.value = false
  }
}
</script>