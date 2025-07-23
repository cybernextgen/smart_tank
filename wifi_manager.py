import machine
import network
import socket
import re
import time

ENCODING = "utf-8"


class WifiManager:

    def __init__(
        self,
        ssid="WifiManager",
        password="wifimanager",
        reboot=True,
        debug=False,
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

        # There is no encryption, it's just a plain text archive. Be aware of this security problem!
        self.settings_file = "settings.dat"

        # Prevents the device from automatically trying to connect to the last saved network without first going through the steps defined in the code.
        self.wlan_sta.disconnect()

        self.reboot = reboot
        self.debug = debug
        self.configuration_mode = configuration_mode

    def connect(self):
        if not self.configuration_mode:
            if self.wlan_sta.isconnected():
                return
            settings = self.read_settings()
            for ssid, *_ in self.wlan_sta.scan():
                ssid = ssid.decode(ENCODING)
                if ssid == settings.get("ssid"):
                    password = settings["password"]
                    if self.wifi_connect(ssid, password):
                        return
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

    def write_settings(self, settings):
        lines = []
        lines.append(
            "{};{};{};{};{};{};{}\n".format(
                settings["ssid"],
                settings["password"],
                settings["device_name"],
                settings["mqtt_host"],
                settings["mqtt_port"],
                settings["mqtt_user"],
                settings["mqtt_password"],
            )
        )
        with open(self.settings_file, "w") as file:
            file.write("".join(lines))

    def read_settings(self):
        lines = []
        try:
            with open(self.settings_file) as file:
                lines = file.readlines()
        except Exception as error:
            if self.debug:
                print(error)
            pass
        settings = {}
        for line in lines:
            raw_settings = line.strip().split(";")
            settings["ssid"] = raw_settings[0]
            settings["password"] = raw_settings[1]
            settings["device_name"] = raw_settings[2]
            settings["mqtt_host"] = raw_settings[3]
            settings["mqtt_port"] = raw_settings[4]
            settings["mqtt_user"] = raw_settings[5]
            settings["mqtt_password"] = raw_settings[6]
        return settings

    def wifi_connect(self, ssid, password):
        print("Trying to connect to:", ssid)
        self.wlan_sta.connect(ssid, password)
        for _ in range(100):
            if self.wlan_sta.isconnected():
                print("\nConnected! Network information:", self.wlan_sta.ifconfig())
                return True
            else:
                print(".", end="")
                time.sleep_ms(100)
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
                    print("The device will reboot in 5 seconds.")
                    time.sleep(5)
                    machine.reset()
            self.client, addr = server_socket.accept()
            try:
                self.client.settimeout(5.0)
                self.request = b""
                try:
                    while True:
                        if "\r\n\r\n" in self.request:
                            # Fix for Safari browser
                            self.request += self.client.recv(512)
                            break
                        self.request += self.client.recv(128)
                except Exception as error:
                    # It's normal to receive timeout errors in this stage, we can safely ignore them.
                    if self.debug:
                        print(error)
                    pass
                if self.request:
                    if self.debug:
                        print(self.url_decode(self.request))
                    url = (
                        re.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", self.request)
                        .group(1)
                        .decode("utf-8")
                        .rstrip("/")
                    )
                    if url == "":
                        self.handle_root()
                    elif url == "configure":
                        self.handle_configure()
                    else:
                        self.handle_not_found()
            except Exception as error:
                if self.debug:
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
            """
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <title>WiFi Manager</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="icon" href="data:,">
                </head>
                <body>
                    {0}
                </body>
            </html>
        """.format(
                payload
            )
        )
        self.client.close()

    def handle_root(self):
        self.send_header()
        self.client.sendall(
            """
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
                        <p><label for="ssid">SSID</label><select id="ssid" name="ssid" class="i">
        """.format(
                self.ap_ssid
            )
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
            """
                        </select></p>
                        <p><label for="password">Password</label><input type="password" id="password" name="password" class="i"></p>
                        </fieldset>
                        <fieldset>
                        <legend>MQTT settings</legend>
                        <p><label for="d_n">Device name</label><input type="text" id="d_n" name="d_n" class="i" required=""></p>
                        <p><label for="b_h">Broker host</label><input type="text" id="b_h" name="b_h" class="i" required=""></p>
                        <p><label for="b_prt">Broker port</label><input type="text" id="b_prt" name="b_prt" class="i" required="" value="1883"></p>
                        <p><label for="b_l">Login</label><input type="text" id="b_l" name="b_l" class="i"></p>
                        <p><label for="b_pwd">Password</label><input type="password" id="b_pwd" name="b_pwd" class="i"></p>
                        </fieldset>
                        <p><input type="submit" value="Save" class="i"></p>
                    </form>
                </body>
            </html>
        """
        )
        self.client.close()

    def handle_configure(self):
        decoded = self.url_decode(self.request)
        regex = "ssid=([^&]*)&password=(.*)&d_n=(.*)&b_h=(.*)&b_prt=(.*)&b_l=(.*)&b_pwd=(.*)"
        match = re.search(regex, decoded)
        if match:
            ssid = match.group(1).decode(ENCODING)
            password = match.group(2).decode(ENCODING)
            device_name = match.group(3).decode(ENCODING)
            mqtt_host = match.group(4).decode(ENCODING)
            mqtt_port = match.group(5).decode(ENCODING)
            mqtt_user = match.group(6).decode(ENCODING)
            mqtt_password = match.group(7).decode(ENCODING)

            if len(ssid) == 0:
                self.send_response(
                    """
                    <p>SSID must be providaded!</p>
                    <p>Go back and try again!</p>
                """,
                    400,
                )
            elif self.wifi_connect(ssid, password):
                self.send_response(
                    """
                    <p>Successfully connected to</p>
                    <h1>{0}</h1>
                    <p>IP address: {1}</p>
                """.format(
                        ssid, self.wlan_sta.ifconfig()[0]
                    )
                )
                settings = self.read_settings()
                settings["ssid"] = ssid
                settings["password"] = password
                settings["device_name"] = device_name
                settings["mqtt_host"] = mqtt_host
                settings["mqtt_port"] = mqtt_port
                settings["mqtt_user"] = mqtt_user
                settings["mqtt_password"] = mqtt_password
                self.write_settings(settings)
                time.sleep(5)
            else:
                self.send_response(
                    """
                    <p>Could not connect to</p>
                    <h1>{0}</h1>
                    <p>Go back and try again!</p>
                """.format(
                        ssid
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
                if self.debug:
                    print(error)
                appnd(b"%")
                appnd(item)

        return b"".join(res)
