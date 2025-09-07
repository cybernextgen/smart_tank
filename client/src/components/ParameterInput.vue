<template>
  <div class="row">
    <div class="col">
      <form @submit.prevent="apply">
        <fieldset :disabled="isDisabled">
          <legend>{{ parameterName }}</legend>
          <p class="grouped">
            <input
              type="number"
              v-model="parameterValue"
              :min="minValue"
              :max="maxValue"
              :step="stepValue"
            />
            <button
              type="button"
              class="button primary"
              @click="apply"
              :disabled="isButtonDisabled"
            >
              Apply
            </button>
          </p>
        </fieldset>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'

const props = defineProps({
  parameterName: String,
  value: Number,
  minValue: Number,
  maxValue: Number,
  stepValue: Number
})

const emit = defineEmits({
  applyValue: (newValue) => typeof newValue === 'number'
})

const parameterValue = ref(props.minValue)

const isDisabled = ref(false)

onMounted(() => {
  parameterValue.value = props.value
})

watch(
  () => props.value,
  () => {
    parameterValue.value = props.value
  }
)

const isButtonDisabled = computed(() => {
  return props.value == parameterValue.value
})

function apply() {
  if (isButtonDisabled.value) return
  isDisabled.value = true
  emit('applyValue', parameterValue.value)
  setTimeout(() => {
    isDisabled.value = false
  }, 3000)
}
</script>

<style scoped></style>
