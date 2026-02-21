<template>
  <ion-page>
    <BaseLayout>
      <template #body>
        <div class="min-h-screen bg-white flex flex-col p-4 gap-5">
          <div class="w-full flex justify-start mb-4">
            <img :src="BackButton" class="w-6 h-6 cursor-pointer" @click="goBack" />

          </div>

          <!-- Camera Preview -->
          <div class="w-full flex justify-center">
            <video ref="videoRef" autoplay playsinline class="w-full max-w-sm rounded-lg border"></video>
          </div>

          <div class="flex flex-col items-center gap-2 mt-2">
            <!-- Status Message -->
            <div class="text-sm text-center px-3 py-2 rounded-lg bg-gray-100 text-gray-700 shadow-sm w-full max-w-xs">
              {{ statusMsg }}
            </div>

            <!-- Location Status -->
            <template v-if="settings.data?.allow_geolocation_tracking">
              <span v-if="locationStatus"
                class="text-sm text-center px-3 py-2 rounded-lg bg-gray-100 text-gray-700 shadow-sm w-full max-w-xs">
                <img :src="locationIcon"
                  class="w-4 h-4 inline-block mr-1 filter brightness-0 saturate-100 invert-[34%] sepia-[94%] saturate-[1352%] hue-rotate-[190deg] brightness-[95%] contrast-[101%]" />
                {{ locationStatus }}
              </span>
            </template>
          </div>
          <div class="text-center">
            <Checkbox v-if="action === 'OUT' && faceMatched" :value="true" v-model="forgetCheckOut"
              label="Forget to CheckOut" class="mt-0" />

          </div>

          <div class="w-full grid grid-cols-1 md:grid-cols-1 gap-4" v-if="action === 'IN' || forgetCheckOut">
            <div v-if="field_employee === 'Yes' && isCheckOut">
              <label class="form-label text-xs">Type</label>
              <FormControl type="autocomplete" :options="[
                { label: 'Lead', value: 'Lead' },
                { label: 'Opportunity', value: 'Opportunity' },
                { label: 'Hospital', value: 'Hospital' },
                { label: 'CAR', value: 'CAR' }
              ]" size="sm" variant="outline" placeholder="Select Type" v-model="typeofCheckIn"
                :input-class="'bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600'"
                required />
            </div>

            <div v-if="typeofCheckIn?.value === 'Lead'">
              <label class="form-label text-xs">Lead</label>
              <FormControl type="autocomplete" :options="leadOptions" size="sm" variant="outline"
                placeholder="Select Lead" v-model="leadValue" required
                :input-class="'bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600'" />
            </div>



            <div v-if="typeofCheckIn?.value === 'Opportunity'">
              <label class="form-label text-xs">Opportunity</label>
              <FormControl type="autocomplete" :options="OpportunityOptions" size="sm" variant="outline"
                placeholder="Select Opportunity" v-model="opportunityValue"
                :input-class="'bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600'" />
            </div>
            <div v-if="typeofCheckIn?.value === 'Hospital'">
              <label class="form-label text-xs">Hospital</label>
              <FormControl type="autocomplete" :options="HospitalOptions" size="sm" variant="outline"
                placeholder="Select Hospital" v-model="hospitalValue"
                :input-class="'bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600'" />
            </div>

            <div v-if="typeofCheckIn?.value === 'CAR'">
              <label class="form-label text-xs">CAR</label>
              <FormControl type="autocomplete" :options="CarOptions" size="sm" variant="outline"
                placeholder="Select CAR" v-model="carValue"
                :input-class="'bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600'" />
            </div>

          </div>
          <!-- ------------------------------------------------------------- -->
          <div v-if="showLeadModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
            <div class="bg-white p-5 rounded-lg w-80 shadow-lg">
              <h3 class="text-lg font-semibold mb-3">Create Lead</h3>
              <div>
                <label class="text-xs font-medium text-gray-700">Salutation</label>
                <FormControl type="autocomplete" :options="salutationOptions" size="sm" variant="outline"
                  placeholder="Select Customer" v-model="newLead.salutation"
                  :input-class="'bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600'" />
              </div>
              <div class="">
                <label class="text-xs font-medium text-gray-700 mt-4">Name</label>
                <FormControl type="text" size="sm" variant="stable" placeholder="Enter Name"
                  v-model="newLead.first_name"
                  :input-class="'bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600'" />

              </div>
              <div class="">
                <label class="text-xs font-medium text-gray-700 mt-4">Mobile Number</label>
                <FormControl type="text" size="sm" variant="outline" placeholder="Enter Mobile Number"
                  v-model="newLead.mobile_no"
                  :input-class="'bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600'" />

              </div>

              <div class="flex justify-end gap-2 mt-5">
                <button class="px-3 py-1 bg-gray-200 rounded" @click="showLeadModal = false">Cancel</button>

                <button class="px-3 py-1 bg-blue-600 text-white rounded" @click="createLead()">Save</button>
              </div>
            </div>
          </div>
          <div v-if="showOpportunityModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
            <div class="bg-white p-5 rounded-lg w-80 shadow-lg">
              <h3 class="text-lg font-semibold mb-3">Create Opportunity</h3>
              <div class="grid grid-cols-1 md:grid-cols-1 gap-2">

                <div>
                  <label class="text-xs font-medium text-gray-700">Lead (Party Name)</label>

                  <FormControl type="autocomplete" :options="leadOptions" size="sm" variant="outline"
                    placeholder="Select Customer" v-model="newOpportunity.party_name"
                    :input-class="'bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600'" />

                </div>
                <div>
                  <label class="text-xs font-medium text-gray-700">Expected Closing</label>

                  <FormControl type="date" size="sm" variant="outline" placeholder="Enter Expected Closing"
                    v-model="newOpportunity.expected_closing"
                    :input-class="'bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600'" />

                </div>

                <div>
                  <label class="text-xs font-medium text-gray-700">Probability (%)</label>
                  <FormControl type="text" size="sm" variant="outline" placeholder="Enter Probability (%)"
                    v-model="newOpportunity.probability"
                    :input-class="'bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600'" />

                </div>

                <div>
                  <label class="text-xs font-medium text-gray-700">Opportunity Amount</label>
                  <FormControl type="text" size="sm" variant="outline" placeholder="Enter Opportunity Amount"
                    v-model="newOpportunity.opportunity_amount"
                    :input-class="'bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600'" />

                </div>

              </div>

              <div class="flex justify-end gap-2 mt-5">
                <button class="px-3 py-1 bg-gray-200 rounded" @click="showOpportunityModal = false">Cancel</button>

                <button class="px-3 py-1 bg-blue-600 text-white rounded" @click="createOpportunity()">Save</button>
              </div>
            </div>
          </div>
          <!-- ------------------------------------------------------------------------------------ -->
          <Button v-if="field_employee === 'Yes' && faceMatched && action != 'OUT'" :loading="checkins.insert.loading"
            class="w-full py-5 text-sm" @click="submitLog(action)">
            {{ __("Confirm {0}", [actionLabel]) }}
          </Button>

          <Button v-if="field_employee === 'Yes' && faceMatched && forgetCheckOut" :loading="checkins.insert.loading"
            class="w-full py-5 text-sm" @click="submitLog('IN')">
            {{ "Confirm Check-In" }}
          </Button>

        </div>
      </template>
    </BaseLayout>
  </ion-page>
