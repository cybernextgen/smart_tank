<script setup lang="ts">
import { ref } from 'vue'

const dialog = ref()
const message = ref()
const acceptButton = ref()
const closeButton = ref()

defineExpose({ show })

function show(msg = 'Confirm action?') {
  message.value = msg
  dialog.value.showModal()
  return new Promise((resolve) => {
    if (acceptButton.value) {
      acceptButton.value.addEventListener('click', () => {
        dialog.value?.close()
        resolve(true)
      })
    }
    if (closeButton.value) {
      closeButton.value.addEventListener('click', () => {
        dialog.value.close()
        resolve(false)
      })
    }
  })
}
</script>
<template>
  <dialog class="confirm_dialog" ref="dialog">
    <div class="row">
      <div class="col">
        <h4>Confirmation</h4>
        <p>{{ message }}</p>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <button ref="acceptButton" class="button error" type="button">
          Yes
        </button>
      </div>
      <div class="col is-right">
        <button ref="closeButton" class="button outline" type="button">
          No
        </button>
      </div>
    </div>
  </dialog>
</template>
<style scoped>
.confirm_dialog:focus {
  outline: none;
}

.confirm_dialog {
  border: none;
  border-radius: 4px;
}
</style>
