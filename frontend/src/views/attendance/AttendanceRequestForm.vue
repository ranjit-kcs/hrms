<template>
  <div class="page-container">
    <div class="content-container">
      <FormView
        v-if="formFields.data"
        class="form-wrapper"
        doctype="Attendance Request"
        v-model="attendanceRequest"
        :isSubmittable="true"
        :fields="formFields.data"
        :id="props.id"
        @validateForm="validateForm"
      />
    </div>
  </div>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { ref, watch, inject } from "vue"
import FormView from "@/components/FormView.vue"

const employee = inject("$employee")
const __ = inject("$translate")

const props = defineProps({
  id: String,
})

const attendanceRequest = ref({})

const formFields = createResource({
  url: "hrms.api.get_doctype_fields",
  params: { doctype: "Attendance Request" },
  auto: true,
  transform(data) {
    if (props.id) return data

    return data.filter(
      (field) =>
        !["employee", "employee_name", "status", "company"].includes(
          field.fieldname
        )
    )
  },
})

watch(
  () => attendanceRequest.value.from_date,
  (from_date) => {
    if (!attendanceRequest.value.to_date) {
      attendanceRequest.value.to_date = from_date
    }
  }
)

watch(
  () => [attendanceRequest.value.from_date, attendanceRequest.value.to_date],
  ([from_date, to_date]) => {
    if (!(from_date && to_date)) return

    const from_date_field = formFields.data.find(
      (field) => field.fieldname === "from_date"
    )

    if (from_date_field) {
      from_date_field.error_message =
        from_date > to_date
          ? __("To Date cannot be before From Date")
          : ""
    }
  }
)

function validateForm() {
  attendanceRequest.value.employee = employee.data.name
}
</script>
