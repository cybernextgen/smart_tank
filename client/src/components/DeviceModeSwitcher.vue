<template>
  <form @submit.prevent="">
    <fieldset :disabled="isPending">
      <legend>Mode</legend>
      <p class="buttons">
        <button
          class="button"
          type="button"
          :class="{ primary: isDisabledMode, outline: !isDisabledMode }"
          @click="setDisableMode"
        >
          Disabled
        </button>
        <button
          class="button"
          type="button"
          :class="{ primary: isAutoMode, outline: !isAutoMode }"
          @click="setAutoMode"
        >
          Auto
        </button>
        <button
          class="button"
          type="button"
          :class="{ primary: isRemoteMode, outline: !isRemoteMode }"
          @click="setRemoteMode"
        >
          Remote
        </button>
      </p>
    </fieldset>
  </form>
</template>

<script setup>
import { computed, watch, ref } from 'vue'
import { useAppStore } from '../store/AppStore'

const appStore = useAppStore()

const DISABLED_MODE = 0
const AUTO_MODE = 1
const REMOTE_MODE = 2

const isDisabledMode = computed(() => appStore.mode === DISABLED_MODE)
const isAutoMode = computed(() => appStore.mode === AUTO_MODE)
const isRemoteMode = computed(() => appStore.mode === REMOTE_MODE)

const isPending = ref(false)

watch(
  () => appStore.mode,
  () => {
    isPending.value = false
  }
)

function setDisableMode() {
  isPending.value = true
  appStore.changeMode(DISABLED_MODE)
}

function setAutoMode() {
  isPending.value = true
  appStore.changeMode(AUTO_MODE)
}

function setRemoteMode() {
  isPending.value = true
  appStore.changeMode(REMOTE_MODE)
}
</script>

<style scoped>
.buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  align-content: center;
}

.button {
  flex-grow: 1;
}
</style>
