<template>
  <BaseLayout>
    <template #body>
      <div class="verify-page">

        <!-- Header -->
        <div class="verify-header">
          <img :src="BackButton" class="back-btn" @click="goBack" />
          <span class="header-title">Verify Attendance</span>
          <div class="header-spacer" />
        </div>

        <!-- Scanner Section -->
        <div class="scanner-section">
          <!-- Instruction text -->
          <p class="scan-instruction">
            {{ faceMatched ? "Face verified successfully" : "Align your face within the frame" }}
          </p>

          <!-- Rectangle Scanner Frame -->
          <div class="scanner-wrapper">
            <video
              ref="videoRef"
              autoplay
              playsinline
              class="scanner-video"
            />

            <!-- Corner brackets -->
            <div class="corner top-left" />
            <div class="corner top-right" />
            <div class="corner bottom-left" />
            <div class="corner bottom-right" />

            <!-- Scanning line animation -->
            <div class="scan-line" :class="{ matched: faceMatched, scanning: !faceMatched }" />

            <!-- Overlay dots (face landmarks effect) -->
            <div v-if="faceMatched" class="match-overlay">
              <div v-for="n in 6" :key="n" class="dot" :style="dotStyle(n)" />
            </div>
          </div>

          <!-- Progress bar -->
          <div class="progress-track">
            <div
              class="progress-bar"
              :class="{ full: faceMatched }"
              :style="{ width: faceMatched ? '100%' : progressWidth }"
            />
          </div>
          <p class="progress-label">
             {{ faceMatched ? "" : progressPct }}
          </p>
        </div>

        <!-- Status Pills -->
        <div class="status-section">
          <!-- Face status -->
          <div class="status-pill" :class="facePillClass">
          <div class="row">
              <span class="status-icon">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
              </svg>
            </span>
            <span class="status-label">Face:</span>
            <span class="status-value">{{ faceStatusText }}</span>
            <span class="status-dot" :class="faceDotClass" />
          </div>
            <div class="row">
                          <span class="status-icon">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
                <circle cx="12" cy="9" r="2.5"/>
              </svg>
            </span>
            <span class="status-label">Location:</span>
            <span class="status-value">{{ locationStatusText }}</span>
            <span class="status-dot" :class="locationDotClass" />
            </div>
          </div>
          <!-- Geolocation coords pill (when enabled) -->
          <template v-if="settings.data?.allow_geolocation_tracking && locationStatus">
<div class="coords-pill">
  <!-- Current -->
  <div class="row">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
      <circle cx="12" cy="9" r="2.5"/>
    </svg>
    <span class="coords-text">Current: {{ locationStatus }}</span>
  </div>

  <!-- Expected -->
  <div class="row" v-if="exptlocationStatus">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
      <circle cx="12" cy="9" r="2.5"/>
    </svg>
    <span class="coords-text">Expected: {{ exptlocationStatus }}</span>
  </div>
