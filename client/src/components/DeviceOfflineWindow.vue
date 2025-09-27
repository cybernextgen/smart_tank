<template>
  <dialog class="offline_dialog" ref="dialog" @keypress="">
    <div class="row">
      <div class="col">
        <h4>Device is offline</h4>
        <p>The device not responded on ping requests.</p>
        <ul>
          <li>Check application connection settings;</li>
          <li>Check device name;</li>
          <li>Check device connection settings;</li>
          <li>Check device power supply.</li>
        </ul>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <button
          ref="disconnectButton"
          class="button error"
          type="button"
          @click="appStore.disconnect"
        >
          Disconnect
        </button>
      </div>
    </div>
  </dialog>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useAppStore } from '../store/AppStore'

const dialog = ref()
const appStore = useAppStore()

function initDialog() {
  if (!appStore.isDeviceOnline) {
    dialog.value.showModal()
  } else {
    dialog.value.close()
  }
}

onMounted(() => {
  initDialog()
})

watch(
  () => appStore.isDeviceOnline,
  () => {
    initDialog()
  }
)
</script>

<style scoped>
.offline_dialog:focus {
  outline: none;
}

.offline_dialog {
  border: none;
  border-radius: 4px;
}
</style>