</template>

<script setup>
import {
  IonPage,
  useIonRouter,
  onIonViewWillEnter,
  onIonViewWillLeave
} from "@ionic/vue"
import { useRoute } from "vue-router"
import { createListResource, createResource, toast, Checkbox } from "frappe-ui"
import { inject, ref, watch, computed, reactive } from "vue"
import BaseLayout from "@/components/BaseLayout.vue"
import BackButton from "@/components/icons/backButton.svg"
import locationIcon from "@/components/icons/location.svg"
import { getRuntimeConfig } from "@/utils/runtimeConfig";
import { getRuntimeURLConfig } from "../utils/runtimeURLConfig"
import * as faceapi from "face-api.js"
import FingerprintJS from "@fingerprintjs/fingerprintjs";

let azure_key = ref("")
const DOCTYPE = "Employee Checkin"

const ionRouter = useIonRouter()
const route = useRoute()

const employee = inject("$employee")
const user = inject("$user")
const dayjs = inject("$dayjs")
const __ = inject("$translate")
const wfh = inject("$wfh")
const geofence = inject("$geofence")


const action = route.query.action || "IN"
const actionLabel = action === "IN" ? __("Check In") : __("Check Out")

const checkinTimestamp = ref(null)
const latitude = ref(0)
const longitude = ref(0)
const locationStatus = ref("")
const videoRef = ref(null)

const referenceDescriptor = ref(null)
const capture_img = ref(null)

const faceMatched = ref(false)
const statusMsg = ref("Initilizing...")

let stream = null
let comparisonInterval = null

let field_employee = ref("")
let forgetCheckOut = ref(false)
let locationDescription = ref("")
let isValidLocation = true
let isCheckOut = false

