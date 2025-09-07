<template>
  <h1>Connection settings</h1>
  <form @submit.prevent="connect">
    <p class="text-error" v-if="msg">
      {{ msg }}
    </p>
    <p>
      <label for="mqtt_broker_host__input">MQTT broker host</label>
      <input
        type="text"
        id="mqtt_broker_host__input"
        v-model="appStore.mqttHost"
        :disabled="isConnectionPending"
      />
    </p>
    <p>
      <label for="mqtt_broker_port__input">MQTT broker port</label>
      <input
        type="text"
        id="mqtt_broker_port__input"
        v-model="appStore.mqttPort"
        :disabled="isConnectionPending"
      />
    </p>
    <p>
      <label for="mqtt_username__input">MQTT username</label>
      <input
        type="text"
        id="mqtt_username__input"
        v-model="appStore.mqttUsername"
        :disabled="isConnectionPending"
      />
    </p>
    <p>
      <label for="mqtt_password__input">MQTT password</label>
      <input
        type="password"
        id="mqtt_password__input"
        v-model="appStore.mqttPassword"
        :disabled="isConnectionPending"
      />
    </p>
    <p>
      <label for="device_name__input">Device name</label>
      <input
        type="text"
        id="device_name__input"
        v-model="appStore.deviceName"
        :disabled="isConnectionPending"
      />
    </p>
    <button
      type="submit"
      class="button primary"
      :disabled="isConnectionPending"
    >
      Connect
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '../store/AppStore'

const appStore = useAppStore()

const msg = ref('')
const isConnectionPending = ref(false)

async function connect() {
  isConnectionPending.value = true
  await appStore.connect()

  msg.value = appStore.isConnected
    ? ''
    : `Connection to broker "ws://${appStore.mqttHost}:${appStore.mqttPort}/" not established!`

  isConnectionPending.value = false
}
</script>

<style scoped></style>
