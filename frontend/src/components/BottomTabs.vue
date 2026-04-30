<template>
  <div class="bg-white shadow-md sm:w-96 py-2 pb-2">
    <div class="flex flex-row justify-around items-center">
      <router-link
        v-for="item in tabItems"
        :key="item.title"
        :to="item.route"
        class="flex flex-col items-center gap-1 px-3 py-1 text-xs transition active:scale-95"
        :class="[
          route.path === item.route
            ? 'text-gray-900 font-semibold'
            : 'text-gray-500 font-normal',
        ]"
      >
        <component :is="item.icon" class="h-5 w-5" />
        <span>{{ item.title }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { inject } from "vue"
import { useRoute } from "vue-router"

import HomeIcon from "@/components/icons/HomeIcon.vue"
import LeaveIcon from "@/components/icons/LeaveIcon.vue"
import ExpenseIcon from "@/components/icons/ExpenseIcon.vue"
import SalaryIcon from "@/components/icons/SalaryIcon.vue"
import AttendanceIcon from "@/components/icons/AttendanceIcon.vue"

const __ = inject("$translate")
const route = useRoute()

const tabItems = [
  {
    icon: HomeIcon,
    title: __("Home"),
    route: "/home",
  },
  {
    icon: AttendanceIcon,
    title: __("Attendance"),
    route: "/dashboard/attendance",
  },
  {
    icon: LeaveIcon,
    title: __("Leaves"),
    route: "/dashboard/leaves",
  },
  {
    icon: ExpenseIcon,
    title: __("Expenses"),
    route: "/dashboard/expense-claims",
  },
  {
    icon: SalaryIcon,
    title: __("Salary"),
    route: "/dashboard/salary-slips",
  },
]
</script>