const loginlocation = ref("")

// let typeofCheckIn=ref("")
let typeofCheckIn = ref(null)
let leadValue = ref(null)
let opportunityValue = ref(null)
let hospitalValue = ref(null)
let carValue = ref(null)

let leadOptions = ref([])
let OpportunityOptions = ref([])
let CarOptions = ref([])
let HospitalOptions = ref([])

let lastLogRefDoctype = ref(null)
let lastLogRefName = ref(null)
let lastLogRefTime = ref(null)

let currentLogRefDoctype = ref(null)
let currentLogRefName = ref(null)
let currentCheckINID = ref(null)
let lastCheckOutID = ref(null)
let lastLogLat = ref(null)
let lastLogLan = ref(null)
let logType = action

let location_url = ""
let location_response = ""
let distance_url = ""
let distance_response = ""
let locations = ref([])
let device_id = ref("")
let showLeadModal = ref(false)
const showOpportunityModal = ref(false);

let newLead = reactive([
  {
    salutation: "",
    first_name: "",
    mobile_no: "",
  }
])
let newCustomer = reactive([
  {
    salutation: "",
    first_name: "",
    mobile_no: "",
  }
])
const newOpportunity = reactive({
  party_name: "",
  opportunity_from: "Lead",
  opportunity_type: "",
  opportunity_owner: "",
  expected_closing: "",
  probability: "",
  opportunity_amount: "",
});
let salutationOptions = ref([
  { label: 'Mr.', value: 'Mr' },
  { label: 'Ms.', value: 'Ms' },
  { label: 'Mrs.', value: 'Mrs' },
  { label: 'M/s.', value: 'M/s' }
])


/* ---------------- CHECKINS ---------------- */

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


/* ---------------- SETTINGS ---------------- */

const settings = createResource({
  url: "hrms.api.get_hr_settings",
  auto: true,
})




/* ---------------- PAGE ENTER ---------------- */

onIonViewWillEnter(async () => {
  checkins.reload()
  checkinTimestamp.value = dayjs().format("YYYY-MM-DD HH:mm:ss")
  field_employee.value = employee.data.field_employee;
  const deviceId = await getDeviceId();
  device_id.value = deviceId;
  // console.log("EMP",field_employee.value);
  // console.log("GFC",geofence.data);
  // console.log("WFH",wfh.data);

  await loadModels()

  await loadAllOptions();
  await loadUserImage()

  await startCamera()
  startComparison()
})

onIonViewWillLeave(() => {
  stopCamera()
  if (comparisonInterval) clearInterval(comparisonInterval)
})

/* ---------------- LOAD MODELS ---------------- */

async function loadModels() {
  const MODEL_URL = "/assets/hrms/models"

  await Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
    faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
    faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
  ])


}

/* ---------------- LOAD REFERENCE IMAGE ---------------- */

async function loadUserImage() {
  if (!user?.data?.user_image) {
    statusMsg.value = "Photo is Missing, Contact HR"
    return
  }

  const img = await faceapi.fetchImage(user.data.user_image)

  const detection = await faceapi
    .detectSingleFace(img, new faceapi.TinyFaceDetectorOptions())
    .withFaceLandmarks()
    .withFaceDescriptor()

  if (!detection) {
    statusMsg.value = "No face detected in profile image"
    return
  }

  referenceDescriptor.value = detection.descriptor


}

/* ---------------- CAMERA ---------------- */

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "user",
        width: { ideal: 640 },
        height: { ideal: 480 }
      },
      audio: false,
    })

    if (videoRef.value) {
      videoRef.value.srcObject = stream
      videoRef.value.style.transform = "scaleX(-1)"
    }
  } catch (err) {
    toast({
      title: __("Camera Error"),
      text: __("Unable to access camera"),
      position: "bottom-center",
    })
  }
}

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
}

/* ---------------- FACE COMPARISON ---------------- */

function captureImage() {
  if (!videoRef.value) return null

  const video = videoRef.value

  const canvas = document.createElement("canvas")
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  const ctx = canvas.getContext("2d")

  // Mirror the image (because video is mirrored)
  ctx.translate(canvas.width, 0)
  ctx.scale(-1, 1)

  ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

  return canvas.toDataURL("image/jpeg", 0.9)
}

