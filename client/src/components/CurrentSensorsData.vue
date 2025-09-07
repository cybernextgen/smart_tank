<template>
  <div class="row">
    <div class="col">
      <table class="striped">
        <thead>
          <tr>
            <th>Sensor name</th>
            <th>Units of measurement</th>
            <th>Last value</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>IP-address</td>
            <td>-</td>
            <td>{{ appStore.ipAddress.value }}</td>
          </tr>
          <tr>
            <td>Free memory</td>
            <td>Kb</td>
            <td>{{ freeMemoryFormatted }}</td>
          </tr>
          <tr>
            <td>Uptime</td>
            <td>-</td>
            <td>{{ uptimeFormatted }}</td>
          </tr>
          <tr>
            <td>Bottom temperature</td>
            <td>°C</td>
            <td>{{ appStore.bottomTemperatureCalibrated.value }}</td>
          </tr>
          <tr>
            <td>Top temperature</td>
            <td>°C</td>
            <td>{{ appStore.topTemperatureCalibrated.value }}</td>
          </tr>
          <tr>
            <td>Weight</td>
            <td>Kg</td>
            <td>{{ appStore.weightCalibratedKg.value }}</td>
          </tr>
          <tr>
            <td>Heater output power</td>
            <td>%</td>
            <td>{{ appStore.heaterOutputPower.value }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../store/AppStore'
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'

const appStore = useAppStore()
dayjs.extend(duration)

const uptimeFormatted = computed(() => {
  const d = dayjs.duration(appStore.uptime.value, 'seconds')

  return `${d.format('DD')} days ${d.format('HH:mm:ss')}`
})

const freeMemoryFormatted = computed(() => {
  const f = Math.round(appStore.freeMemory.value / 1024)
  return f
})
</script>

<style scoped>
.sensor_value {
  font-weight: 800;
}
</style>