</div>
          </template>
        </div>

        <!-- Forget-checkout checkbox -->
        <div class="checkbox-row" v-if="action === 'OUT' && faceMatched && isCheckOut">
          <Checkbox
            :value="true"
            v-model="forgetCheckOut"
            label="Forget to CheckOut"
          />
        </div>

        <!-- Field-employee dropdowns -->
        <div class="dropdowns-section" v-if="action === 'IN' || forgetCheckOut">
          <div v-if="field_employee === 'Yes' && isCheckOut">
            <label class="form-label text-xs text-black">Type</label>
            <FormControl
              type="autocomplete"
              :options="[
                { label: 'Lead',        value: 'Lead'        },
                { label: 'Opportunity', value: 'Opportunity' },
                { label: 'Hospital',    value: 'Hospital'    },
                { label: 'CAR',         value: 'CAR'         },
              ]"
              size="sm"
              variant="outline"
              placeholder="Select Type"
              v-model="typeofCheckIn"
              :input-class="inputCls"
              required
            />
          </div>

          <div v-if="typeofCheckIn?.value === 'Lead'">
            <label class="form-label text-xs text-black">Lead</label>
            <FormControl type="autocomplete" :options="leadOptions" size="sm" variant="outline" placeholder="Select Lead" v-model="leadValue" :input-class="inputCls" required />
          </div>
          <div v-if="typeofCheckIn?.value === 'Opportunity'">
            <label class="form-label text-xs text-black">Opportunity</label>
            <FormControl type="autocomplete" :options="OpportunityOptions" size="sm" variant="outline" placeholder="Select Opportunity" v-model="opportunityValue" :input-class="inputCls" />
          </div>
          <div v-if="typeofCheckIn?.value === 'Hospital'">
            <label class="form-label text-xs text-black">Hospital</label>
            <FormControl type="autocomplete" :options="HospitalOptions" size="sm" variant="outline" placeholder="Select Hospital" v-model="hospitalValue" :input-class="inputCls" />
          </div>
          <div v-if="typeofCheckIn?.value === 'CAR'">
            <label class="form-label text-xs text-black">CAR</label>
            <FormControl type="autocomplete" :options="CarOptions" size="sm" variant="outline" placeholder="Select CAR" v-model="carValue" :input-class="inputCls" />
          </div>
        </div>

        <!-- Create Lead Modal -->
        <div v-if="showLeadModal" class="modal-overlay">
          <div class="modal-card">
            <h3 class="modal-title">Create Lead</h3>
            <div class="modal-body">
              <label class="text-xs font-medium text-gray-700">Salutation</label>
              <FormControl type="autocomplete" :options="salutationOptions" size="sm" variant="outline" placeholder="Select Salutation" v-model="newLead.salutation" :input-class="inputCls" />
              <label class="text-xs font-medium text-gray-700 mt-4">Name</label>
              <FormControl type="text" size="sm" variant="stable" placeholder="Enter Name" v-model="newLead.first_name" :input-class="inputCls" />
              <label class="text-xs font-medium text-gray-700 mt-4">Mobile Number</label>
              <FormControl type="text" size="sm" variant="outline" placeholder="Enter Mobile Number" v-model="newLead.mobile_no" :input-class="inputCls" />
            </div>
            <div class="modal-footer">
              <button class="modal-btn cancel" @click="showLeadModal = false">Cancel</button>
              <button class="modal-btn save" @click="createLead">Save</button>
            </div>
          </div>
        </div>

        <!-- Create Opportunity Modal -->
        <div v-if="showOpportunityModal" class="modal-overlay">
          <div class="modal-card">
            <h3 class="modal-title">Create Opportunity</h3>
            <div class="modal-body grid grid-cols-1 gap-2">
              <div>
                <label class="text-xs font-medium text-gray-700">Lead (Party Name)</label>
                <FormControl type="autocomplete" :options="leadOptions" size="sm" variant="outline" placeholder="Select Customer" v-model="newOpportunity.party_name" :input-class="inputCls" />
              </div>
              <div>
                <label class="text-xs font-medium text-gray-700">Expected Closing</label>
                <FormControl type="date" size="sm" variant="outline" v-model="newOpportunity.expected_closing" :input-class="inputCls" />
              </div>
              <div>
                <label class="text-xs font-medium text-gray-700">Probability (%)</label>
                <FormControl type="text" size="sm" variant="outline" placeholder="Enter Probability (%)" v-model="newOpportunity.probability" :input-class="inputCls" />
              </div>
              <div>
                <label class="text-xs font-medium text-gray-700">Opportunity Amount</label>
                <FormControl type="text" size="sm" variant="outline" placeholder="Enter Opportunity Amount" v-model="newOpportunity.opportunity_amount" :input-class="inputCls" />
              </div>
            </div>
            <div class="modal-footer">
              <button class="modal-btn cancel" @click="showOpportunityModal = false">Cancel</button>
              <button class="modal-btn save" @click="createOpportunity">Save</button>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="action-section">
          <Button
            v-if="faceMatched && isValidLocation"
            :loading="checkins.insert.loading"
         variant="solid"   
            @click="submitLog(action)"
          >
            {{ __("Confirm {0}", [actionLabel]) }}
          </Button>

          <Button
            v-if="field_employee === 'Yes' && faceMatched && forgetCheckOut"
            :loading="checkins.insert.loading"
            variant="solid"  
            @click="submitLog('IN')"
          >
            Confirm Check-In
          </Button>
        </div>

      </div>
    </template>
  </BaseLayout>
</template>

<script setup>
import { useRoute, useRouter }          from "vue-router"
import { createListResource, createResource, toast, Checkbox, Button } from "frappe-ui"
import { inject, ref, watch, computed, reactive, onMounted, onUnmounted } from "vue"

import BaseLayout   from "@/components/BaseLayout.vue"
import BackButton   from "@/components/icons/backButton.svg"
import locationIcon from "@/components/icons/location.svg"
import { getRuntimeConfig }    from "@/utils/runtimeConfig"
import { getRuntimeURLConfig } from "@/utils/runtimeURLConfig"
import * as faceapi            from "face-api.js"
import FingerprintJS           from "@fingerprintjs/fingerprintjs"

import { useCheckinCache } from "@/composables/useCheckinCache"

const {
  modelsReady,
  descriptorReady,
  referenceDescriptor,
  leadOptions,
  OpportunityOptions,
  HospitalOptions,
  CarOptions,
  loadModels,
  loadDescriptor,
  loadAllOptions,
  addLead,
  addOpportunity,
} = useCheckinCache()

const DOCTYPE = "Employee Checkin"
const inputCls =
  "bg-gray-100 border border-blue-500 text-gray-800 focus:ring-blue-500 focus:border-blue-600"

const router   = useRouter()
const route    = useRoute()
const employee = inject("$employee")
const user     = inject("$user")
const dayjs    = inject("$dayjs")
const __       = inject("$translate")
const wfh      = inject("$wfh")
const geofence = inject("$geofence")

const action      = route.query.action || "IN"
const actionLabel = action === "IN" ? __("Check In") : __("Check Out")

let azure_key = ref("")

const checkinTimestamp   = ref(null)
const latitude           = ref(0)
const longitude          = ref(0)
const locationStatus     = ref("")
const exptlocationStatus = ref("")
const videoRef           = ref(null)

const capture_img    = ref(null)
const faceMatched    = ref(false)
const statusMsg      = ref("Initializing…")

// UI scan progress
const progressPct   = ref("")
const progressWidth = ref("15%")

let stream             = null
let comparisonInterval = null
let progressInterval   = null

let field_employee      = ref("")
let forgetCheckOut      = ref(false)
let locationDescription = ref("")
let isValidLocation     = true
let isCheckOut          = false
const loginlocation     = ref("")

let typeofCheckIn    = ref(null)
let leadValue        = ref(null)
let opportunityValue = ref(null)
let hospitalValue    = ref(null)
let carValue         = ref(null)