function startComparison() {
  if (!referenceDescriptor.value) return

  comparisonInterval = setInterval(async () => {
    const detection = await faceapi
      .detectSingleFace(
        videoRef.value,
        new faceapi.TinyFaceDetectorOptions(
          {
          inputSize: 160,   //critical
          scoreThreshold: 0.5
        }
        )
      )
      .withFaceLandmarks()
      .withFaceDescriptor()

    if (!detection) {
      statusMsg.value = "No face detected"
      faceMatched.value = false
      return
    }

    const distance = faceapi.euclideanDistance(
      referenceDescriptor.value,
      detection.descriptor
    )

    if (distance < 0.45) {
      faceMatched.value = true
      statusMsg.value = "Face Matched"
      clearInterval(comparisonInterval)
      // Capture image
      capture_img.value = captureImage()
      if (capture_img.value) {
        validateLocation();
      }
      // submitLog();
      // Stop camera after capture (optional)
      //   stopCamera()
    } else {
      faceMatched.value = false
      statusMsg.value = "Face Not Matched"
    }
  }, 1500)
}
function validateLocation() {
  const today = new Date().toISOString().split("T")[0];

  //Find WFH record for the logged-in employee that includes today in choose_date
  const wfhRecordForToday = wfh.data.find(item => {
    // Check if this record belongs to the same employee
    const sameEmployee = item.employee_wfh_details?.some(
      detail => detail.employee === employee.data.name
    );

    // Check if today's date is one of the chosen WFH dates
    const hasTodayDate = item.choose_date?.some(
      dateItem => dateItem.date === today
    );

    return sameEmployee && hasTodayDate;
  });

  // ------------------ WFH CASE ------------------
  if (wfhRecordForToday && field_employee.value !== "Yes") {
    faceMatched.value = true;
    statusMsg.value = "Face Matched (WFH)";
    statusMsg.value = "Face Matched (WFH)";



    //  If IN - directly submit
    if (action === "IN") {
      //   submitLog(nextAction.value.action);
    } else {
      //  OUT → verify boundary using last check-in coordinates
      const lastLat = parseFloat(lastLog.value.latitude);
      const lastLon = parseFloat(lastLog.value.longitude);
      const defaultRadius = 200;

      const dist = getDistanceFromLatLonInMeters(
        latitude.value,
        longitude.value,
        lastLat,
        lastLon
      );

      if (dist <= defaultRadius) {
        // submitLog(nextAction.value.action);
      } else {
        statusMsg.value = "You Are Outside The Work-From-Home Allowed Boundary";

        isValidLocation = false;
      }
    }
    return; //Stop here (no geofence check needed)
  }
  if (field_employee.value !== 'Yes') {
    // ------------------ OFFICE GEOFENCE CASE ------------------
    const allowedFences = geofence.data[0]?.fence || [];
    let insideAnyFence = false;

    for (const loc of allowedFences) {
      const distanceToCenter = getDistanceFromLatLonInMeters(
        latitude.value,
        longitude.value,
        parseFloat(loc.latitude),
        parseFloat(loc.longitude)
      );

      if (distanceToCenter <= loc.radius) {
        insideAnyFence = true;
        loginlocation.value = loc.location; // store current matched location name
        break;
      }
    }

    if (insideAnyFence) {
      faceMatched.value = true;
      statusMsg.value = "Face Matched & Inside Allowed Location";

      if (action === "IN") {
        locationDescription.value = '';
        submitLog(action);
        console.log("Geofence Check In");

      } else {
        locationDescription.value = '';

        //Check again using geofence (same as IN)
        let insideFenceForOut = false;

        for (const loc of allowedFences) {
          const distanceToCenter = getDistanceFromLatLonInMeters(
            latitude.value,
            longitude.value,
            parseFloat(loc.latitude),
            parseFloat(loc.longitude)
          );

          if (distanceToCenter <= loc.radius) {
            insideFenceForOut = true;
            loginlocation.value = loc.location; // optional: update location
            break;
          }
        }

        if (insideFenceForOut) {
          submitLog(action);
          console.log("Geofence Check Out");
        } else {
          statusMsg.value = "You Are Outside the Allowed Office Boundary";
          isValidLocation = false;
        }
      }

    } else {
      faceMatched.value = false;
      if (geofence.data.length === 0) {
        statusMsg.value = "Geofence is Missing, Contact ur HR" //Camera ready. Upload reference image.
        return
      }
      statusMsg.value = "Matched but Outside Allowed Office Boundary";
      isValidLocation = false;
    }
  }
  // Sales Employee
  else {
    if (action === "IN") {
      // submitLog(nextAction.value.action);
      statusMsg.value = "Face Matched"
      isCheckOut = true;
      faceMatched.value = true;
      if (lastLog.value) {
        lastLogRefDoctype.value = lastLog.value.reference_dt
        lastLogRefName.value = lastLog.value.reference_dn
        lastCheckOutID.value = lastLog.value.name;
        lastLogLat.value = lastLog.value.latitude;
        lastLogLan.value = lastLog.value.longitude;
        lastLogRefTime.value = lastLog.value?.time?.slice(0, 10) || "";
      }
      // console.log("last --",lastLogRefDoctype.value)
    } else {
      isCheckOut = false;
      statusMsg.value = "Face Matched"
      lastLogRefDoctype.value = lastLog.value.reference_dt
      lastLogRefName.value = lastLog.value.reference_dn
      lastCheckOutID.value = lastLog.value.name;
      lastLogLat.value = lastLog.value.latitude;
      lastLogLan.value = lastLog.value.longitude;
      // console.log("last --",lastLogRefDoctype.value)

      const lastLat = parseFloat(lastLog.value.latitude);
      const lastLon = parseFloat(lastLog.value.longitude);
      const defaultRadius = 200;

      const dist = getDistanceFromLatLonInMeters(
        latitude.value,
        longitude.value,
        lastLat,
        lastLon
      );

      if (dist <= defaultRadius) {
        submitLog(action);

      } else {
        statusMsg.value = "You Are Outside The  Allowed Boundary";
        isValidLocation = false;
        isCheckOut = true;

      }
    }
  }
}
function getDistanceFromLatLonInMeters(lat1, lon1, lat2, lon2) {
  const R = 6371e3; // meters
  const φ1 = lat1 * Math.PI / 180;
  const φ2 = lat2 * Math.PI / 180;
  const Δφ = (lat2 - lat1) * Math.PI / 180;
  const Δλ = (lon2 - lon1) * Math.PI / 180;

  const a = Math.sin(Δφ / 2) ** 2 +
    Math.cos(φ1) * Math.cos(φ2) *
    Math.sin(Δλ / 2) ** 2;

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c; // in meters
}


