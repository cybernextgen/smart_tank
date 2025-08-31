<template>
  <main class="container">
    <section id="connection_settings" v-if="!appStore.isConnected">
      <ConnectionSettings></ConnectionSettings>
    </section>
    <section id="dashboard" v-if="appStore.isConnected">
      <DeviceDashboard></DeviceDashboard>
    </section>
    <section id="weight_calibration"></section>
  </main>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAppStore } from './store/AppStore'
import ConnectionSettings from './components/AppConnectionSettings.vue'
import DeviceDashboard from './components/AppDeviceDashboard.vue'

const appStore = useAppStore()

onMounted(() => {
  appStore.isConnected = false
})
</script>

<style scoped></style>