let lastLogRefDoctype = ref(null)
let lastLogRefName    = ref(null)
let lastLogRefTime    = ref(null)

let currentLogRefDoctype = ref(null)
let currentLogRefName    = ref(null)
let currentCheckINID     = ref(null)
let lastCheckOutID       = ref(null)
let lastLogLat           = ref(null)
let lastLogLan           = ref(null)

let location_url      = ""
let location_response = ""
let distance_url      = ""
let distance_response = ""

let device_id = ref("")

const showLeadModal        = ref(false)
const showOpportunityModal = ref(false)

const newLead = reactive({ salutation: "", first_name: "", mobile_no: "" })
const newOpportunity = reactive({
  party_name: "",
  opportunity_from: "Lead",
  opportunity_type: "",
  opportunity_owner: "",
  expected_closing: "",
  probability: "",
  opportunity_amount: "",
})

const salutationOptions = [
  { label: "Mr.",  value: "Mr"  },
  { label: "Ms.",  value: "Ms"  },
  { label: "Mrs.", value: "Mrs" },
  { label: "M/s.", value: "M/s" },
]

// ── computed UI states ────────────────────────────────────────────────────────
const faceStatusText = computed(() => {
  if (faceMatched.value) return "Matched"
  if (statusMsg.value === "Initializing…" || statusMsg.value === "Loading face models…") return "Initializing"
  if (statusMsg.value === "Looking for face…" || statusMsg.value === "Starting camera…") return "Scanning…"
  if (statusMsg.value === "Face Not Matched") return "Not Matched"
  if (statusMsg.value === "No face detected") return "No Face"
  return statusMsg.value
})

const locationStatusText = computed(() => {
  if (!settings.data?.allow_geolocation_tracking) return "Not Required"
  if (!locationStatus.value || locationStatus.value === "Locating…") return "Locating…"
  if (!isValidLocation) return "Outside Boundary"
  if (faceMatched.value) return "Verified"
  return "Acquired"
})

const facePillClass = computed(() => ({
  'pill-success': faceMatched.value,
  'pill-error': statusMsg.value === "Face Not Matched",
  'pill-scanning': !faceMatched.value && statusMsg.value !== "Face Not Matched",
}))

const locationPillClass = computed(() => ({
  'pill-success': faceMatched.value && isValidLocation,
  'pill-error': !isValidLocation,
  'pill-scanning': isValidLocation && !faceMatched.value,
}))

const faceDotClass = computed(() => ({
  'dot-green': faceMatched.value,
  'dot-red': statusMsg.value === "Face Not Matched",
  'dot-pulse': !faceMatched.value && statusMsg.value !== "Face Not Matched",
}))

const locationDotClass = computed(() => ({
  'dot-green': faceMatched.value && isValidLocation,
  'dot-red': !isValidLocation,
  'dot-pulse': isValidLocation && !faceMatched.value,
}))

// Animated landmark dots for matched state
function dotStyle(n) {
  const positions = [
    { top: '30%', left: '30%' }, { top: '30%', left: '70%' },
    { top: '50%', left: '20%' }, { top: '50%', left: '80%' },
    { top: '65%', left: '40%' }, { top: '65%', left: '60%' },
  ]
  return { ...positions[n - 1], animationDelay: `${n * 0.1}s` }
}

// ── checkins resource ─────────────────────────────────────────────────────────
const checkins = createListResource({
  doctype: DOCTYPE,
  fields: [
    "name", "employee", "employee_name", "log_type", "time",
    "device_id", "location", "latitude", "longitude",
    "reference_dt", "reference_dn",
  ],
  filters: { employee: employee.data.name },
  orderBy: "time desc",
})

const lastLog = computed(() => {
  if (checkins.list.loading || !checkins.data) return null
  return checkins.data[0]
})

const settings = createResource({ url: "hrms.api.get_hr_settings", auto: true })

// ── progress animation ────────────────────────────────────────────────────────
function startProgressAnimation() {
  let pct = 15
  progressInterval = setInterval(() => {
    if (faceMatched.value) {
      clearInterval(progressInterval)
      progressWidth.value = "100%"
      progressPct.value   = ""
      return
    }
    pct = pct < 85 ? pct + Math.random() * 3 : 85
    progressWidth.value = `${pct.toFixed(0)}%`
    progressPct.value   = `${pct.toFixed(0)}%`
  }, 600)
}

// ─────────────────────────────────────────────────────────────────────────────
// EXPECTED LOCATION — set before face match
// ─────────────────────────────────────────────────────────────────────────────

function setExpectedLocation() {
  if (action === "OUT") {
    // All OUT cases: expected = last check-in coords (shown immediately)
    if (lastLog.value?.latitude && lastLog.value?.longitude) {
      exptlocationStatus.value = `Lat: ${parseFloat(lastLog.value.latitude).toFixed(5)}, Long: ${parseFloat(lastLog.value.longitude).toFixed(5)}`
    }
    return
  }

  // IN action — field employees don't need expected shown upfront
  if (field_employee.value === "Yes") return

  // IN action — office geofence: show nearest office coords immediately
  const allFences = (geofence.data || []).flatMap(g => g.fence || [])
  if (!allFences.length) return

  let nearestFence = null
  let nearestDist  = Infinity

  for (const loc of allFences) {
    const dist = getDistanceFromLatLonInMeters(
      latitude.value, longitude.value,
      parseFloat(loc.latitude), parseFloat(loc.longitude)
    )
    if (dist < nearestDist) {
      nearestDist  = dist
      nearestFence = loc
    }
  }

  if (nearestFence) {
    exptlocationStatus.value = `Lat: ${parseFloat(nearestFence.latitude).toFixed(5)}, Long: ${parseFloat(nearestFence.longitude).toFixed(5)}`
  }
}

