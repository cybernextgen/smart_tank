<template>
  <h3>Auto mode setpoints</h3>
  <p>
    Setpoints for automatic mode. Device will be disabled after weight setpoint
    will be reached.
  </p>
  <div class="row">
    <div class="col">
      <ParameterInput
        :parameter-name="'Bottom temperature setpoint, °C'"
        :value="appStore.bottomTemperatureSP"
        :min-value="20"
        :max-value="99"
        :step-value="0.1"
        @apply-value="appStore.changeBottomTemperatureSP"
      ></ParameterInput>
    </div>
    <div class="col">
      <ParameterInput
        :parameter-name="'Weight setpoint, Kg'"
        :value="weightSP"
        :min-value="0"
        :max-value="15"
        :step-value="0.1"
        @apply-value="changeWeightSP"
      ></ParameterInput>
    </div>
  </div>
  <h3>AH setpoints</h3>
  <p>
    Device will be disabled if this alarms high (AH) setpoints will be reached.
  </p>
  <div class="row">
    <div class="col">
      <ParameterInput
        :parameter-name="'Bottom temperature AH, °C'"
        :value="appStore.bottomTemperatureAH"
        :min-value="20"
        :max-value="99"
        :step-value="0.1"
        @apply-value="appStore.changeBottomTemperatureAH"
      ></ParameterInput>
    </div>
    <div class="col">
      <ParameterInput
        :parameter-name="'Top temperature AH, °C'"
        :value="appStore.topTemperatureAH"
        :min-value="20"
        :max-value="99"
        :step-value="0.1"
        @apply-value="appStore.changeTopTemperatureAH"
      ></ParameterInput>
    </div>
  </div>
</template>

<script setup>
import ParameterInput from './ParameterInput.vue'
import { useAppStore } from '../store/AppStore'
import { computed } from 'vue'

const appStore = useAppStore()

const weightSP = computed(() => {
  return appStore.weightSP / 1000
})

function changeWeightSP(newValue) {
  appStore.changeWeightSP(newValue * 1000)
}
</script>

<style scoped></style>
