<template>
  <h3>PID regulator coefficients</h3>
  <p>
    Coefficients for adjustment automatic mode regulator.
    <a
      href="https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller#Loop_tuning"
      target="_blank"
      rel="noopener noreferrer"
      >Read more...</a
    >
  </p>
  <div class="row">
    <div class="col">
      <ParameterInput
        :parameter-name="'Proportional'"
        :value="appStore.pidP"
        :min-value="0"
        :max-value="10"
        :step-value="0.01"
        @apply-value="appStore.changePidP"
      ></ParameterInput>
    </div>
    <div class="col">
      <ParameterInput
        :parameter-name="'Integeral'"
        :value="appStore.pidI"
        :min-value="0"
        :max-value="10"
        :step-value="0.01"
        @apply-value="appStore.changePidI"
      ></ParameterInput>
    </div>
    <div class="col">
      <ParameterInput
        :parameter-name="'Derivative'"
        :value="appStore.pidD"
        :min-value="0"
        :max-value="10"
        :step-value="0.01"
        @apply-value="appStore.changePidD"
      ></ParameterInput>
    </div>
  </div>
  <h3>Calibration points</h3>
  <p>
    Calibration point defines the nominal input value and the desired output
    value for sensors.
  </p>

  <div class="row">
    <div class="col">
      <CalibrationPointsInput
        :value="appStore.weightCalibrationPoints"
        :parameter-name="'Weight'"
        :current-raw-value="appStore.weight"
        :current-calibrated-value="appStore.weightCalibrated"
        :raw-units="'ADC code'"
        :calibrated-units="'Gramms'"
        :raw-min-value="-1e8"
        :raw-max-value="1e8"
        :calibrated-min-value="0"
        :calibrated-max-value="40"
        :raw-step-value="1"
        :calibrated-step-value="1"
        @apply-points="appStore.changeWeightCalibrationPoints"
      ></CalibrationPointsInput>
    </div>
  </div>

  <div class="row">
    <div class="col">
      <CalibrationPointsInput
        :value="appStore.bottomTemperatureCalibrationPoints"
        :parameter-name="'Bottom temperature'"
        :current-raw-value="appStore.bottomTemperature"
        :current-calibrated-value="appStore.bottomTemperatureCalibrated"
        :raw-units="'°C'"
        :calibrated-units="'°C'"
        :raw-min-value="0"
        :raw-max-value="100"
        :calibrated-min-value="0"
        :calibrated-max-value="100"
        :raw-step-value="0.1"
        :calibrated-step-value="0.1"
        @apply-points="appStore.changeBottomTemperatureCalibrationPoints"
      ></CalibrationPointsInput>
    </div>
  </div>

  <div class="row">
    <div class="col">
      <CalibrationPointsInput
        :value="appStore.topTemperatureCalibrationPoints"
        :parameter-name="'Top temperature'"
        :current-raw-value="appStore.topTemperature"
        :current-calibrated-value="appStore.topTemperatureCalibrated"
        :raw-units="'°C'"
        :calibrated-units="'°C'"
        :raw-min-value="0"
        :raw-max-value="100"
        :calibrated-min-value="0"
        :calibrated-max-value="100"
        :raw-step-value="0.1"
        :calibrated-step-value="0.1"
        @apply-points="appStore.changeTopTemperatureCalibrationPoints"
      ></CalibrationPointsInput>
    </div>
  </div>
</template>

<script setup>
import ParameterInput from './ParameterInput.vue'
import { useAppStore } from '../store/AppStore'
import CalibrationPointsInput from './CalibrationPointsInput.vue'

const appStore = useAppStore()
</script>

<style scoped></style>