// Watch lastLog — for OUT, set expected as soon as last check-in data arrives
watch(
  lastLog,
  (val) => {
    if (val && latitude.value !== 0) {
      setExpectedLocation()
    }
  },
  { immediate: true }
)

// ─────────────────────────────────────────────────────────────────────────────
// LIFECYCLE
// ─────────────────────────────────────────────────────────────────────────────

onMounted(async () => {
  checkins.reload()
  checkinTimestamp.value = dayjs().format("YYYY-MM-DD HH:mm:ss")
  field_employee.value   = employee.data.field_employee
  device_id.value        = await getDeviceId()

  statusMsg.value = "Loading face models…"
  await loadModels()

  if (!referenceDescriptor.value) {
    if (!user?.data?.user_image) {
      statusMsg.value = "Photo is missing, contact HR"
      return
    }
    statusMsg.value = "Preparing face data…"
    await loadDescriptor(user.data.user_image)

    if (!referenceDescriptor.value) {
      statusMsg.value = "No face detected in profile image"
      return
    }
  }

  loadAllOptions().catch(console.error)

  statusMsg.value = "Starting camera…"
  await startCamera()
  startProgressAnimation()
  startComparison()
})

onUnmounted(() => {
  stopCamera()
  if (comparisonInterval) clearInterval(comparisonInterval)
  if (progressInterval)   clearInterval(progressInterval)
})

// ─────────────────────────────────────────────────────────────────────────────
// CAMERA
// ─────────────────────────────────────────────────────────────────────────────

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 } },
      audio: false,
    })
    if (videoRef.value) {
      videoRef.value.srcObject      = stream
      videoRef.value.style.transform = "scaleX(-1)"
    }
  } catch {
    toast({ title: __("Camera Error"), text: __("Unable to access camera"), position: "bottom-center" })
  }
}

function stopCamera() {
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null }
}

// ─────────────────────────────────────────────────────────────────────────────
// FACE COMPARISON
// ─────────────────────────────────────────────────────────────────────────────

function captureImage() {
  if (!videoRef.value) return null
  const video  = videoRef.value
  const canvas = document.createElement("canvas")
  canvas.width  = video.videoWidth
  canvas.height = video.videoHeight
  const ctx = canvas.getContext("2d")
  ctx.translate(canvas.width, 0)
  ctx.scale(-1, 1)
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
  return canvas.toDataURL("image/jpeg", 0.9)
}

function startComparison() {
  if (!referenceDescriptor.value) {
    statusMsg.value = "Face reference not ready"
    return
  }
  statusMsg.value = "Looking for face…"

  comparisonInterval = setInterval(async () => {
    if (!videoRef.value) return

    const detection = await faceapi
      .detectSingleFace(
        videoRef.value,
        new faceapi.TinyFaceDetectorOptions({ inputSize: 160, scoreThreshold: 0.5 })
      )
      .withFaceLandmarks()
      .withFaceDescriptor()

    if (!detection) {
      statusMsg.value   = "No face detected"
      faceMatched.value = false
      return
    }

    const distance = faceapi.euclideanDistance(
      referenceDescriptor.value,
      detection.descriptor
    )

    if (distance < 0.45) {
      faceMatched.value = true
      statusMsg.value   = "Face Matched"
      clearInterval(comparisonInterval)
      capture_img.value = captureImage()
      if (capture_img.value) validateLocation()
    } else {
      faceMatched.value = false
      statusMsg.value   = "Face Not Matched"
    }
  }, 1500)
}

// ─────────────────────────────────────────────────────────────────────────────
// LOCATION VALIDATION
// ─────────────────────────────────────────────────────────────────────────────

