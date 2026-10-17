<template>
  <div class="flex flex-col h-full w-full sm:w-96">
    <!-- Header -->
    <div class="w-full bg-white shadow-sm p-4 shrink-0">
      <div class="flex flex-row justify-between items-center">
        <div class="flex flex-row items-center gap-2">
          <h2 class="text-xl font-bold text-gray-900">
            {{ props.pageTitle || __("Frappe HR") }}
          </h2>
        </div>
        <div class="flex flex-row items-center gap-3 ml-auto">
          <router-link
            :to="{ name: 'Notifications' }"
            class="flex flex-col items-center"
          >
            <span class="relative inline-block">
              <FeatherIcon name="bell" class="h-6 w-6" />
              <span
                v-if="unreadNotificationsCount.data"
                class="absolute top-0 right-0.5 inline-block w-2 h-2 bg-red-600 rounded-full border border-white"
              />
            </span>
          </router-link>
          <router-link
            :to="{ name: 'Profile' }"
            class="flex flex-col items-center"
          >
            <Avatar
              :image="user.data.user_image"
              :label="user.data.first_name"
              size="xl"
            />
          </router-link>
        </div>
      </div>
    </div>

    <!-- Body -->
    <div class="flex-1 overflow-y-auto">
      <slot name="body" />
    </div>
  </div>
</template>

<script setup>
import { inject } from "vue"
import { FeatherIcon, Avatar } from "frappe-ui"
import { unreadNotificationsCount } from "@/data/notifications"

const __ = inject("$translate")
const user = inject("$user")

const props = defineProps({
  pageTitle: {
    type: String,
    required: false,
    default: "",
  },
})
</script>