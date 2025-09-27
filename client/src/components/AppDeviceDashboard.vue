<template>
  <h1>
    {{ appStore.deviceName }}
    <DeviceConnectionState></DeviceConnectionState>
  </h1>
  <nav class="nav">
    <div class="nav-left">
      <div class="tabs">
        <a
          :class="{ active: isDashboardTabActive }"
          @click="activateDasboardTab"
          href="#"
          >Dashboard</a
        >
        <a
          :class="{ active: isSetpointsTabActive }"
          @click="activateSetpointsTab"
          href="#"
          >Setpoints</a
        >
        <a
          :class="{ active: isCalibrationTabActive }"
          @click="activateCalibrationTab"
          href="#"
          >Calibration</a
        >
      </div>
    </div>
    <div class="nav-right">
      <AppButtonWithConfirmation
        :child-class="'button error'"
        :confirmation-dialog-text="'Disconnect from broker?'"
        @confirmed="disconnect()"
        >Disconnect</AppButtonWithConfirmation
      >
    </div>
  </nav>
  <div v-show="isDashboardTabActive">
    <div class="row">
      <div class="col">
        <DeviceModeSwitcher></DeviceModeSwitcher>
        <HeaterPowerSwitcher></HeaterPowerSwitcher>
        <CurrentSensorsData></CurrentSensorsData>
      </div>
      <div class="col">
        <SensorsHistoryCharts></SensorsHistoryCharts>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <MessagesHistory></MessagesHistory>
      </div>
    </div>
  </div>
  <div v-show="isSetpointsTabActive">
    <AppDeviceSetpoints></AppDeviceSetpoints>
  </div>
  <div v-show="isCalibrationTabActive">
    <AppDeviceCalibration></AppDeviceCalibration>
  </div>
  <DeviceOfflineWindow></DeviceOfflineWindow>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAppStore } from '../store/AppStore'
import AppButtonWithConfirmation from './AppButtonWithConfirmation.vue'
import DeviceModeSwitcher from './DeviceModeSwitcher.vue'
import CurrentSensorsData from './CurrentSensorsData.vue'
import SensorsHistoryCharts from './SensorsHistoryCharts.vue'
import HeaterPowerSwitcher from './HeaterPowerSwitcher.vue'
import MessagesHistory from './MessagesHistory.vue'
import AppDeviceSetpoints from './AppDeviceSetpoints.vue'
import AppDeviceCalibration from './AppDeviceCalibration.vue'
import DeviceConnectionState from './DeviceConnectionState.vue'
import DeviceOfflineWindow from './DeviceOfflineWindow.vue'

const appStore = useAppStore()
const confirmDialog = ref()

const DASHBOARD_TAB_ID = 0
const SETPOINTS_TAB_ID = 1
const CALIBRATION_TAB_ID = 2

const currentTab = ref(DASHBOARD_TAB_ID)

const isDashboardTabActive = computed(
  () => currentTab.value === DASHBOARD_TAB_ID
)
const isSetpointsTabActive = computed(
  () => currentTab.value === SETPOINTS_TAB_ID
)
const isCalibrationTabActive = computed(
  () => currentTab.value === CALIBRATION_TAB_ID
)

function activateDasboardTab() {
  currentTab.value = DASHBOARD_TAB_ID
}

function activateSetpointsTab() {
  currentTab.value = SETPOINTS_TAB_ID
}

function activateCalibrationTab() {
  currentTab.value = CALIBRATION_TAB_ID
}

function disconnect() {
  appStore.disconnect()
}
</script>

<style scoped>
nav {
  margin-bottom: 20px;
}
</style>