function validateLocation() {
  const today = new Date().toISOString().split("T")[0]

  const wfhRecordForToday = wfh.data.find((item) => {
    const sameEmployee = item.employee_wfh_details?.some(
      (d) => d.employee === employee.data.name
    )
    const hasTodayDate = item.choose_date?.some((d) => d.date === today)
    return sameEmployee && hasTodayDate
  })

  // ── WFH block ──────────────────────────────────────────────────────────────
  if (wfhRecordForToday && field_employee.value !== "Yes") {
    faceMatched.value = true
    statusMsg.value   = "Face Matched (WFH)"

    if (action === "IN") {
      // WFH + IN: exptlocationStatus not required
    } else {
      // WFH + OUT: already set by setExpectedLocation(), just validate distance
      const dist = getDistanceFromLatLonInMeters(
        latitude.value, longitude.value,
        parseFloat(lastLog.value.latitude),
        parseFloat(lastLog.value.longitude)
      )
      if (dist > 200) {
        statusMsg.value = "You Are Outside The Work-From-Home Allowed Boundary"
        isValidLocation = false
      }
    }
    return
  }

  // ── Field Employee block ──────────────────────────────────────────────────
   if (field_employee.value === "Yes") {
    if (action === "IN") {
      // Field employee IN: exptlocationStatus not required
      statusMsg.value   = "Face Matched"
      isCheckOut        = true
      faceMatched.value = true
      if (lastLog.value) {
        lastLogRefDoctype.value = lastLog.value.reference_dt
        lastLogRefName.value    = lastLog.value.reference_dn
        lastCheckOutID.value    = lastLog.value.name
        lastLogLat.value        = lastLog.value.latitude
        lastLogLan.value        = lastLog.value.longitude
        lastLogRefTime.value    = lastLog.value?.time?.slice(0, 10) || ""
      }
    } else {
      // Field employee OUT: already set by setExpectedLocation(), just validate distance
      isCheckOut              = false
      statusMsg.value         = "Face Matched"
      lastLogRefDoctype.value = lastLog.value.reference_dt
      lastLogRefName.value    = lastLog.value.reference_dn
      lastCheckOutID.value    = lastLog.value.name
      lastLogLat.value        = lastLog.value.latitude
      lastLogLan.value        = lastLog.value.longitude

      const dist = getDistanceFromLatLonInMeters(
        latitude.value, longitude.value,
        parseFloat(lastLog.value.latitude),
        parseFloat(lastLog.value.longitude)
      )
      if (dist > 200) {
        statusMsg.value = "You Are Outside The Allowed Boundary"
        isValidLocation = false
        isCheckOut      = true
      }
    }
  } 
  // ── Office geofence block ──────────────────────────────────────────────────
  else  {
    const allFences    = (geofence.data || []).flatMap(g => g.fence || [])
    let insideAnyFence = false

    for (const loc of allFences) {
      const dist = getDistanceFromLatLonInMeters(
        latitude.value, longitude.value,
        parseFloat(loc.latitude), parseFloat(loc.longitude)
      )
      if (dist <= loc.radius) {
        insideAnyFence           = true
        loginlocation.value      = loc.location
        // Update exptlocationStatus to the actually-matched fence (more precise than nearest)
        exptlocationStatus.value = `Lat: ${parseFloat(loc.latitude).toFixed(5)}, Long: ${parseFloat(loc.longitude).toFixed(5)}`
        break
      }
    }

    if (insideAnyFence) {
      faceMatched.value         = true
      statusMsg.value           = "Face Matched & Inside Allowed Location"
      locationDescription.value = ""

      if (action === "OUT") {
        let insideFenceForOut = false
        for (const loc of allFences) {
          const dist = getDistanceFromLatLonInMeters(
            latitude.value, longitude.value,
            parseFloat(loc.latitude), parseFloat(loc.longitude)
          )
          if (dist <= loc.radius) {
            insideFenceForOut        = true
            loginlocation.value      = loc.location
            exptlocationStatus.value = `Lat: ${parseFloat(loc.latitude).toFixed(5)}, Long: ${parseFloat(loc.longitude).toFixed(5)}`
            break
          }
        }
        if (!insideFenceForOut) {
          statusMsg.value = "You Are Outside the Allowed Office Boundary"
          isValidLocation = false
        }
      }
    } else {
      faceMatched.value = false
      statusMsg.value   = allFences.length === 0
        ? "Geofence is Missing, Contact your HR"
        : "Matched"
      isValidLocation   = false
    }

  // ── Field employee block ───────────────────────────────────────────────────
  }
}

function getDistanceFromLatLonInMeters(lat1, lon1, lat2, lon2) {
  const R  = 6371e3
  const φ1 = (lat1 * Math.PI) / 180
  const φ2 = (lat2 * Math.PI) / 180
  const Δφ = ((lat2 - lat1) * Math.PI) / 180
  const Δλ = ((lon2 - lon1) * Math.PI) / 180
  const a  =
    Math.sin(Δφ / 2) ** 2 +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

// ─────────────────────────────────────────────────────────────────────────────
// GEOLOCATION
// ─────────────────────────────────────────────────────────────────────────────

watch(
  () => settings.data,
  (value) => { if (value?.allow_geolocation_tracking == 1) fetchLocation() },
  { immediate: true }
)

async function fetchLocation() {
  if (!navigator.geolocation) {
    locationStatus.value = __("Geolocation not supported")
    return
  }
  locationStatus.value = __("Locating…")
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      latitude.value       = pos.coords.latitude
      longitude.value      = pos.coords.longitude
      locationStatus.value = `Lat: ${latitude.value.toFixed(5)}, Long: ${longitude.value.toFixed(5)}`

      // ✅ Set expected location as soon as coords are acquired
      setExpectedLocation()
    },
    (err) => { locationStatus.value = err.message }
  )
  await loadUrls()
  await getLocationAPI(latitude.value, longitude.value)
}

// ─────────────────────────────────────────────────────────────────────────────
// SUBMIT
// ─────────────────────────────────────────────────────────────────────────────

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(";").shift()
}

async function getDeviceId() {
  let id = localStorage.getItem("hrms_device_id")
  if (id) return id
  const fp     = await FingerprintJS.load()
  const result = await fp.get()
  id = result.visitorId
  localStorage.setItem("hrms_device_id", id)
  return id
}

watch(
  () => typeofCheckIn.value?.value,
  (newVal, oldVal) => {
    if (newVal !== oldVal) {
      hospitalValue.value    = null
      carValue.value         = null
      leadValue.value        = null
      opportunityValue.value = null
    }
  }
)