/* ---------------- GEOLOCATION ---------------- */

watch(
  () => settings.data,
  (value) => {
    if (value?.allow_geolocation_tracking == 1) {
      fetchLocation()
    }
  },
  { immediate: true }
)

async function fetchLocation() {
  if (!navigator.geolocation) {
    locationStatus.value = __("Geolocation not supported")
    return
  }

  locationStatus.value = __("Locating...")

  navigator.geolocation.getCurrentPosition(
    (position) => {
      latitude.value = position.coords.latitude
      longitude.value = position.coords.longitude
      locationStatus.value =
        `Lat: ${latitude.value.toFixed(5)}, Long: ${longitude.value.toFixed(5)}`
    },
    (error) => {
      locationStatus.value = error.message
    }
  )
  await loadUrls();
  await getLocationAPI(latitude.value, longitude.value)
}


/* ---------------- SUBMIT ---------------- */

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(";").shift()
}

async function getDeviceId() {
  let deviceId = localStorage.getItem("hrms_device_id");

  if (deviceId) return deviceId;

  const fp = await FingerprintJS.load();
  const result = await fp.get();
  deviceId = result.visitorId;

  localStorage.setItem("hrms_device_id", deviceId);
  return deviceId;
}
watch(
  () => typeofCheckIn.value?.value,
  (newVal, oldVal) => {
    if (newVal !== oldVal) {
      hospitalValue.value = null
      carValue.value = null
      leadValue.value = null
      opportunityValue.value = null
    }
  }
)
function submitLog(logType) {
  const actionLabel = logType === "IN" ? __("Check-in") : __("Check-out")
  if (!faceMatched.value) {
    toast({
      title: "Face Verification",
      text: "Face not matched",
      position: "bottom-center",
    })
    return
  }
  const refDocDT = typeofCheckIn.value?.value || lastLogRefDoctype.value || "";
  const refDocDN =
    hospitalValue.value?.value ||
    carValue.value?.value ||
    leadValue.value?.value ||
    opportunityValue.value?.value ||
    lastLogRefName.value || "";


  currentLogRefDoctype.value = refDocDT
  currentLogRefName.value = refDocDN

  checkins.insert.submit(
    {
      employee: employee.data.name,
      log_type: logType,
      time: checkinTimestamp.value,
      latitude: latitude.value,
      longitude: longitude.value,
      location: loginlocation.value,
      device_id: device_id.value,
      reference_dt: refDocDT,   // ← fixed
      reference_dn: refDocDN,   // ← fixed
      description: locationDescription.value
    },
    {
      onSuccess(doc) {
        currentCheckINID.value = doc.name;
        if (field_employee.value === 'Yes' && actionLabel === 'Check-in' && !forgetCheckOut.value) {

          const now = new Date();

          const formattedDateTime =
            now.getFullYear() + '-' +
            (now.getMonth() + 1).toString().padStart(2, '0') + '-' +
            now.getDate().toString().padStart(2, '0');
          const lastDate = lastLogRefTime.value;

          if (lastDate && lastDate === formattedDateTime) {
            CreateCheckInJoureny();
          }



        }

        forgetCheckOut.value = false;
        isCheckOut = false;
        toast({
          title: __("Success"),
          text: __("{0} successful!", [actionLabel]),
          position: "bottom-center",
        })
        stopCamera()
        ionRouter.back()
      },
    }
  )
}

