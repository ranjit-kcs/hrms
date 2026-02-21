<template>
  <ion-page>
    <BaseLayout>
      <template #body>
        <div class="flex flex-col items-center my-7 p-4 gap-7">
          <CheckInPanel :refreshKey="refreshKey"/>
          <QuickLinks :items="quickLinks" :title="__('Quick Links')" />
          <RequestPanel />
        </div>
      </template>
    </BaseLayout>
  </ion-page>
</template>

<script setup>
import { IonPage,onIonViewWillEnter } from "@ionic/vue"
import { inject, markRaw,ref } from "vue"

import CheckInPanel from "@/components/CheckInPanel.vue"
import QuickLinks from "@/components/QuickLinks.vue"
import BaseLayout from "@/components/BaseLayout.vue"
import RequestPanel from "@/components/RequestPanel.vue"

import AttendanceIcon from "@/components/icons/AttendanceIcon.vue"
import ShiftIcon from "@/components/icons/ShiftIcon.vue"
import LeaveIcon from "@/components/icons/LeaveIcon.vue"
import ExpenseIcon from "@/components/icons/ExpenseIcon.vue"
import EmployeeAdvanceIcon from "@/components/icons/EmployeeAdvanceIcon.vue"
import SalaryIcon from "@/components/icons/SalaryIcon.vue"

const __ = inject("$translate")
const refreshKey = ref(0)
onIonViewWillEnter(() => {
  refreshKey.value++   // trigger refresh
})
const quickLinks = [
  {
    icon: markRaw(AttendanceIcon),
    title: __("Request Attendance"),
    route: "AttendanceRequestFormView",
  },
  {
    icon: markRaw(ShiftIcon),
    title: __("Request a Shift"),
    route: "ShiftRequestFormView",
  },
  {
    icon: markRaw(LeaveIcon),
    title: __("Request Leave"),
    route: "LeaveApplicationFormView",
  },
  {
    icon: markRaw(ExpenseIcon),
    title: __("Claim an Expense"),
    route: "ExpenseClaimFormView",
  },
  {
    icon: markRaw(EmployeeAdvanceIcon),
    title: __("Request an Advance"),
    route: "EmployeeAdvanceFormView",
  },
  {
    icon: markRaw(SalaryIcon),
    title: __("View Salary Slips"),
    route: "SalarySlipsDashboard",
  },
]
</script>