function submitLog(logType) {
  const label = logType === "IN" ? __("Check-in") : __("Check-out")
  if (!faceMatched.value) {
    toast({ title: "Face Verification", text: "Face not matched", position: "bottom-center" })
    return
  }

  const refDocDT = typeofCheckIn.value?.value || lastLogRefDoctype.value || ""
  const refDocDN =
    hospitalValue.value?.value  ||
    carValue.value?.value       ||
    leadValue.value?.value      ||
    opportunityValue.value?.value ||
    lastLogRefName.value || ""

  currentLogRefDoctype.value = refDocDT
  currentLogRefName.value    = refDocDN

  checkins.insert.submit(
    {
      employee:     employee.data.name,
      log_type:     logType,
      time:         checkinTimestamp.value,
      latitude:     latitude.value,
      longitude:    longitude.value,
      location:     loginlocation.value,
      device_id:    device_id.value,
      reference_dt: refDocDT,
      reference_dn: refDocDN,
      description:  locationDescription.value,
    },
    {
      onSuccess(doc) {
        currentCheckINID.value = doc.name
        const now = new Date()
        const formattedDate =
          now.getFullYear() + "-" +
          String(now.getMonth() + 1).padStart(2, "0") + "-" +
          String(now.getDate()).padStart(2, "0")

        if (
          field_employee.value === "Yes" &&
          label === "Check-in" &&
          !forgetCheckOut.value &&
          lastLogRefTime.value === formattedDate
        ) {
          CreateCheckInJoureny()
        }

        forgetCheckOut.value = false
        isCheckOut           = false
        toast({ title: __("Success"), text: __("{0} successful!", [label]), position: "bottom-center" })
        stopCamera()
        router.back()
      },
    }
  )
}

async function CreateCheckInJoureny() {
  const distance = await getDistanceInMeters(
    latitude.value, longitude.value,
    lastLogLat.value, lastLogLan.value
  )
  const dis_km = distance ? Number((distance / 1000).toFixed(2)) : 0

  const now = new Date()
  const formattedDate =
    now.getFullYear() + "-" +
    String(now.getMonth() + 1).padStart(2, "0") + "-" +
    String(now.getDate()).padStart(2, "0")

  const csrf = window?.frappe?.csrf_token || window?.csrf_token || getCookie("csrf_token")

  await fetch("/api/method/hrms.api.hr_api.create_checkin_journey", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": csrf },
    body: JSON.stringify({
      employee:                employee.data.name,
      user:                    employee.data.user_id,
      checkout:                lastCheckOutID.value,
      checkout_reference:      lastLogRefDoctype.value,
      checkout_reference_name: lastLogRefName.value,
      checkin:                 currentCheckINID.value,
      checkin_reference:       currentLogRefDoctype.value,
      checkin_reference_name:  currentLogRefName.value,
      distance:                dis_km,
      date:                    formattedDate,
    }),
  })
}

function goBack() {
  stopCamera()
  router.back()
}

// ─────────────────────────────────────────────────────────────────────────────
// SALES EMPLOYEE HELPERS
// ─────────────────────────────────────────────────────────────────────────────

async function loadUrls() {
  const config     = await getRuntimeConfig()
  azure_key.value  = config.AZURE_KEY
  const url_config = await getRuntimeURLConfig()
  distance_url      = url_config.distance_url
  location_url      = url_config.location_url
  distance_response = url_config.distance_response
  location_response = url_config.location_response
}

async function createLead() {
  const csrf = window?.frappe?.csrf_token || window?.csrf_token || getCookie("csrf_token")
  const resp = await fetch("/api/method/hrms.api.hr_api.create_lead", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": csrf },
    body: JSON.stringify({
      first_name: newLead.first_name,
      mobile_no:  newLead.mobile_no,
      salutation: newLead.salutation.value,
    }),
  })
  const result = await resp.json()
  if (result.message) {
    const created = result.message.data
    const option  = {
      label: `${created.name} (${created.first_name}, ${created.mobile_no})`,
      value: created.name,
    }
    addLead(option)
    leadValue.value    = option
    newLead.first_name = ""
    newLead.mobile_no  = ""
    newLead.salutation = ""
    showLeadModal.value = false
  } else {
    console.error("Error Creating Lead:", result)
  }
}

async function createOpportunity() {
  const csrf = window?.frappe?.csrf_token || window?.csrf_token || getCookie("csrf_token")
  const resp = await fetch("/api/method/hrms.api.hr_api.create_opportunity", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": csrf },
    body: JSON.stringify({
      party_name:         newOpportunity.party_name.value,
      opportunity_from:   "Lead",
      opportunity_owner:  "",
      expected_closing:   newOpportunity.expected_closing,
      opportunity_amount: newOpportunity.opportunity_amount,
      probability:        newOpportunity.probability,
    }),
  })
  const result = await resp.json()
  if (result.message) {
    const created = result.message.data
    const option  = {
      label: `${created.name} (${created.opportunity_from}, ${created.party_name})`,
      value: created.name,
    }
    addOpportunity(option)
    opportunityValue.value = option
    Object.assign(newOpportunity, {
      party_name: "", opportunity_from: "Lead", opportunity_owner: "",
      expected_closing: "", opportunity_amount: "", probability: "",
    })
    showOpportunityModal.value = false
  } else {
    console.error("Error Creating Opportunity:", result)
  }
}

function buildUrl(template, replacements) {
  let url = template
  for (const key in replacements)
    url = url.replace(new RegExp(`\\$\\{${key}\\}`, "g"), replacements[key])
  return url
}