async function CreateCheckInJoureny() {



  const distance = await getDistanceInMeters(
    latitude.value,
    longitude.value,
    lastLogLat.value,
    lastLogLan.value
  );
  let dis_km = 0
  if (distance !== 0) {
    dis_km = Number((distance / 1000).toFixed(2));
  }



  const lastLogID = lastLog.value.name


  const employeeData = employee.data
  const now = new Date();
  const formattedDateTime =
    now.getFullYear() + '-' +
    (now.getMonth() + 1).toString().padStart(2, '0') + '-' +
    now.getDate().toString().padStart(2, '0');

  const csrfToken =
    frappe?.csrf_token || window?.csrf_token || getCookie("csrf_token");

  const payload = {
    employee: employeeData.name,
    user: employeeData.user_id,
    checkout: lastCheckOutID.value,
    checkout_reference: lastLogRefDoctype.value,
    checkout_reference_name: lastLogRefName.value,
    checkin: currentCheckINID.value,
    checkin_reference: currentLogRefDoctype.value,
    checkin_reference_name: currentLogRefName.value,
    // reference_dt:refDocDT,
    // reference_name:refDocDN,
    distance: dis_km,
    date: formattedDateTime,
    // description:locationDescription.value
  };

  const response = await fetch(
    "/api/method/hrms.api.hr_api.create_checkin_journey",
    {
      method: "POST",
      credentials: "include", //  send session cookies
      headers: {
        "Content-Type": "application/json",
        "X-Frappe-CSRF-Token": csrfToken, //  required for POST/PUT/DELETE
      },
      body: JSON.stringify(payload),
    }
  );


  const result = await response.json();

  if (result.message) {
    // console.log("result",result.message.data);


  } else {
    console.error(" Error Creating CheckIn Joureny:", result);
  }


}

function goBack() {
  stopCamera()
  ionRouter.back()
}

// --------------------Sales Employee Helpers-----------------------------
async function loadUrls() {
  const config = await getRuntimeConfig();
  azure_key.value = config.AZURE_KEY;
  //   console.log("azure_key.value",azure_key.value)
  const url_config = await getRuntimeURLConfig();
  distance_url = url_config.distance_url;
  location_url = url_config.location_url;
  distance_response = url_config.distance_response;
  location_response = url_config.location_response;
}

async function createLead() {
  const csrfToken =
    frappe?.csrf_token || window?.csrf_token || getCookie("csrf_token");

  const payload = {
    first_name: newLead.first_name,
    mobile_no: newLead.mobile_no,
    salutation: newLead.salutation.value
  };

  const response = await fetch(
    "/api/method/hrms.api.hr_api.create_lead",
    {
      method: "POST",
      credentials: "include", //  send session cookies
      headers: {
        "Content-Type": "application/json",
        "X-Frappe-CSRF-Token": csrfToken, //  required for POST/PUT/DELETE
      },
      body: JSON.stringify(payload),
    }
  );

  const result = await response.json();

  if (result.message) {
    const createdLead = result.message.data;

    // Optional: Clear form
    newLead.first_name = "";
    newLead.mobile_no = "";
    newLead.salutation = "";
    showLeadModal.value = false;

    // Push new Lead into Autocomplete options
    const newOption = {
      label: `${createdLead.name} (${createdLead.first_name}, ${createdLead.mobile_no})`,
      value: createdLead.name,
    };
    leadOptions.value = [newOption, ...leadOptions.value];

    // Set selected Lead
    leadValue.value = newOption;



  } else {
    console.error(" Error Creating Lead:", result);
  }
}
async function createOpportunity() {
  const csrfToken =
    frappe?.csrf_token || window?.csrf_token || getCookie("csrf_token");

  const payload = {
    party_name: newOpportunity.party_name.value,
    opportunity_from: "Lead",
    opportunity_owner: '',
    expected_closing: newOpportunity.expected_closing,
    opportunity_amount: newOpportunity.opportunity_amount,
    probability: newOpportunity.probability
  };

  const response = await fetch(
    "/api/method/hrms.api.hr_api.create_opportunity",
    {
      method: "POST",
      credentials: "include", //  send session cookies
      headers: {
        "Content-Type": "application/json",
        "X-Frappe-CSRF-Token": csrfToken, //  required for POST/PUT/DELETE
      },
      body: JSON.stringify(payload),
    }
  );

  const result = await response.json();

  if (result.message) {
    const newOpportunityRes = result.message.data;

    // Optional: Clear form


    // Push new Lead into Autocomplete options
    const newOption = {
      label: `${newOpportunityRes.name} (${newOpportunityRes.opportunity_from}, ${newOpportunityRes.party_name})`,
      value: newOpportunityRes.name,
    };
    OpportunityOptions.value = [newOption, ...OpportunityOptions.value];

    // Set selected Lead
    opportunityValue.value = newOption;


    newOpportunity.party_name = "";
    newOpportunity.opportunity_from = "Lead";
    newOpportunity.opportunity_owner = "";
    newOpportunity.expected_closing = "";
    newOpportunity.opportunity_amount = "";
    newOpportunity.probability = "";

    showOpportunityModal.value = false;

  } else {
    console.error(" Error Creating Opportunity:", result);
  }
}
function buildUrl(template, replacements) {
  let url = template;
  for (const key in replacements) {
    url = url.replace(new RegExp(`\\$\\{${key}\\}`, "g"), replacements[key]);
  }
  return url;
}

