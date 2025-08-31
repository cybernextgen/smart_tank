import { defineStore } from 'pinia'
import { ref } from 'vue'
import mqtt from 'mqtt'
import { Measurement } from '../models/Measurement'
import { Message } from '../models/Message'

export const useAppStore = defineStore(
  'appStore',
  () => {
    const mqttHost = ref('localhost')
    const mqttPort = ref('1883')
    const mqttUsername = ref('')
    const mqttPassword = ref('')

    const deviceName = ref('')
    const isConnected = ref(false)
    const isDeviceOnline = ref(false)
    const mqttClient = ref()

    const pingIntervalId = ref()
    const pongIntervalId = ref()

    const mode = ref(0)
    const uptime = ref(new Measurement())

    const bottomTemperature = ref(new Measurement())
    const bottomTemperatureCalibrated = ref(new Measurement())
    const bottomTemperatureCalibratedHistory = ref([])

    const topTemperature = ref(new Measurement())
    const topTemperatureCalibrated = ref(new Measurement())
    const topTemperatureCalibratedHistory = ref([])

    const weight = ref(new Measurement())
    const weightCalibrated = ref(new Measurement())
    const weightCalibratedHistory = ref([])

    const heaterOutputPower = ref(new Measurement())
    const heaterOutputPowerHistory = ref([])

    const ipAddress = ref(new Measurement())
    const freeMemory = ref(new Measurement())

    const messagesHistory = ref([])

    function clearPingInterval() {
      if (!pingIntervalId.value) return

      clearInterval(pingIntervalId.value)
      pingIntervalId.value = undefined
    }

    function clearPongInterval() {
      if (!pongIntervalId.value) return

      clearTimeout(pongIntervalId.value)
      pongIntervalId.value = undefined
    }

    function getOutputTopic(topic) {
      return `${deviceName.value}/from_device/${topic}`
    }

    function getInputTopic(topic) {
      return `${deviceName.value}/to_device/${topic}`
    }

    function resetConnectionFlags() {
      isConnected.value = false
      isDeviceOnline.value = false
    }

    function setMeasurement(rawData, variable) {
      variable.value = new Measurement(rawData['value'], rawData['quality'])
    }

    function addToHistory(measurement, variable, datetime) {
      if (measurement.isBad()) return

      variable.value.push({ x: datetime.getTime(), y: measurement.value })
      if (variable.value.length > 50) {
        variable.value.shift()
      }
    }

    function addMessageToHistory(rawData) {}

    async function connect() {
      try {
        const client = await mqtt.connectAsync({
          host: mqttHost.value,
          port: mqttPort.value,
          username: mqttUsername.value,
          password: mqttPassword.value,
          reconnectPeriod: 0,
          connectTimeout: 2000
        })

        mqttClient.value = client

        await client.subscribeAsync(getOutputTopic('#'))

        isConnected.value = true

        client.on('message', (topic, message) => {
          if (topic === getOutputTopic('pong')) {
            isDeviceOnline.value = true
            clearPongInterval()
          } else if (topic === getOutputTopic('parameters')) {
            const messageJSON = JSON.parse(message)
            console.log(messageJSON)
            mode.value = messageJSON['mode'] || 0
          } else if (topic === getOutputTopic('sensors')) {
            const sensorsDataJSON = JSON.parse(message)

            setMeasurement(sensorsDataJSON['uptime'], uptime)
            setMeasurement(
              sensorsDataJSON['bottom_temperature'],
              bottomTemperature
            )
            setMeasurement(
              sensorsDataJSON['bottom_temperature_calibrated'],
              bottomTemperatureCalibrated
            )
            setMeasurement(sensorsDataJSON['top_temperature'], topTemperature)
            setMeasurement(
              sensorsDataJSON['top_temperature_calibrated'],
              topTemperatureCalibrated
            )
            setMeasurement(sensorsDataJSON['weight'], weight)
            setMeasurement(
              sensorsDataJSON['weight_calibrated'],
              weightCalibrated
            )
            weightCalibrated.value.value = (
              weightCalibrated.value.value / 1000
            ).toFixed(2)

            setMeasurement(
              sensorsDataJSON['heater_output_power'],
              heaterOutputPower
            )

            setMeasurement(sensorsDataJSON['ip_address'], ipAddress)
            setMeasurement(sensorsDataJSON['free_memory'], freeMemory)

            const currentDatetime = new Date()
            addToHistory(
              bottomTemperatureCalibrated.value,
              bottomTemperatureCalibratedHistory,
              currentDatetime
            )
            addToHistory(
              topTemperatureCalibrated.value,
              topTemperatureCalibratedHistory,
              currentDatetime
            )
            addToHistory(
              weightCalibrated.value,
              weightCalibratedHistory,
              currentDatetime
            )
            addToHistory(
              heaterOutputPower.value,
              heaterOutputPowerHistory,
              currentDatetime
            )
          } else if (topic === getOutputTopic('status')) {
            const messageJSON = JSON.parse(message)
            messagesHistory.value.push(
              new Message(messageJSON['status'], messageJSON['message'])
            )

            while (messagesHistory.value.length > 3) {
              messagesHistory.value.shift()
            }
          }
        })

        pingDevice()

        pingIntervalId.value = setInterval(async () => {
          await pingDevice()
        }, 10_000)
      } catch (e) {
        isConnected.value = false
      }
    }

    async function disconnect() {
      if (!mqttClient.value) return

      clearPingInterval()
      clearPongInterval()

      try {
        await mqttClient.value.endAsync()
      } finally {
        mqttClient.value = undefined

        resetConnectionFlags()
      }
    }

    async function pingDevice() {
      if (!mqttClient.value || !isConnected.value) {
        clearPingInterval()
        return
      }

      try {
        await mqttClient.value.publishAsync(getInputTopic('ping'), '')

        clearPongInterval()

        pongIntervalId.value = setTimeout(
          () => (isDeviceOnline.value = false),
          10_000
        )
      } catch {
        resetConnectionFlags()
      }
    }

    async function changeMode(newMode) {
      if (!mqttClient.value) return

      try {
        await mqttClient.value.publishAsync(
          getInputTopic('parameters/mode'),
          `${newMode}`
        )
      } catch (e) {
        resetConnectionFlags()
      }
    }

    async function setHeaterOutputPower(newPower) {
      if (!mqttClient.value) return

      try {
        await mqttClient.value.publishAsync(
          getInputTopic('heater_power'),
          `${newPower}`
        )
      } catch (e) {
        resetConnectionFlags()
      }
    }

    return {
      mqttHost,
      mqttUsername,
      mqttPort,
      mqttPassword,
      deviceName,
      isConnected,
      isDeviceOnline,
      mode,
      uptime,
      bottomTemperature,
      bottomTemperatureCalibrated,
      topTemperature,
      topTemperatureCalibrated,
      weight,
      weightCalibrated,
      ipAddress,
      freeMemory,
      heaterOutputPower,
      bottomTemperatureCalibratedHistory,
      topTemperatureCalibratedHistory,
      weightCalibratedHistory,
      heaterOutputPowerHistory,
      messagesHistory,
      connect,
      disconnect,
      changeMode,
      setHeaterOutputPower
    }
  },

  {
    persist: true
  }
)