async function getDistanceInMeters(currentLat, currentLon, expectedLat, expectedLon) {
  if (!azure_key.value) { console.warn("Azure Key missing"); return 0 }
  const url = buildUrl(distance_url, {
    key: azure_key.value, currentLat, currentLon, expectedLat, expectedLon,
  })
  try {
    const data = await (await fetch(url)).json()
    return getValueByPath(data, distance_response) ?? 0
  } catch (err) {
    console.error("Azure Distance API Error:", err)
    return 0
  }
}

function getValueByPath(obj, path) {
  if (!obj || !path) return null
  return path
    .replace(/\?\./g, ".")
    .replace(/\[(\d+)\]/g, ".$1")
    .split(".")
    .filter(Boolean)
    .reduce((o, k) => (o && k in o ? o[k] : null), obj)
}

async function getLocationAPI(currentLat, currentLon) {
  const csrf = window?.frappe?.csrf_token || window?.csrf_token || getCookie("csrf_token")
  try {
    const frappeResp = await fetch(
      `/api/method/hrms.api.hr_api.find_location_by_latlon?lat=${currentLat}&lon=${currentLon}`,
      { method: "GET", credentials: "include",
        headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": csrf } }
    )
    const frappeResult = await frappeResp.json()

    if (frappeResult?.message?.found === false) {
      if (!azure_key.value) { stopCamera(); return null }
      const url     = buildUrl(location_url, { key: azure_key.value, currentLat, currentLon })
      const apiData = await (await fetch(url)).json()
      const saveResp = await fetch("/api/method/hrms.api.hr_api.save_location", {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": csrf },
        body: JSON.stringify({ payload: apiData }),
      })
      const saveResult = await saveResp.json()
      locationDescription.value = saveResult.message.display_name || ""
      return locationDescription.value
    }

    locationDescription.value = frappeResult.message.display_name || ""
    return locationDescription.value
  } catch (error) {
    console.error("Location API Error:", error)
    return null
  }
}

watch(leadValue, (val) => {
  if (val?.value === "create_new_lead") {
    showLeadModal.value = true
    leadValue.value     = null
  }
})

watch(opportunityValue, (val) => {
  if (val?.value === "create_new_opportunity") {
    showOpportunityModal.value = true
    opportunityValue.value     = null
  }
})
</script>

<style scoped>
/* ── Page layout ──────────────────────────────────────────────────────────── */
.verify-page {
  min-height: 100vh;
  /* background: linear-gradient(180deg, #0a0e1a 0%, #0d1526 60%, #0a1020 100%); */
  display: flex;
  flex-direction: column;
  padding: 0 0 2rem 0;
  gap: 0;
  color: #e8eaf0;
}

/* ── Header ───────────────────────────────────────────────────────────────── */
.verify-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem 1rem;
}

.back-btn {
  width: 36px;
  height: 36px;
  cursor: pointer;
  background: rgba(255, 255, 255, 1);
  border-radius: 50%;
  padding: 8px;
  filter: invert(1);
  transition: background 0.2s;
}
.back-btn:hover { background: rgba(255,255,255,0.14); }

.header-title {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: #000000;
}

.header-spacer { width: 36px; }

/* ── Scanner section ──────────────────────────────────────────────────────── */
.scanner-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 1.25rem 0;
  gap: 1rem;
}

.scan-instruction {
  font-size: 13px;
  color: #8fa3c8;
  letter-spacing: 0.2px;
  margin: 0;
  text-align: center;
}

/* Rectangle scanner frame */
.scanner-wrapper {
  position: relative;
  width: 100%;
  max-width: 300px;
  aspect-ratio: 3 / 4;
  border-radius: 8px;
  overflow: hidden;
}

.scanner-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: 8px;
}

/* Dark overlay tint on video */
.scanner-wrapper::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(10, 18, 40, 0.25);
  z-index: 1;
  border-radius: 8px;
}

