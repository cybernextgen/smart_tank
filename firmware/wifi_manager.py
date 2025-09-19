import machine
import network
import socket
import re
import time
import ujson

ENCODING = "utf-8"
SETTINGS_FILE_NAME = "wifi_settings.json"


class WiFiSettings:

    def __init__(
        self,
        ssid: str = "",
        password: str = "",
        device_name: str = "smart_tank",
        mqtt_host: str = "",
        mqtt_port: int = 0,
        mqtt_user: str = "",
        mqtt_password: str = "",
    ):
        self.ssid = ssid
        self.password = password
        self.device_name = device_name
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password

    def _to_dict(self):
        return {
            "ssid": self.ssid,
            "password": self.password,
            "device_name": self.device_name,
            "mqtt_host": self.mqtt_host,
            "mqtt_port": self.mqtt_port,
            "mqtt_user": self.mqtt_user,
            "mqtt_password": self.mqtt_password,
        }

    def to_json(self):
        return ujson.dumps(self._to_dict())

    @staticmethod
    def from_json(json_string):
        json_dict = ujson.loads(json_string)
        return WiFiSettings(**json_dict)


class WifiManager:

    def __init__(
        self,
        ssid="WifiManager",
        password="wifimanager",
        reboot=True,
        configuration_mode=False,
    ):
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_sta.active(True)
        self.wlan_ap = network.WLAN(network.AP_IF)

        if len(ssid) > 32:
            raise Exception("The SSID cannot be longer than 32 characters.")
        else:
            self.ap_ssid = ssid
        if len(password) < 8:
            raise Exception("The password cannot be less than 8 characters long.")
        else:
            self.ap_password = password

        self.ap_authmode = 3
        self.wlan_sta.disconnect()

        self.reboot = reboot
        self.configuration_mode = configuration_mode

    def connect(self):
        if not self.configuration_mode:
            if self.wlan_sta.isconnected():
                return
            settings = self.read_settings()
            for ssid, *_ in self.wlan_sta.scan():
                ssid = ssid.decode(ENCODING)
                if ssid == settings.ssid:
                    password = settings.password
                    if self.wifi_connect(ssid, password):
                        return
            if __debug__:
                print(
                    "Could not connect to any WiFi network. Starting the configuration portal..."
                )
        self.web_server()

    def disconnect(self):
        if self.wlan_sta.isconnected():
            self.wlan_sta.disconnect()

    def is_connected(self):
        return self.wlan_sta.isconnected()

    def get_address(self):
        return self.wlan_sta.ifconfig()

    def write_settings(self, settings: WiFiSettings):
        with open(SETTINGS_FILE_NAME, "w") as file:
            file.write(settings.to_json())

    def read_settings(self) -> WiFiSettings:
        try:
            with open(SETTINGS_FILE_NAME) as file:
                return WiFiSettings.from_json(file.read())
        except OSError:
            return WiFiSettings()

    def wifi_connect(self, ssid, password):
        if __debug__:
            print("Trying to connect to:", ssid)

        self.wlan_sta.connect(ssid, password)
        for _ in range(100):
            if self.wlan_sta.isconnected():
                if __debug__:
                    print("\nConnected! Network information:", self.wlan_sta.ifconfig())
                return True
            else:
                if __debug__:
                    print(".", end="")
                time.sleep_ms(100)
        if __debug__:
            print("\nConnection failed!")

        self.wlan_sta.disconnect()
        return False

    def web_server(self):
        self.wlan_ap.active(True)
        self.wlan_ap.config(
            essid=self.ap_ssid, password=self.ap_password, authmode=self.ap_authmode
        )
        server_socket = socket.socket()
        server_socket.close()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", 80))
        server_socket.listen(1)
        if __debug__:
            print(
                "Connect to",
                self.ap_ssid,
                "with the password",
                self.ap_password,
                "and access the captive portal at",
                self.wlan_ap.ifconfig()[0],
            )
        while True:
            if self.wlan_sta.isconnected():
                self.wlan_ap.active(False)
                if self.reboot:
                    if __debug__:
                        print("The device will reboot in 5 seconds.")

                    time.sleep(5)
                    machine.reset()
            self.client, addr = server_socket.accept()
            try:
                self.client.settimeout(5.0)
                self.request = b""
                try:
                    while True:
                        if b"\r\n\r\n" in self.request:
                            self.request += self.client.recv(512)
                            break
                        self.request += self.client.recv(128)
                except Exception as error:
                    if __debug__:
                        print(error)
                    pass
                if self.request:
                    req = self.request.decode(ENCODING, "ignore")
                    if __debug__:
                        print(req)
                    url = (
                        re.search(r"(?:GET|POST) /(.*?)(?:\?.*?)? HTTP", req)
                        .group(1)
                        .rstrip("/")
                    )
                    if url == "":
                        self.handle_root()
                    elif url == "configure":
                        self.handle_configure()
                    else:
                        self.handle_not_found()
            except Exception as error:
                if __debug__:
                    print(error)
                return
            finally:
                self.client.close()

    def send_header(self, status_code=200):
        self.client.send("""HTTP/1.1 {0} OK\r\n""".format(status_code))
        self.client.send("""Content-Type: text/html\r\n""")
        self.client.send("""Connection: close\r\n""")

    def send_response(self, payload, status_code=200):
        self.send_header(status_code)
        self.client.sendall(
            f"""
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <title>WiFi Manager</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="icon" href="data:,">
                </head>
                <body>
                    {payload}
                </body>
            </html>
        """
        )
        self.client.close()

    def handle_root(self):
        settings = self.read_settings()

        self.send_header()
        self.client.sendall(
            f"""
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <title>Smart tank configuration</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="icon" href="data:,">
                    <style>
                        label {{ display: inline-block; width: 100px}}
                        .i {{ display: inline-block; width: 150px }}
                    </style>
                </head>
                <body>
                    <h1>Smart tank configuration</h1>
                    <form action="/configure" method="post" accept-charset="utf-8">
                        <fieldset>
                        <legend>WiFi settings</legend>
                        <p><label for="ssid">SSID</label><select id="ssid" name="ssid" class="i" value="{settings.ssid}">
        """
        )

        for ssid, *_ in self.wlan_sta.scan():
            ssid = ssid.decode(ENCODING)

            if not ssid:
                continue

            self.client.sendall(
                """
                        <option value="{0}" id="{0}">{0}</option>
            """.format(
                    ssid
                )
            )
        self.client.sendall(
            f"""
                        </select></p>
                        <p><label for="password">Password</label><input type="password" id="password" name="password" class="i" value="{settings.password}"></p>
                        </fieldset>
                        <fieldset>
                        <legend>MQTT settings</legend>
                        <p><label for="d_n">Device name</label><input type="text" id="d_n" name="d_n" class="i" required="" value="{settings.device_name}"></p>
                        <p><label for="b_h">Broker host</label><input type="text" id="b_h" name="b_h" class="i" required="" value="{settings.mqtt_host}"></p>
                        <p><label for="b_prt">Broker port</label><input type="text" id="b_prt" name="b_prt" class="i" required="" value="{settings.mqtt_port}"></p>
                        <p><label for="b_l">Login</label><input type="text" id="b_l" name="b_l" class="i" value="{settings.mqtt_user}"></p>
                        <p><label for="b_pwd">Password</label><input type="password" id="b_pwd" name="b_pwd" class="i" value="{settings.mqtt_password}"></p>
                        </fieldset>
                        <p><input type="submit" value="Save" class="i"></p>
                    </form>
                </body>
            </html>
        """
        )
        self.client.close()

    def handle_configure(self):
        decoded = self.url_decode(self.request).decode(ENCODING, "ignore")
        regex = r"ssid=([^&]*)&password=(.*)&d_n=(.*)&b_h=(.*)&b_prt=(.*)&b_l=(.*)&b_pwd=(.*)"
        match = re.search(regex, decoded)
        if match:
            settings = WiFiSettings(*[match.group(index) for index in range(1, 8)])

            if len(settings.ssid) == 0:
                self.send_response(
                    """
                    <p>SSID must be provided!</p>
                    <p>Go back and try again!</p>
                """,
                    400,
                )
            elif self.wifi_connect(settings.ssid, settings.password):
                self.send_response(
                    """
                    <p>Successfully connected to</p>
                    <h1>{0}</h1>
                    <p>IP address: {1}</p>
                """.format(
                        settings.ssid, self.wlan_sta.ifconfig()[0]
                    )
                )
                self.write_settings(settings)
                time.sleep(5)
            else:
                self.send_response(
                    """
                    <p>Could not connect to</p>
                    <h1>{0}</h1>
                    <p>Go back and try again!</p>
                """.format(
                        settings.ssid
                    )
                )
                time.sleep(5)
        else:
            self.send_response(
                """
                <p>Parameters not found!</p>
            """,
                400,
            )
            time.sleep(5)

    def handle_not_found(self):
        self.send_response(
            """
            <p>Page not found!</p>
        """,
            404,
        )

    def url_decode(self, url_string):
        if not url_string:
            return b""

        if isinstance(url_string, str):
            url_string = url_string.encode("utf-8")

        bits = url_string.split(b"%")

        if len(bits) == 1:
            return url_string

        res = [bits[0]]
        appnd = res.append
        hextobyte_cache = {}

        for item in bits[1:]:
            try:
                code = item[:2]
                char = hextobyte_cache.get(code)
                if char is None:
                    char = hextobyte_cache[code] = bytes([int(code, 16)])
                appnd(char)
                appnd(item[2:])
            except Exception as error:
                if __debug__:
                    print(error)
                appnd(b"%")
                appnd(item)

        return b"".join(res)
