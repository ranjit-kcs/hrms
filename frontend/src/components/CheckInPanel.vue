<template>
  <div class="flex flex-col bg-white rounded w-full py-6 px-4 border-none">
    <h2 class="text-lg font-bold text-gray-900">
      {{ __("Hey, {0} 👋", [employee?.data?.first_name]) }}
    </h2>

    <template v-if="settings.data?.allow_employee_checkin_from_mobile_app">
      <div class="font-medium text-sm text-gray-500 mt-1.5" v-if="lastLog">
        <span>
          {{ __("Last {0} was at {1}", [__(lastLogType), formatTimestamp(lastLog.time)]) }}
        </span>
        <span class="whitespace-pre"> &middot; </span>

        <router-link :to="{ name: 'EmployeeCheckinListView' }">
          <span class="underline">View List</span>
        </router-link>
      </div>

      <Button
        class="mt-4 mb-1 drop-shadow-sm py-5 text-base"
        @click="goToCheckinPage"
      >
        <template #prefix>
          <FeatherIcon
            :name="nextAction.action === 'IN' ? 'arrow-right-circle' : 'arrow-left-circle'"
            class="w-4"
          />
        </template>
        {{ nextAction.label }}
      </Button>
    </template>

    <div v-else class="font-medium text-sm text-gray-500 mt-1.5">
      {{ dayjs().format("ddd, D MMMM, YYYY") }}
    </div>
  </div>
</template>

<script setup>
import { createResource, createListResource, FeatherIcon,toast } from "frappe-ui"
import { computed, inject,onMounted,watch,ref } from "vue"
import { useRouter } from "vue-router"
import { formatTimestamp } from "@/utils/formatters"
import { useIonRouter ,onIonViewWillEnter} from "@ionic/vue"
import { getRuntimeConfig } from "@/utils/runtimeConfig";
import { getRuntimeURLConfig } from "../utils/runtimeURLConfig"
import { Device } from "@capacitor/device"


let azure_key = ref("")
let distance_url = ref("")
let distance_response = ref("")
let location_url = ref("")
let location_response = ref("")

onIonViewWillEnter(() => {
	console.log("view");
  checkins.reload()
  
})

const props = defineProps({
  refreshKey: Number,
})

watch(
  () => props.refreshKey,
  () => {
    checkins.reload()
	initAzure();
  }
)

const DOCTYPE = "Employee Checkin"

const ionRouter = useIonRouter()
const employee = inject("$employee")
const user = inject("$user")
const dayjs = inject("$dayjs")
const __ = inject("$translate")
const geofence = inject("$geofence")

const settings = createResource({
  url: "hrms.api.get_hr_settings",
  auto: true,
})
async function initAzure() {
  const config = await getRuntimeConfig();
  azure_key = config.AZURE_KEY;
  const url_config = await getRuntimeURLConfig();
  distance_url = url_config.distance_url;
  location_url = url_config.location_url;
  distance_response = url_config.distance_response;
  location_response = url_config.location_response;
}
const checkins = createListResource({
  doctype: DOCTYPE,
  fields: ["name", "employee", "employee_name", "log_type", "time", "device_id", "location", "latitude", "longitude", "reference_dt", "reference_dn"],
  filters: { employee: employee.data.name },
  orderBy: "time desc",
})

const lastLog = computed(() => {
  if (checkins.list.loading || !checkins.data) return null
  return checkins.data[0]
})

const lastLogType = computed(() => {
  return lastLog?.value?.log_type === "IN" ? "check-in" : "check-out"
})

// const nextAction = computed(() => {
//   return lastLog?.value?.log_type === "IN"
//     ? { action: "OUT", label: __("Check Out") }
//     : { action: "IN", label: __("Check In") }
// })
const nextAction = computed(() => {
  const log = lastLog?.value;
  if (!log || !log.time) {
    return { action: "IN", label: __("Check In") };
  }

  const lastLogDate = log.time.split(" ")[0]; // YYYY-MM-DD
  const todayDate = new Date().toISOString().split("T")[0];

  // If last log was IN but not today → forgot checkout → allow Check In
  if (log.log_type === "IN" && lastLogDate === todayDate) {
    return { action: "OUT", label: __("Check Out") };
  }

  return { action: "IN", label: __("Check In") };
});

async function goToCheckinPage() {
  const info = await Device.getInfo()
  toast({
    title: info.platform,   // will show "web" / "android" / "ios"
    text: "hello test",
    icon: "info",
    position: "top-center",
    timeout: 3000,
  })
  if (info.platform === "web") {
    toast({
      title: __("Not Allowed"),
      text: __("Check-in allowed only from the HRMS mobile app"),
      icon: "x-circle",
      position: "top-center",
      timeout: 3000,
    })
    return
  }
  if(geofence.data.length === 0 && employee.data.field_employee !='Yes'){
		toast({
          title: __("Required"),
          text: __("Geofence is Missing, Contact HR",),
          icon: "check-circle",
          position: "top-center",
        })
    return; 
  }
	if (!azure_key) {
		toast({
          title: __("Required"),
          text: __("Azure Key Miss, Contact HR",),
          icon: "check-circle",
          position: "top-center",
        })
    return; 
  }
  if (!distance_url) {
	toast({
          title: __("Required"),
          text: __("Distance URL value is Missing, Contact HR",),
          icon: "check-circle",
          position: "top-center",
        })
    return;
  }
  if (!location_url) {
	toast({
          title: __("Required"),
          text: __("Location URL value is Missing,, Contact HR",),
          icon: "check-circle",
          position: "top-center",
        })

    return;
  }
  if (!distance_response) {
	toast({
          title: __("Required"),
          text: __("Distance Response value is Missing, Contact HR",),
          icon: "check-circle",
          position: "top-center",
        })
    return;
  }
  if (!location_response) {
	toast({
          title: __("Required"),
          text: __("Location Response value is Missing, Contact HR",),
          icon: "check-circle",
          position: "top-center",
        })
    return;
  }
    if (!user?.data?.user_image) {
		toast({
          title: __("Required"),
          text: __("Photo is Missing, Contact HR",),
          icon: "check-circle",
          position: "top-center",
        })
    return
  }
	if (settings.data?.allow_geolocation_tracking) {
    ionRouter.push({
  name: "CheckinConfirm",
  query: {
    action: nextAction.value.action,
  },
})
  }else{
	toast({
          title: __("Required"),
          text: __("Allow Geolocation is Not Enabled",),
          icon: "check-circle",
          position: "bottom-center",
        })
  }
  

}
</script>
