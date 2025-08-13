# Smart tank

Upgrade for boiling device. Adds "smart" functions to device, such as:

- Boiling product weight measurement using 4 load cells;
- Heater control using PWM;
- Measurement product temperature with several DS18B20 sensors;
- Automatic mode (stabilizing product temperature with PID regulator until weight not ritched setpoint) or remote mode (device can be controlled from remote server);
- Standalone HTTP server for initial configuration (using WiFi AdHoc mode);
- MQTT over WiFi;
- OLED display.

# Hardware

Required modules:

- ESP32_devkitc_v4 module (ESP32WROOM32D based development board);

# Software
