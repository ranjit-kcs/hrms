<template>
  <div class="flex flex-col bg-white rounded mt-5 overflow-auto" v-if="props.items?.length">
    <div
      class="flex flex-row p-3.5 items-center justify-between border-b cursor-pointer"
      v-for="link in props.items"
      :key="link.name"
      @click="openRequestModal(link)"
    >
      <component
        :is="props.component || link.component"
        :doc="link"
        :workflowStateField="link.workflow_state_field"
        :isTeamRequest="props.teamRequests"
      />
    </div>

    <router-link
      v-if="props.addListButton"
      :to="{ name: props.listButtonRoute }"
    >
      <Button
        variant="ghost"
        class="w-full !text-gray-600 py-6 text-sm border-none bg-white hover:bg-white"
      >
        {{ __("View List") }}
      </Button>
    </router-link>
  </div>
  <EmptyState :message="emptyStateMessage || __('You have no requests')" v-else />

  <!-- Bottom Sheet Modal (replaces ion-modal) -->
  <div
    v-if="isRequestModalOpen"
    class="fixed inset-0 z-50 flex items-end justify-center"
    @click.self="closeRequestModal"
  >
    <!-- Backdrop -->
    <div
      class="absolute inset-0 bg-black opacity-30 cursor-pointer"
      @click="closeRequestModal"
    />

    <!-- Sheet -->
    <div class="relative w-full sm:w-96 bg-white rounded-t-xl overflow-y-auto max-h-[90vh] z-10">
      <RequestActionSheet
        :fields="fieldsMap[selectedRequest?.doctype]"
        v-model="selectedRequest"
        @dismiss="closeRequestModal"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from "vue"
import RequestActionSheet from "@/components/RequestActionSheet.vue"

import {
  LEAVE_FIELDS,
  EXPENSE_CLAIM_FIELDS,
  ATTENDANCE_REQUEST_FIELDS,
  SHIFT_REQUEST_FIELDS,
  SHIFT_FIELDS,
} from "@/data/config/requestSummaryFields"

const __ = inject("$translate")

const props = defineProps({
  component: {
    type: Object,
  },
  items: {
    type: Array,
  },
  teamRequests: {
    type: Boolean,
    default: false,
  },
  addListButton: {
    type: Boolean,
    default: false,
  },
  listButtonRoute: {
    type: String,
    default: "",
  },
  emptyStateMessage: {
    type: String,
    default: "",
  },
})

const fieldsMap = {
  "Leave Application": LEAVE_FIELDS,
  "Expense Claim": EXPENSE_CLAIM_FIELDS,
  "Attendance Request": ATTENDANCE_REQUEST_FIELDS,
  "Shift Request": SHIFT_REQUEST_FIELDS,
  "Shift Assignment": SHIFT_FIELDS,
}

const isRequestModalOpen = ref(false)
const selectedRequest = ref(null)

const openRequestModal = async (request) => {
  selectedRequest.value = request
  isRequestModalOpen.value = true
}

const closeRequestModal = async () => {
  isRequestModalOpen.value = false
  selectedRequest.value = null
}
</script>