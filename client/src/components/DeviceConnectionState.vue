<template>
  <span
    class="tag is-small"
    :class="{
      'text-success': appStore.isDeviceOnline,
      'text-error': !appStore.isDeviceOnline
    }"
    >{{ deviceStateName }}</span
  >
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../store/AppStore'

const appStore = useAppStore()

const deviceStateName = computed(() =>
  appStore.isDeviceOnline ? 'Online' : 'Offline'
)
</script>

<style scoped></style>