async function getDistanceInMeters(currentLat, currentLon, expectedLat, expectedLon) {

  // console.log("currentLat",currentLat)
  // console.log("currentLon",currentLon)
  // console.log("expectedLat",expectedLat)

  const key = azure_key.value

  if (!key) {
    console.warn("Azure Key missing");
    alert("Please add the key in the system settings");

  }

  // console.log("Using Azure Key:", key);

  //   expectedLat = 12.8742
  //   expectedLon= 77.5569

  // const url = `https://atlas.microsoft.com/route/directions/json?api-version=1.0&subscription-key=${key}&query=${currentLat},${currentLon}:${expectedLat},${expectedLon}`;
  const url = buildUrl(distance_url, {
    key,
    currentLat,
    currentLon,
    expectedLat,
    expectedLon
  });
  try {
    const response = await fetch(url);
    const data = await response.json();

    const distance = getValueByPath(data, distance_response);
    console.log("Distance ", distance);

    // const distance = data?.distance_response;


    if (!distance && distance !== 0) {
      //   console.error("Invalid Distance Response:", data);
      return 0;
    }

    // console.log(" Distance (meters):", distance);
    return distance;
  } catch (err) {
    console.error("Azure Distance API Error:", err);
    return null;
  }
}

function getValueByPath(obj, path) {
  //  console.log("Resolving path:", path);
  if (!obj || !path || typeof path !== "string") return null;

  const cleanPath = path.replace(/\?\./g, ".");

  return cleanPath
    .replace(/\[(\d+)\]/g, ".$1")
    .split(".")
    .filter(Boolean)
    .reduce((o, k) => (o && k in o ? o[k] : null), obj);
}


