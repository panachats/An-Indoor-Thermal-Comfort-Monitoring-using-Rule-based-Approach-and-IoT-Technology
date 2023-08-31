from machine import Pin, SoftI2C, PWM
import ssd1306
from time import sleep
import dht
import machine
import network
import urequests

# Define pins for RGB LED
red_pin = Pin(15, Pin.OUT)
green_pin = Pin(2, Pin.OUT)
blue_pin = Pin(4, Pin.OUT)

# Define PWM objects for each pin
red_pwm = PWM(red_pin)
green_pwm = PWM(green_pin)
blue_pwm = PWM(blue_pin)


# ESP32 Pin assignment
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

# DHT22 Pin
sensorDHT = dht.DHT22(machine.Pin(3))

# Motion detector Pin
ldr = Pin(14, Pin.IN)

# ThingSpeak Settings
api_key = "2RYH4FZ0JU2R5NWZ" # ThingSpeak API key

sleep(2)
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Set time
rtc = machine.RTC()
rtc.datetime((2023, 2, 20, 1, 15, 53, 0, 0))

def set_color(red, green, blue):
    # Set duty cycle of each PWM object
    red_pwm.duty(int(red / 255 * 1023))
    green_pwm.duty(int(green / 255 * 1023))
    blue_pwm.duty(int(blue / 255 * 1023))


# Function to set the color of the RGB LED
# def set_color(red, green, blue):
#     # Set duty cycle of each PWM object
#     red_pwm.duty(int(red / 255 * 1023))
#     green_pwm.duty(int(green / 255 * 1023))
#     blue_pwm.duty(int(blue / 255 * 1023))


sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Aztaroz')
while not sta_if.isconnected(): #ถ้าเซนเซอร์ไม่มีการตรวจจับ
    set_color(255, 0, 0)
    sleep(0.3)
    set_color(0, 255, 0)
    sleep(0.3)
print('network config:', sta_if.ifconfig())

# Main loop
while True:
    # Get current time
    t = rtc.datetime()
    now = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6])

    try:

        # Read temperature and humidity
        sensorDHT.measure()
        temp = sensorDHT.temperature()
        hum = sensorDHT.humidity()
        print("ldr value = ", ldr.value())


        set_color(0, 0, 255)

        if rtc.datetime()[6] % 30 == 0:  # เช็คว่าเวลาปัจจุบันหาร 30 ลงตัวหรือไม่ ถ้าลงตัวแสดงว่าผ่านไปเวลา 30 วินาที
            response = urequests.get(
                f'https://api.thingspeak.com/update?api_key={api_key}&field1={temp}&field2={hum}&field3={ldr.value()}')
            response.close()

        # If motion detected, display time, temperature and humidity
        if ldr.value() == 1:
            print('OBJECT DETECTED')
            oled.fill(0)
            oled.text(string="Time: " + now, x=2, y=2)
            oled.text('-' * oled_width, 2, 10)
            oled.text("Temp: " + str(temp) + " C", 2, 30, 1)
            oled.text("Humid: " + str(hum) + " %", 2, 40, 1)
            oled.text('ip: ' + sta_if.ifconfig()[0], 2, 50, 1)
            oled.show()
        else:
            # If no motion detected, display nothing
            print('no object detected')
            oled.fill(0)
            # it is important to call show() to make the changes visible
            oled.show()

    except OSError as e:
        print('Failed to read sensor.')
        sleep(0)




