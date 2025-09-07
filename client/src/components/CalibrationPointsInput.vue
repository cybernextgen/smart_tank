<template>
  <div class="row">
    <div class="col">
      <form @submit.prevent="applyPoints">
        <fieldset :disabled="isDisabled">
          <legend v-if="parameterName">{{ parameterName }}</legend>
          <div class="row">
            <div class="col">
              <label>Current raw value ({{ rawUnits }})</label>
            </div>
            <div class="col">
              <label>Current calibrated value ({{ calibratedUnits }})</label>
            </div>
          </div>
          <div class="row">
            <div class="col">
              <input type="number" readonly v-model="rawValue" />
            </div>
            <div class="col">
              <input type="number" readonly v-model="calibratedValue" />
            </div>
          </div>
          <div class="row">
            <div class="col">
              <label>Point 1 raw value ({{ rawUnits }})</label>
            </div>
            <div class="col">
              <label>Point 1 calibrated value ({{ calibratedUnits }})</label>
            </div>
          </div>
          <div class="row">
            <div class="col">
              <input
                type="number"
                v-model="calibrationPoints[0].rawValue"
                :min="rawMinValue"
                :max="rawMaxValue"
                :step="rawStepValue"
              />
            </div>
            <div class="col">
              <input
                type="number"
                v-model="calibrationPoints[0].calibratedValue"
                :min="calibratedMinValue"
                :max="calibratedMaxValue"
                :step="calibratedStepValue"
              />
            </div>
          </div>
          <div class="row">
            <div class="col">
              <label>Point 2 raw value ({{ rawUnits }})</label>
            </div>
            <div class="col">
              <label>Point 2 calibrated value ({{ calibratedUnits }})</label>
            </div>
          </div>
          <div class="row">
            <div class="col">
              <input
                type="number"
                v-model="calibrationPoints[1].rawValue"
                :min="rawMinValue"
                :max="rawMaxValue"
                :step="rawStepValue"
              />
            </div>
            <div class="col">
              <input
                type="number"
                v-model="calibrationPoints[1].calibratedValue"
                :min="calibratedMinValue"
                :max="calibratedMaxValue"
                :step="calibratedStepValue"
              />
            </div>
          </div>
          <p class="grouped">
            <button
              type="button"
              class="button primary"
              @click="applyPoints"
              :disabled="isDisabled"
            >
              Apply
            </button>
          </p>
        </fieldset>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch, ref, computed } from 'vue'
import { CalibrationPoint } from '../models/CalibrationPoint'
import { Measurement } from '../models/Measurement'

const props = defineProps({
  parameterName: String,
  value: Array,
  currentRawValue: Measurement,
  currentCalibratedValue: Measurement,
  rawMinValue: Number,
  rawMaxValue: Number,
  calibratedMinValue: Number,
  calibratedMaxValue: Number,
  rawStepValue: Number,
  calibratedStepValue: Number,
  rawUnits: String,
  calibratedUnits: String
})

const calibrationPoints = ref([
  new CalibrationPoint(0, 0),
  new CalibrationPoint(1, 1)
])

const rawValue = ref(0)
const calibratedValue = ref(0)
const isDisabled = ref(false)

function initPoints() {
  props.value.forEach((element, index) => {
    calibrationPoints.value[index].rawValue = element.rawValue
    calibrationPoints.value[index].calibratedValue = element.calibratedValue
  })
}

onMounted(() => {
  initPoints()
})

watch(
  () => props.value,
  () => {
    initPoints()
  }
)

watch(
  () => props.currentRawValue,
  () => {
    rawValue.value = props.currentRawValue.value
  }
)

watch(
  () => props.currentCalibratedValue,
  () => {
    calibratedValue.value = props.currentCalibratedValue.value
  }
)

const emit = defineEmits(['applyPoints'])

function applyPoints() {
  isDisabled.value = true
  emit('applyPoints', calibrationPoints.value)
  setTimeout(() => {
    isDisabled.value = false
  }, 3000)
}
</script>

<style scoped></style>
