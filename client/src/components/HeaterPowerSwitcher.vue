<template>
  <div class="row">
    <div class="col">
      <form @submit.prevent="">
        <fieldset :disabled="!isEnabled">
          <legend>Heater output power</legend>
          <p class="grouped">
            <input type="number" readonly v-model="outputPower" />
            <button type="button" @click="decrease">-5%</button>
            <button type="button" @click="increase">+5%</button>
            <button type="button" class="button primary" @click="apply">
              Apply
            </button>
          </p>
        </fieldset>
      </form>
    </div>
  </div>
</template>

<script setup>
import { watch, ref, computed } from 'vue'
import { useAppStore } from '../store/AppStore'

const appStore = useAppStore()

const outputPower = ref(appStore.heaterOutputPower.value)

const isPending = ref(false)
const isEnabled = computed(() => appStore.mode == 2 && !isPending.value)

watch(
  () => appStore.heaterOutputPower.value,
  () => {
    isPending.value = false
    outputPower.value = appStore.heaterOutputPower.value
  }
)

function increase() {
  if (!isEnabled) return

  outputPower.value += 5

  if (outputPower.value > 100) outputPower.value = 100
}

function decrease() {
  if (!isEnabled) return
  outputPower.value -= 5

  if (outputPower.value < 0) outputPower.value = 0
}

function apply() {
  if (!isEnabled) return

  isPending.value = true
  appStore.setHeaterOutputPower(outputPower.value)
}
</script>

<style lang="scss" scoped></style>