async function getLocationAPI(currentLat, currentLon) {
  const csrfToken =
    frappe?.csrf_token ||
    window?.csrf_token ||
    getCookie("csrf_token");

  try {
    /* ------------------------------------------------
       1. Check if location already exists (Frappe)
    ------------------------------------------------ */
    const frappeResp = await fetch(
      `/api/method/hrms.api.hr_api.find_location_by_latlon?lat=${currentLat}&lon=${currentLon}`,
      {
        method: "GET",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-Frappe-CSRF-Token": csrfToken
        }
      }
    );

    const frappeResult = await frappeResp.json();
    //  console.log("Frappe Result:", frappeResult);

    /* ------------------------------------------------
       2. If location NOT found → call external API
    ------------------------------------------------ */
    if (frappeResult?.message?.found === false) {
      console.log("Frappe Result:", frappeResult);


      if (!azure_key.value) {
        console.warn("Azure Key missing");
        stopCamera();
        // alert("Please add the key in the system settings");
        return null;
      }

      const url = buildUrl(location_url, {
        key: azure_key.value,
        currentLat,
        currentLon
      });
      const apiResp = await fetch(url);
      const apiData = await apiResp.json();

      const locationResult = getValueByPath(
        apiData,
        location_response
      );

      //   console.log("Location Result:", locationResult);

      locationDescription.value = locationResult || "";
      // console.log("Des new before save",locationDescription.value);


      const response = await fetch(
        "/api/method/hrms.api.hr_api.save_location",
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
            "X-Frappe-CSRF-Token": csrfToken
          },
          body: JSON.stringify({
            payload: apiData
          })
        }
      );

      const result = await response.json();
      //   console.log("Save Res",result);
      locationDescription.value = result.message.display_name || "";
      // console.log("Des After before save",locationDescription.value);


      if (!response.ok) {
        throw new Error(result?.message || "Failed to save location");
      }

      return locationResult;


    }

    /* ------------------------------------------------
       3. Location already exists
    ------------------------------------------------ */
    locationDescription.value = frappeResult.message.display_name || "";
    // console.log("Des Alerady",locationDescription.value);
    return locationDescription.value;

  } catch (error) {
    console.error("Location API Error:", error);
    return null;
  }
}
async function fetchLocationList() {
  const csrfToken = frappe?.csrf_token || window?.csrf_token || getCookie("csrf_token")

  const response = await fetch(
    "/api/method/hrms.api.location_api.get_all_locations",
    {
      method: "GET",
      credentials: "include", //  needed to send session cookies
      headers: {
        "Content-Type": "application/json",
        "X-Frappe-CSRF-Token": csrfToken, //  required
      },
    }
  )

  const result = await response.json()

  if (result.message.data) {
    locations.value = result.message.data

  } else {
    console.error("Error:", result.message)
    return []
  }
}

async function fetchOptions(docType) {
  const csrfToken = frappe?.csrf_token || window?.csrf_token || getCookie("csrf_token");
  const endpoint = `/api/method/hrms.api.hr_api.get_all_${docType.toLowerCase()}`;

  const response = await fetch(endpoint, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-Frappe-CSRF-Token": csrfToken,
    },
  });

  const result = await response.json();
  return result?.message?.data || result?.data || [];
}
async function loadAllOptions() {
  const leadData = await fetchOptions("lead");
  const leadArray = Array.isArray(leadData) ? leadData : Object.values(leadData);

  leadOptions.value = leadArray.map(i => {
    // Build label parts dynamically
    let extras = [];

    if (i.lead_name) extras.push(i.lead_name);
    if (i.mobile_no) extras.push(i.mobile_no);

    return {
      label: extras.length ? `${i.name} (${extras.join(", ")})` : i.name,
      value: i.name
    };
  });

  leadOptions.value = [
    ...leadOptions.value,
    { label: "+ Create New Lead", value: "create_new_lead" }
  ];

  const oppData = await fetchOptions("opportunity");
  const oppArray = Array.isArray(oppData) ? oppData : Object.values(oppData);

  OpportunityOptions.value = oppArray.map(i => {
    let extras = [];

    if (i.opportunity_from) extras.push(i.opportunity_from);
    //   if (i.party_name) extras.push(i.party_name);
    if (i.title) extras.push(i.title);

    return {
      label: extras.length ? `${i.name} (${extras.join(", ")})` : i.name,
      value: i.name
    };
  });

  OpportunityOptions.value = [
    ...OpportunityOptions.value,
    { label: "+ Create New Opportunity", value: "create_new_opportunity" }
  ];

  const hospitalData = await fetchOptions("hospital");
  const hospitalArray = Array.isArray(hospitalData) ? hospitalData : Object.values(hospitalData);
  HospitalOptions.value = hospitalArray.map(i => {
    let extras = [];
    if (i.title) extras.push(i.title);
    return {
      label: extras.length ? `${i.name} (${extras.join(", ")})` : i.name,
      value: i.name
    };
  });
  const carData = await fetchOptions("car");
  const carArray = Array.isArray(carData) ? carData : Object.values(carData);
  CarOptions.value = carArray.map(i => {
    let extras = [];
    return {
      label: extras.length ? `${i.name} (${extras.join(", ")})` : i.name,
      value: i.name
    };
  });

  await fetchLocationList();

}

watch(leadValue, (val) => {
  if (val && val.value === "create_new_lead") {
    // console.log("Triggered ");
    showLeadModal.value = true;
    leadValue.value = null; // Reset selection
  }
});
watch(opportunityValue, (val) => {
  if (val && val.value === "create_new_opportunity") {
    // console.log("Triggered  Opportunity Modal Open");
    showOpportunityModal.value = true;
    opportunityValue.value = ""; // reset
  }
});
watch(hospitalValue, (val) => {
  if (val) {
    hospitalValue.value = ""; // reset
  }
});
watch(carValue, (val) => {
  if (val) {
    carValue.value = ""; // reset
  }
});

</script>
