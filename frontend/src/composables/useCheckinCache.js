/**
 * useCheckinCache.js
 *
 * Preloads everything CheckinConfirm.vue needs so that page opens instantly:
 *   • face-api.js models
 *   • user profile-image face descriptor
 *   • Lead / Opportunity / Hospital / CAR dropdown options
 *   • Location list
 *
 * Call  preload(userImageUrl)  once from Home.vue → onMounted.
 * CheckinConfirm.vue reads the reactive refs directly — no extra fetches.
 */

import { ref, readonly } from "vue"
import * as faceapi from "face-api.js"

// ─── singleton state (module-level so it survives route changes) ───────────────

const modelsReady      = ref(false)
const descriptorReady  = ref(false)
const optionsReady     = ref(false)

const referenceDescriptor = ref(null)   // Float32Array from face-api
const leadOptions         = ref([])
const OpportunityOptions  = ref([])
const HospitalOptions     = ref([])
const CarOptions          = ref([])
const locations           = ref([])

// track whether a preload is already running so we never double-load
let _modelsPromise     = null
let _descriptorPromise = null
let _optionsPromise    = null

// ─── helpers ──────────────────────────────────────────────────────────────────

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(";").shift()
}

function csrfToken() {
  return (
    window?.frappe?.csrf_token ||
    window?.csrf_token ||
    getCookie("csrf_token") ||
    ""
  )
}

async function fetchOptions(docType) {
  const endpoint = `/api/method/hrms.api.hr_api.get_all_${docType.toLowerCase()}`
  const resp = await fetch(endpoint, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-Frappe-CSRF-Token": csrfToken(),
    },
  })
  const result = await resp.json()
  return result?.message?.data || result?.data || []
}

async function fetchLocationList() {
  const resp = await fetch(
    "/api/method/hrms.api.location_api.get_all_locations",
    {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-Frappe-CSRF-Token": csrfToken(),
      },
    }
  )
  const result = await resp.json()
  return result?.message?.data || []
}

// ─── individual loaders (idempotent – skip if already done) ───────────────────

function loadModels() {
  if (modelsReady.value) return Promise.resolve()
  if (_modelsPromise) return _modelsPromise

  _modelsPromise = (async () => {
    const MODEL_URL = "/assets/hrms/models"
    await Promise.all([
      faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
      faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
      faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
    ])
    modelsReady.value = true
  })()

  return _modelsPromise
}

function loadDescriptor(userImageUrl) {
  if (descriptorReady.value) return Promise.resolve()
  if (_descriptorPromise) return _descriptorPromise
  if (!userImageUrl) return Promise.resolve()

  _descriptorPromise = (async () => {
    // models must be ready first
    await loadModels()

    const img = await faceapi.fetchImage(userImageUrl)
    const detection = await faceapi
      .detectSingleFace(img, new faceapi.TinyFaceDetectorOptions())
      .withFaceLandmarks()
      .withFaceDescriptor()

    if (detection) {
      referenceDescriptor.value = detection.descriptor
      descriptorReady.value = true
    }
  })()

  return _descriptorPromise
}

function loadAllOptions() {
  if (optionsReady.value) return Promise.resolve()
  if (_optionsPromise) return _optionsPromise

  _optionsPromise = (async () => {
    try {
      const [leadData, oppData, hospitalData, carData, locationData] =
        await Promise.all([
          fetchOptions("lead"),
          fetchOptions("opportunity"),
          fetchOptions("hospital"),
          fetchOptions("car"),
          fetchLocationList(),
        ])

      // ── Leads ──────────────────────────────────────────────────────────────
      const leadArray = Array.isArray(leadData)
        ? leadData
        : Object.values(leadData)

      leadOptions.value = [
        ...leadArray.map((i) => {
          const extras = [i.lead_name, i.mobile_no].filter(Boolean)
          return {
            label: extras.length ? `${i.name} (${extras.join(", ")})` : i.name,
            value: i.name,
          }
        }),
        { label: "+ Create New Lead", value: "create_new_lead" },
      ]

      // ── Opportunities ──────────────────────────────────────────────────────
      const oppArray = Array.isArray(oppData)
        ? oppData
        : Object.values(oppData)

      OpportunityOptions.value = [
        ...oppArray.map((i) => {
          const extras = [i.opportunity_from, i.title].filter(Boolean)
          return {
            label: extras.length ? `${i.name} (${extras.join(", ")})` : i.name,
            value: i.name,
          }
        }),
        { label: "+ Create New Opportunity", value: "create_new_opportunity" },
      ]

      // ── Hospitals ──────────────────────────────────────────────────────────
      const hospitalArray = Array.isArray(hospitalData)
        ? hospitalData
        : Object.values(hospitalData)

      HospitalOptions.value = hospitalArray.map((i) => {
        const extras = [i.title].filter(Boolean)
        return {
          label: extras.length ? `${i.name} (${extras.join(", ")})` : i.name,
          value: i.name,
        }
      })

      // ── Cars ───────────────────────────────────────────────────────────────
      const carArray = Array.isArray(carData)
        ? carData
        : Object.values(carData)

      CarOptions.value = carArray.map((i) => ({
        label: i.name,
        value: i.name,
      }))

      // ── Locations ──────────────────────────────────────────────────────────
      locations.value = locationData

      optionsReady.value = true
    } catch (err) {
      console.error("[useCheckinCache] loadAllOptions error:", err)
      // reset so a retry is possible
      _optionsPromise = null
    }
  })()

  return _optionsPromise
}

// ─── public API ───────────────────────────────────────────────────────────────

/**
 * preload(userImageUrl)
 *   Call once from Home.vue → onMounted.
 *   Kicks off models + descriptor + dropdown options in parallel.
 */
function preload(userImageUrl) {
  // fire and forget – errors are caught inside each loader
  loadModels().catch(console.error)
  loadDescriptor(userImageUrl).catch(console.error)
  loadAllOptions().catch(console.error)
}

/**
 * addLead(option)  – called after a new lead is created in the modal
 * Prepends the new option so the dropdown reflects it immediately.
 */
function addLead(option) {
  // remove the sentinel "create_new_lead" entry, prepend new option, re-append sentinel
  const withoutSentinel = leadOptions.value.filter(
    (o) => o.value !== "create_new_lead"
  )
  leadOptions.value = [
    option,
    ...withoutSentinel,
    { label: "+ Create New Lead", value: "create_new_lead" },
  ]
}

function addOpportunity(option) {
  const withoutSentinel = OpportunityOptions.value.filter(
    (o) => o.value !== "create_new_opportunity"
  )
  OpportunityOptions.value = [
    option,
    ...withoutSentinel,
    { label: "+ Create New Opportunity", value: "create_new_opportunity" },
  ]
}

// ─── composable export ────────────────────────────────────────────────────────

export function useCheckinCache() {
  return {
    // state (readonly to prevent accidental mutation from outside)
    modelsReady:      readonly(modelsReady),
    descriptorReady:  readonly(descriptorReady),
    optionsReady:     readonly(optionsReady),
    referenceDescriptor,   // CheckinConfirm needs to read the raw Float32Array
    leadOptions,
    OpportunityOptions,
    HospitalOptions,
    CarOptions,
    locations,

    // actions
    preload,
    loadModels,
    loadDescriptor,
    loadAllOptions,
    addLead,
    addOpportunity,
  }
}