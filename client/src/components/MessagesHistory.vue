<template>
  <div class="row">
    <div class="col">
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Message</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="msg in messages"
            :class="{
              'text-primary': msg.statusCode == 200,
              'text-error': msg.statusCode >= 400
            }"
          >
            <td>{{ formatDatetime(msg.datetime) }}</td>
            <td>{{ msg.text }}</td>
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

const appStore = useAppStore()

const messages = computed(() => [...appStore.messagesHistory].reverse())

function formatDatetime(datetime) {
  return dayjs(datetime).format('DD.MM.YYYY HH:mm:ss')
}
</script>

<style scoped></style>
