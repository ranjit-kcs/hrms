<template>
  <div class="min-h-screen bg-gray-100 flex ">
    <div class="w-full sm:w-96 flex flex-col min-h-screen">
      
      <!-- Header -->
      <header
        class="flex items-center bg-white shadow-sm py-4 px-3 border-b sticky top-0 z-10"
      >
        <Button
          variant="ghost"
          class="!pl-0 hover:bg-white"
          @click="router.back()"
        >
          <FeatherIcon name="chevron-left" class="h-5 w-5" />
        </Button>

        <h2 class="text-xl font-semibold text-gray-900 ml-2">
          {{ __("Profile") }}
        </h2>
      </header>

      <!-- Content -->
      <div class="flex-1 px-4 py-6 overflow-y-auto">
        <!-- Profile -->
        <div class="flex flex-col items-center">
          <img
            v-if="user.data.user_image"
            class="h-24 w-24 rounded-full object-cover"
            :src="user.data.user_image"
          />

          <div
            v-else
            class="h-24 w-24 rounded-full bg-gray-300 flex items-center justify-center text-2xl font-bold text-gray-700"
          >
            {{ user.data.first_name[0] }}
          </div>

          <h3 class="mt-4 text-xl font-bold text-gray-900">
            {{ employee?.data?.employee_name }}
          </h3>

          <p class="text-sm text-gray-500">
            {{ employee?.data?.designation }}
          </p>
        </div>

        <!-- Menu -->
        <div class="bg-white rounded-xl mt-6 overflow-hidden shadow-sm">
          <div
            v-for="link in profileLinks"
            :key="link.title"
            @click="openInfoModal(link)"
            class="flex justify-between items-center px-4 py-4 border-b last:border-b-0 cursor-pointer"
          >
            <div class="flex items-center gap-3">
              <FeatherIcon
                :name="link.icon"
                class="h-5 w-5 text-gray-500"
              />
              <span class="text-gray-800">
                {{ link.title }}
              </span>
            </div>

            <FeatherIcon
              name="chevron-right"
              class="h-5 w-5 text-gray-400"
            />
          </div>
        </div>

        <!-- Settings -->
        <div
          v-if="allowPushNotifications"
          class="bg-white rounded-xl mt-4 overflow-hidden shadow-sm"
        >
          <router-link
            :to="{ name: 'Settings' }"
            class="flex justify-between items-center px-4 py-4"
          >
            <div class="flex items-center gap-3">
              <FeatherIcon
                name="settings"
                class="h-5 w-5 text-gray-500"
              />
              <span class="text-gray-800">
                {{ __("Settings") }}
              </span>
            </div>

            <FeatherIcon
              name="chevron-right"
              class="h-5 w-5 text-gray-400"
            />
          </router-link>
        </div>
      </div>

      <!-- Bottom Logout Button -->
      <div class="p-4 bg-gray-100">
        <Button
          @click="logout"
          variant="outline"
          theme="red"
          class="w-full py-4"
        >
          <template #prefix>
            <FeatherIcon name="log-out" class="w-4" />
          </template>

          {{ __("Log Out") }}
        </Button>
      </div>
    </div>

    <!-- Modal -->
    <div
      v-if="isInfoModalOpen"
      class="fixed inset-0 bg-black/40 z-50 flex items-end justify-center"
      @click.self="closeInfoModal"
    >
      <div
        class="bg-white w-full sm:w-96 rounded-t-2xl p-4 max-h-[85vh] overflow-y-auto"
      >
        <ProfileInfoModal
          :title="selectedItem.title"
          :data="
            selectedItem.fields.map((field) => {
              const [label, fieldtype] = getFieldInfo(field)

              return {
                fieldname: field,
                value: employeeDoc.doc[field],
                label,
                fieldtype,
              }
            })
          "
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject, ref, onMounted, onBeforeUnmount } from "vue"
import { useRouter } from "vue-router"
import { IonModal, IonPage, IonContent } from "@ionic/vue"
import { FeatherIcon, createDocumentResource, createResource } from "frappe-ui"

import { showErrorAlert } from "@/utils/dialogs"
import { formatCurrency } from "@/utils/formatters"

import ProfileInfoModal from "@/components/ProfileInfoModal.vue"

import { arePushNotificationsEnabled } from "@/data/notifications"

const DOCTYPE = "Employee"

const socket = inject("$socket")
const session = inject("$session")
const user = inject("$user")
const employee = inject("$employee")
const __ = inject("$translate")

const router = useRouter()

const profileLinks = [
	{
		icon: "user",
		title: __("Employee Details"),
		fields: [
			"employee_name",
			"employee_number",
			"gender",
			"date_of_birth",
			"date_of_joining",
			"blood_group",
		],
	},
	{
		icon: "file",
		title: __("Company Information"),
		fields: [
			"company",
			"department",
			"designation",
			"branch",
			"grade",
			"reports_to",
			"employment_type",
		],
	},
	{
		icon: "book",
		title: __("Contact Information"),
		fields: [
			"cell_number",
			"personal_email",
			"company_email",
			"preferred_email",
		],
	},
	{
		icon: "dollar-sign",
		title: __("Salary Information"),
		fields: [
			"ctc",
			"payroll_cost_center",
			"pan_number",
			"provident_fund_account",
			"salary_mode",
			"bank_name",
			"bank_ac_no",
			"ifsc_code",
			"micr_code",
			"iban",
		],
	},
]

const isInfoModalOpen = ref(false)
const selectedItem = ref(null)

const allowPushNotifications = computed(
	() =>
		window.frappe?.boot.push_relay_server_url &&
		arePushNotificationsEnabled.data
)

const openInfoModal = async (request) => {
	selectedItem.value = request
	isInfoModalOpen.value = true
}

const closeInfoModal = async (_request) => {
	isInfoModalOpen.value = false
	selectedItem.value = null
}

const employeeDoc = createDocumentResource({
	doctype: DOCTYPE,
	name: employee.data.name,
	fields: "*",
	auto: true,
	transform: (data) => {
		data.ctc = formatCurrency(data.ctc, data.salary_currency)
		return data
	},
})

const employeeDocType = createResource({
	url: "hrms.api.get_doctype_fields",
	params: { doctype: DOCTYPE },
	auto: true,
})

const getFieldInfo = (fieldname) => {
	const field = employeeDocType.data.find(
		(field) => field.fieldname === fieldname
	)
	return [__(field?.label, null, "Employee"), field?.fieldtype]
}

const logout = async () => {
	try {
		await session.logout.submit()
	} catch (e) {
		const msg = "An error occurred while attempting to log out!"
		console.error(msg, e)
		showErrorAlert(msg)
	}
}

onMounted(() => {
	socket.emit("doctype_subscribe", DOCTYPE)
	socket.on("list_update", (data) => {
		if (data.doctype === DOCTYPE && data.name === employee.data.name) {
			employeeDoc.reload()
		}
	})
})

onBeforeUnmount(() => {
	socket.emit("doctype_unsubscribe", DOCTYPE)
	socket.off("list_update")
})
</script>
