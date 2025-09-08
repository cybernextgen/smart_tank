# Smart tank

Upgrade for boiling device. Adds "smart" functions to device, such as:

- Boiling product weight measurement using 4 load cells;
- Heater control using PWM;
- Measurement product temperature with several DS18B20 sensors;
- Automatic mode (stabilizing product temperature with PID regulator until weight not ritched setpoint) or remote mode (device can be controlled from remote server);
- Standalone HTTP server for initial configuration (using WiFi AdHoc mode);
- MQTT over WiFi.

## Hardware

### Required modules

- ESP32_devkitc_v4 module (ESP32WROOM32D based development board);
- Step down DC-DC converter (for example, LM2596 or XL4015 based);
- Power supply 12v 5a;
- Miniature circuit breaker 1p B6;
- 4x10Kg load cells;
- 4xHX711 load cells amplifier;
- 2xDS18B20 temperature sensors with heat resistent wires (PTFE or silicon insulation).

## Software

### Firmware

1. Install `micropython==1.25.0` release into the ESP32 devboard (https://micropython.org/download/ESP32_GENERIC/);
2. Clone this repo. Install dependencies:

```sh
   $ git clone https://github.com/cybernextgen/smart_tank
   $ cd smart_tank/firmware
   $ uv sync

```

3. Connect the devboard to computer, transfer firmware files:

```sh
$ uv run mpremote fs cp *.py :.
```

### Client app

1. Install `nodejs>=22.0` engine;
2. Clone this repo. Install dependencies:

```sh
$ git clone https://github.com/cybernextgen/smart_tank
$ cd smart_tank/client

# Start dev-server
$ npm start

# Package app
$ npm run package
# Start app
$ ./out/client-linux-x64/client
```

### Screenshots

![Connection settings](/img/connection_settings.png)

![Dashboard](/img/dashboard.png)

![Dashboard](/img/setpoints.png)

![Dashboard](/img/calibration.png)

### Communication protocol

Device communicates with clients apps using MQTT protocol. There are two data streams - from device to client and from client to device.

#### Topics from device to client

##### **{{device_name}}/from_device/parameters**

Device publish (after power on or after changes occurred) parameters, which are stored in non-volatile memory. Messages are retained. Message example:

```js
{
  "top_temperature_ah": 70.5, // alarm temperature setpoint, °C, heater shutdown,
  "bottom_temperature_ah": 90 // alarm temperature setpoint, °C, heater shutdown
  "bottom_temperature_sp": 70, // temperature setpoint for automatic mode, °C
  "weight_sp": 5500.0, // weight setpoint for automatic mode, gramms
  "output_max_power": 70, // heater maximum output power limitation, percents
  "mode": 1, // device working mode. 0 - disabled, 1 - auto, 2 - remote
  "output_pwm_interval_ms": 1000, // heater PWM pulses interval in milliseconds
  "pid_p": 1.5, // PI regulator proportional value
  "pid_i": 10, // PI regulator integral value
  "weight_calibration_points": [
    { "calibrated_value": 0, "raw_value": -224980 },
    { "calibrated_value": 10000, "raw_value": 1705616 }
  ],
  "bottom_temperature_calibration_points": [
    { "calibrated_value": 0, "raw_value": 0 },
    { "calibrated_value": 1, "raw_value": 1 }
  ],
  "top_temperature_calibration_points": [
    { "calibrated_value": 0, "raw_value": 0 },
    { "calibrated_value": 1, "raw_value": 1 }
  ],
}
```

##### **{{device_name}}/from_device/sensors**

Device publish current sensors measured values and it's quality:

- 0 - measured value are valid;
- 1 - measured value are bad (sensor not ready or not working properly).

Data published every 5 seconds after device powered on. Message example:

```js
{
  "heater_output_power": { "value": 0, "quality": 0 }, // heater output power, percents
  "top_temperature": { "value": 25.5625, "quality": 0 }, // raw temperature, °C
  "bottom_temperature_calibrated": { "value": 24.4375, "quality": 0 }, // calibrated temperature, °C
  "bottom_temperature": { "value": 24.4375, "quality": 0 }, // raw temperature, °C
  "weight": { "value": 1121544, "quality": 0 }, // raw weight ADS code
  "ip_address": { "value": "192.168.1.110", "quality": 0 },
  "free_memory": { "value": 97744, "quality": 0 }, // MCU free RAM, bytes
  "weight_calibrated": { "value": 6974.654, "quality": 0 }, // calibrated weight, gramms
  "top_temperature_calibrated": { "value": 25.5625, "quality": 0 }, // calibrated temperature, °C
  "uptime": { "value": 2606.643, "quality": 0 } // device uptime, seconds
}
```

##### **{{device_name}}/from_device/pong**

Device publish empty message after recieving message from topic `{{device_name}}/to_device/ping`

##### **{{device_name}}/from_device/status**

Device publish execution status of last recieved command from client. Message example:

```js
{ "message": "wrong device mode", "status": 400 }
```

or

```js
{ "message": "ok", "status": 200 }
```

#### Topics from client to device

##### **{{device_name}}/to_device/parameters/mode**

Client publish message with new device working mode value:

- 0 - disabled;
- 1 - auto mode;
- 2 - remote mode.

##### **{{device_name}}/to_device/parameters/(top_temperature_ah|bottom_temperature_ah|bottom_temperatrue_sp|weight_sp|pid_p|pid_i)**

Client publish new parameter value as float pointing number.

##### **{{device_name}}/to_device/parameters/(bottom_temperature_calibration_points|top_temperature_calibration_points|weight_calibration_points)**

Client publish message with calibration points data. Data must contain array of two calibration points. Message example:

```js
[
  { calibrated_value: 0, raw_value: 0 },
  { calibrated_value: 1, raw_value: 1 }
];
```

##### **{{device_name}}/to_device/heater_power**

Client publish message with new heater power value. Works only for remote mode.

##### **{{device_name}}/to_device/ping**

Client publish empty message to this topic. Device must reply with empty message using topic `{{device_name}}/from_device/pong`. When device in remote mode, client must ping device at least once every 30 seconds. Otherwise, mode will be switched to "disabled".
