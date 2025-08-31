<template>
  <div class="row">
    <div class="col">
      <nav class="nav">
        <div class="nav-left">
          <div class="tabs">
            <a
              :class="{ active: currentTab == 0 }"
              @click="currentTab = 0"
              href="#"
              >Temperatures</a
            >
            <a
              :class="{ active: currentTab == 1 }"
              @click="currentTab = 1"
              href="#"
              >Weight</a
            >
            <a
              :class="{ active: currentTab == 2 }"
              @click="currentTab = 2"
              href="#"
              >Heater output power</a
            >
          </div>
        </div>
      </nav>
    </div>
  </div>
  <div class="row">
    <div class="col">
      <apexchart
        type="line"
        :series="seriesTemperature"
        :options="optionsTemperature"
        v-if="currentTab == 0"
      ></apexchart>
      <apexchart
        type="line"
        :series="seriesWeight"
        :options="optionsWeight"
        v-if="currentTab == 1"
      ></apexchart>
      <apexchart
        type="line"
        :series="seriesHeater"
        :options="optionsHeater"
        v-if="currentTab == 2"
      ></apexchart>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAppStore } from '../store/AppStore'

const appStore = useAppStore()

const currentTab = ref(0)

const optionsTemperature = ref({
  xaxis: {
    type: 'datetime',
    labels: {
      datetimeUTC: false
    },
    tickAmount: 50
  },
  yaxis: {
    min: 0,
    max: 100
  }
})

const optionsWeight = ref({
  xaxis: {
    type: 'datetime',
    labels: {
      datetimeUTC: false
    },
    tickAmount: 50
  },
  yaxis: {
    min: 0,
    max: 20
  }
})
const optionsHeater = ref({
  xaxis: {
    type: 'datetime',
    labels: {
      datetimeUTC: false
    },
    tickAmount: 50
  },
  yaxis: {
    min: 0,
    max: 100
  }
})

const seriesTemperature = computed(() => [
  {
    name: 'bottom temperature',
    data: appStore.bottomTemperatureCalibratedHistory
  },
  {
    name: 'top temperature',
    data: appStore.topTemperatureCalibratedHistory
  }
])

const seriesWeight = computed(() => [
  {
    name: 'weight',
    data: appStore.weightCalibratedHistory
  }
])

const seriesHeater = computed(() => [
  {
    name: 'heater output power',
    data: appStore.heaterOutputPowerHistory
  }
])
</script>

<style scoped></style>
