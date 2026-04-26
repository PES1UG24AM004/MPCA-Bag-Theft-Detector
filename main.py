from machine import Pin, I2C
import mpu6050
import time
import network
import socket

# WIFI
SSID = "Hello"
PASSWORD = "987654321"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    time.sleep(1)

ip = wifi.ifconfig()[0]
print(ip)

# SERVER
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(1)
server.settimeout(0.2)

# MPU
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
mpu = mpu6050.accel(i2c)

# LDR
ldr = Pin(26, Pin.IN)

# BUZZER
buzzer = Pin(25, Pin.OUT)
buzzer.value(1)

# SETTINGS
MOVEMENT_THRESHOLD = 4000
MOVEMENT_DELAY = 0.7
LIGHT_DELAY = 2.0

baseline = mpu.get_values()

movement_time = None
light_time = None

status = "DISARMED"
armed = False

alert_until = 0
alert_active = False

# ALARM
def alarm(msg):
    global status, alert_until, alert_active
    status = msg
    alert_until = time.time() + 4
    alert_active = True

    for _ in range(3):
        buzzer.value(0)
        time.sleep(0.2)
        buzzer.value(1)
        time.sleep(0.2)

# MAIN LOOP
while True:
    try:
        curr = mpu.get_values()

        diff = abs(curr['AcX'] - baseline['AcX']) + \
               abs(curr['AcY'] - baseline['AcY']) + \
               abs(curr['AcZ'] - baseline['AcZ'])

        movement = diff > MOVEMENT_THRESHOLD
        dark = (ldr.value() == 1)

        now = time.time()

        if armed:
            if movement:
                if movement_time is None:
                    movement_time = now
                elif now - movement_time > MOVEMENT_DELAY:
                    alarm("MOVEMENT DETECTED")
                    movement_time = None
            else:
                movement_time = None

            if dark:
                if light_time is None:
                    light_time = now
                elif now - light_time > LIGHT_DELAY:
                    alarm("DARK DETECTED")
                    light_time = None
            else:
                light_time = None

            if now > alert_until:
                alert_active = False
                if not movement and not dark:
                    status = "ARMED (SAFE)"

        try:
            conn, addr = server.accept()
            request = conn.recv(1024).decode()

            if "GET /arm" in request:
                armed = True
                baseline = mpu.get_values()
                status = "ARMED"

            elif "GET /disarm" in request:
                armed = False
                status = "DISARMED"
                alert_active = False
                buzzer.value(1)

            if alert_active:
                color = "red"
            elif "SAFE" in status:
                color = "green"
            else:
                color = "gray"

            alert_banner = ""
            if alert_active:
                alert_banner = """
                <div style="background:red; padding:20px; border-radius:10px;">
                <h1>THEFT DETECTED</h1>
                </div>
                """

            response = f"""
            <html>
            <head>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="2">
            </head>
            <body style="font-family:Arial; text-align:center; background:#111; color:white;">

            <h1>Bag Theft Detector</h1>

            {alert_banner}

            <div style="padding:20px; margin:20px; border-radius:10px; background:{color};">
                <h2>{status}</h2>
            </div>

            <p>Movement: {diff}</p>
            <p>Light State: {'DARK' if dark else 'LIGHT'}</p>

            <br>

            <a href="/arm">
            <button style="font-size:20px; padding:15px; background:green; color:white;">
            ARM
            </button>
            </a>

            <br><br>

            <a href="/disarm">
            <button style="font-size:20px; padding:15px; background:red; color:white;">
            DISARM
            </button>
            </a>

            </body>
            </html>
            """

            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n")
            conn.send(response)
            conn.close()

        except:
            pass

        time.sleep(0.05)

    except Exception as e:
        print(e)