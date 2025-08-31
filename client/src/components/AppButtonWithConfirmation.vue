<script setup lang="ts">
import { ref } from 'vue'
import AppConfirmDialog from './AppConfirmDialog.vue'

const props = defineProps<{
  childClass: string
  confirmationDialogText: string
}>()
const emit = defineEmits(['confirmed'])
const confirmDialog = ref()

async function showDialog() {
  if (!confirmDialog.value) return
  if (await confirmDialog.value.show(props.confirmationDialogText)) {
    emit('confirmed')
  }
}
</script>
<template>
  <button :class="props.childClass" @click="showDialog()" type="button">
    <slot />
  </button>
  <AppConfirmDialog ref="confirmDialog"></AppConfirmDialog>
</template>
<style scoped></style>