/* Corner brackets */
.corner {
  position: absolute;
  width: 28px;
  height: 28px;
  z-index: 3;
}
.corner.top-left    { top: 12px;    left: 12px;  border-top: 3px solid #3b9eff;  border-left: 3px solid #3b9eff;  border-radius: 4px 0 0 0; }
.corner.top-right   { top: 12px;    right: 12px; border-top: 3px solid #3b9eff;  border-right: 3px solid #3b9eff; border-radius: 0 4px 0 0; }
.corner.bottom-left { bottom: 12px; left: 12px;  border-bottom: 3px solid #3b9eff; border-left: 3px solid #3b9eff; border-radius: 0 0 0 4px; }
.corner.bottom-right{ bottom: 12px; right: 12px; border-bottom: 3px solid #3b9eff; border-right: 3px solid #3b9eff; border-radius: 0 0 4px 0; }

/* Scan line */
.scan-line {
  position: absolute;
  left: 12px;
  right: 12px;
  height: 2px;
  z-index: 2;
  border-radius: 1px;
}

.scan-line.scanning {
  background: linear-gradient(90deg, transparent, #3b9eff, #60c8ff, #3b9eff, transparent);
  animation: scanMove 2s ease-in-out infinite;
}

.scan-line.matched {
  background: linear-gradient(90deg, transparent, #00d68f, #4dffc3, #00d68f, transparent);
  top: 50%;
  animation: matchPulse 1.2s ease-out;
}

@keyframes scanMove {
  0%   { top: 15%; opacity: 0.6; }
  50%  { top: 80%; opacity: 1;   }
  100% { top: 15%; opacity: 0.6; }
}

@keyframes matchPulse {
  0%   { opacity: 0; transform: scaleX(0.5); }
  50%  { opacity: 1; transform: scaleX(1.1); }
  100% { opacity: 0.8; transform: scaleX(1); }
}

/* Landmark dots on match */
.match-overlay {
  position: absolute;
  inset: 0;
  z-index: 3;
}

.dot {
  position: absolute;
  width: 6px;
  height: 6px;
  background: #00d68f;
  border-radius: 50%;
  box-shadow: 0 0 6px #00d68f;
  transform: translate(-50%, -50%);
  animation: dotAppear 0.3s ease forwards;
  opacity: 0;
}

@keyframes dotAppear {
  from { opacity: 0; transform: translate(-50%, -50%) scale(0); }
  to   { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}

/* Progress bar */
.progress-track {
  width: 100%;
  max-width: 300px;
  height: 4px;
  background: rgba(59, 158, 255, 0.15);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #1a6fff, #3b9eff, #60c8ff);
  border-radius: 2px;
  transition: width 0.6s ease;
}

.progress-bar.full {
  background: linear-gradient(90deg, #00a86b, #00d68f, #4dffc3);
}

.progress-label {
  font-size: 12px;
  color: #5a7aaa;
  margin: 0;
  letter-spacing: 0.3px;
}
/* ── Status pills ───────────────────────────────────────── */
.status-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0.75rem 1.25rem 0;
}

.status-pill {
  display: flex;
  flex-direction: column;
  gap: 8px;

  padding: 12px 16px;
  border-radius: 14px;
  border: 1px solid #9ca3af;
  font-size: 13px;
  background: #f3f4f6;
}

.row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-pill.pill-success {
  background: #16a34a1a;
  border-color: #278f5e4d;
  color: #16a34a;
}

.status-pill.pill-error {
  background: #fef2f2;
  border-color: #fca5a5;
  color: #dc2626;
}

.status-pill.pill-scanning {
  background: #eff6ff;
  border-color: #93c5fd;
  color: #2563eb;
}

.status-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  opacity: 0.85;
}

.status-icon svg {
  stroke: currentColor;
}

.status-label {
  font-weight: 500;
}

.status-value {
  font-weight: 600;
}

.status-dot {
  margin-left: auto;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.dot-green {
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.45);
}

.status-dot.dot-red {
  background: #ef4444;
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.45);
}

.status-dot.dot-pulse {
  background: #3b82f6;
  animation: dotPulse 1.4s ease-in-out infinite;
}

@keyframes dotPulse {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 6px rgba(59, 130, 246, 0.45);
  }
  50% {
    opacity: 0.4;
    box-shadow: 0 0 2px rgba(59, 130, 246, 0.2);
  }
}

/* ── Coordinates pill ─────────────────────────────────── */
.coords-pill {
  display: flex;
  flex-direction: column;
  gap: 8px;

  padding: 12px 16px;
  border-radius: 12px;

  background: rgba(209, 213, 219, 0.2); 
  border: 1px solid rgba(209, 213, 219);

  color: #374151;
}

.coords-pill .row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.coords-pill svg {
  flex-shrink: 0;
  stroke: #374151;
}

.coords-text {
  font-family: monospace;
  font-size: 12px;
  line-height: 1.35;
}
/* ── Checkbox row ─────────────────────────────────────────────────────────── */
.checkbox-row {
  padding: 0.5rem 1.25rem 0;
}

/* ── Dropdowns section ────────────────────────────────────────────────────── */
.dropdowns-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  padding: 0.75rem 1.25rem 0;
}

/* ── Modals ───────────────────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  /* background: rgba(0, 0, 0, 0.7); */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  backdrop-filter: blur(4px);
}

.modal-card {
  background: #ffffff;
  border: 1px solid rgba(59, 158, 255, 0.2);
  padding: 1.5rem;
  border-radius: 16px;
  width: 320px;
  box-shadow: 0 24px 60px rgba(0,0,0,0.6);
}

.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: #000000;
  margin: 0 0 1rem;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 1.25rem;
}

.modal-btn {
  padding: 7px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: opacity 0.15s;
}
.modal-btn:hover { opacity: 0.85; }
.modal-btn.cancel {
  background: rgba(255,255,255,0.08);
  color: #8fa3c8;
}
.modal-btn.save {
  background: #1a6fff;
  color: #ffffff;
}

/* ── Action buttons ───────────────────────────────────────────────────────── */
.action-section {
  padding: 1rem 1.25rem 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.confirm-btn {
  width: 100%;
  padding: 0.875rem !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  border-radius: 12px !important;
  background: linear-gradient(135deg, #1a6fff, #3b9eff) !important;
  color: white !important;
  border: none !important;
  letter-spacing: 0.3px;
  box-shadow: 0 8px 24px rgba(26, 111, 255, 0.35) !important;
  transition: opacity 0.2s, transform 0.15s !important;
}
.confirm-btn:hover  { opacity: 0.9 !important; transform: translateY(-1px) !important; }
.confirm-btn:active { transform: translateY(0) !important; }

.confirm-btn.secondary {
  background: linear-gradient(135deg, #0a9e6e, #00d68f) !important;
  box-shadow: 0 8px 24px rgba(0, 214, 143, 0.25) !important;
}
</style>