import { defineStore } from 'pinia'
import { ref } from 'vue'
import mqtt from 'mqtt'
import { Measurement } from '../models/Measurement'
import { Message } from '../models/Message'
import { CalibrationPoint } from '../models/CalibrationPoint'

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
    const weightCalibratedKg = ref(new Measurement())
    const weightCalibratedHistory = ref([])

    const heaterOutputPower = ref(new Measurement())
    const heaterOutputPowerHistory = ref([])

    const ipAddress = ref(new Measurement())
    const freeMemory = ref(new Measurement())

    const bottomTemperatureSP = ref(0)
    const bottomTemperatureAH = ref(0)
    const weightSP = ref(0)
    const topTemperatureAH = ref(0)
    const pidP = ref(0)
    const pidI = ref(0)
    const pidD = ref(0)

    const weightCalibrationPoints = ref([
      new CalibrationPoint(0, 0),
      new CalibrationPoint(1, 1)
    ])
    const bottomTemperatureCalibrationPoints = ref([
      new CalibrationPoint(0, 0),
      new CalibrationPoint(1, 1)
    ])
    const topTemperatureCalibrationPoints = ref([
      new CalibrationPoint(0, 0),
      new CalibrationPoint(1, 1)
    ])

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

    function setCalibrationPoints(rawData, variable) {
      if (!rawData || rawData.length != 2) return

      variable.value = []
      rawData.forEach((element) => {
        variable.value.push(
          new CalibrationPoint(
            element['raw_value'],
            element['calibrated_value']
          )
        )
      })
    }

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
            mode.value = messageJSON['mode'] || 0
            bottomTemperatureSP.value =
              messageJSON['bottom_temperature_sp'] || 0
            bottomTemperatureAH.value =
              messageJSON['bottom_temperature_ah'] || 0
            weightSP.value = messageJSON['weight_sp'] || 0
            topTemperatureAH.value = messageJSON['top_temperature_ah'] || 0
            pidI.value = messageJSON['pid_i'] || 0
            pidP.value = messageJSON['pid_p'] || 0
            pidD.value = messageJSON['pid_d'] || 0
            setCalibrationPoints(
              messageJSON['weight_calibration_points'],
              weightCalibrationPoints
            )
            setCalibrationPoints(
              messageJSON['bottom_temperature_calibration_points'],
              bottomTemperatureCalibrationPoints
            )
            setCalibrationPoints(
              messageJSON['top_temperature_calibration_points'],
              topTemperatureCalibrationPoints
            )
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
            weightCalibrated.value.value =
              weightCalibrated.value.value.toFixed(0)
            weightCalibratedKg.value.value = (
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
              weightCalibratedKg.value,
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

        pongIntervalId.value = setTimeout(() => {
          isDeviceOnline.value = false
        }, 10_000)
      } catch {
        resetConnectionFlags()
      }
    }

    async function changeBottomTemperatureSP(newValue) {
      return changeParameter('bottom_temperature_sp', newValue)
    }

    async function changeBottomTemperatureAH(newValue) {
      return changeParameter('bottom_temperature_ah', newValue)
    }

    async function changeTopTemperatureAH(newValue) {
      return changeParameter('top_temperature_ah', newValue)
    }

    async function changeWeightSP(newValue) {
      return changeParameter('weight_sp', newValue)
    }

    async function changePidP(newValue) {
      return changeParameter('pid_p', newValue)
    }

    async function changePidI(newValue) {
      return changeParameter('pid_i', newValue)
    }

    async function changePidD(newValue) {
      return changeParameter('pid_d', newValue)
    }

    async function changeParameter(parameterName, parameterValue) {
      if (!mqttClient.value) return

      const parameterNames = [
        'mode',
        'top_temperature_ah',
        'bottom_temperature_ah',
        'bottom_temperature_sp',
        'weight_sp',
        'output_max_power',
        'output_pwm_interval_ms',
        'pid_p',
        'pid_i',
        'pid_d'
      ]
      if (!parameterNames.includes(parameterName)) return

      try {
        await mqttClient.value.publishAsync(
          getInputTopic(`parameters/${parameterName}`),
          `${parameterValue}`
        )
      } catch (e) {
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

    async function changeCalibrationPoints(parameterName, newPoints) {
      if (!mqttClient.value) return

      const parameterNames = [
        'weight_calibration_points',
        'bottom_temperature_calibration_points',
        'top_temperature_calibration_points'
      ]
      if (!parameterNames.includes(parameterName)) return

      const p = []
      newPoints.forEach((element) => {
        p.push({
          raw_value: element.rawValue,
          calibrated_value: element.calibratedValue
        })
      })

      await mqttClient.value.publishAsync(
        getInputTopic(`parameters/${parameterName}`),
        JSON.stringify(p)
      )
    }

    async function changeWeightCalibrationPoints(newPoints) {
      return changeCalibrationPoints('weight_calibration_points', newPoints)
    }

    async function changeBottomTemperatureCalibrationPoints(newPoints) {
      return changeCalibrationPoints(
        'bottom_temperature_calibration_points',
        newPoints
      )
    }

    async function changeTopTemperatureCalibrationPoints(newPoints) {
      return changeCalibrationPoints(
        'top_temperature_calibration_points',
        newPoints
      )
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
      weightCalibratedKg,
      ipAddress,
      freeMemory,
      heaterOutputPower,
      bottomTemperatureCalibratedHistory,
      topTemperatureCalibratedHistory,
      weightCalibratedHistory,
      heaterOutputPowerHistory,
      messagesHistory,
      bottomTemperatureSP,
      bottomTemperatureAH,
      topTemperatureAH,
      weightSP,
      pidI,
      pidP,
      pidD,
      weightCalibrationPoints,
      bottomTemperatureCalibrationPoints,
      topTemperatureCalibrationPoints,
      connect,
      disconnect,
      changeMode,
      setHeaterOutputPower,
      changeBottomTemperatureSP,
      changeBottomTemperatureAH,
      changeTopTemperatureAH,
      changeWeightSP,
      changePidP,
      changePidI,
      changePidD,
      changeWeightCalibrationPoints,
      changeBottomTemperatureCalibrationPoints,
      changeTopTemperatureCalibrationPoints
    }
  },

  {
    persist: true
  }
)
