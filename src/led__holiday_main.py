from hsv import hsv_rgb, norm_hsv
import micropython
import gc
from machine import Pin, Timer, Signal, I2C
from mpu6050.imu import MPU6050
from button_tempo import ButtonTempo
from patterns.led_strip import LedStrip
from myneopixel import NeoPixel
from patterns.sparkle_rainbow import SparkleRainbow
from patterns.holiday_red_green import HolidayRedGreen
from patterns.xmas_tree_lights import XmasTreeLights
from patterns.vu import VU
from patterns.pulse import Pulse
from mode_button import ModeButton
import uasyncio

touch_pin = Pin(15, Pin.IN, Pin.PULL_UP)
ttempo = ButtonTempo(touch_pin)
timer = Timer(-1)
num_leds = 144
pattern_size = num_leds // 2
hsv_bytes_right = bytearray(pattern_size * 3)
strip_right = LedStrip(hsv_buff=hsv_bytes_right, buff_start_idx=0, led_count=pattern_size)
hsv_bytes_left = bytearray(pattern_size * 3)
strip_left = LedStrip(hsv_buff=hsv_bytes_left, buff_start_idx=0, led_count=pattern_size)
np = NeoPixel(Pin(25), num_leds)

# mode_touch = ModeButton(Pin(4, Pin.IN, Pin.PULL_UP))
mode_touch = ModeButton(
    Signal(Pin(0, Pin.IN, Pin.PULL_UP), invert=True),
    Signal(Pin(4, Pin.IN, Pin.PULL_UP), invert=True)
    )

def print_triplets(buf):
    for i in range(0, len(buf), 3):
        print((buf[i], buf[i+1], buf[i+2]))

def update(_):
    ttempo.on_update()
    if mode_touch.update(): change_mode()
    # if pattern: pattern.update()
    if pattern_left: pattern_left.update()
    if pattern_right: pattern_right.update()
    # print_triplets(strip.hsv_buff)
    hsv_rgb(strip_right.hsv_buff, np.buf, 0, 0, True)
    hsv_rgb(strip_left.hsv_buff, np.buf, 0, pattern_size * 3, False)
    # hsv_rgb(strip.hsv_buff, np.buf, 0, 0, False)
    # hsv_rgb(strip.hsv_buff, np.buf, 0, pattern_size * 3, True)
    np.write()
    if (ttempo.bpm_changed): print("bpm:", ttempo.bpm)

loop = uasyncio.get_event_loop()
flag = uasyncio.ThreadSafeFlag()



async def main():
    while True:
        update(None)
        gc.collect()
        await flag.wait()

def isr(_):
    flag.set()

period = 1000 // 50
# period = 150

ttempo.set_bpm(128.0)
mode = 0

pattern_right = None
pattern_left = None

def mode_sparkle():
    print("Mode Sparkle")
    global pattern_right, pattern_left
    pattern_left = SparkleRainbow(strip_left)
    pattern_left.saturation = 255
    pattern_left.brightness = 30
    pattern_left.spark_duration = (1,3)
    pattern_right = SparkleRainbow(strip_right)
    pattern_right.saturation = 255
    pattern_right.brightness = 30
    pattern_right.spark_duration = (1,3)

def mode_xmas_tree_lights():
    print("Mode Xmas Tree Lights")
    global pattern_right, pattern_left
    pattern_left = XmasTreeLights(strip_left)
    pattern_left.saturation = 255
    pattern_left.brightness = 20
    pattern_left.spark_duration = (1,3)
    pattern_right = XmasTreeLights(strip_right)
    pattern_right.saturation = 255
    pattern_right.brightness = 20
    pattern_right.spark_duration = (1,3)


def mode_holiday_red_green():
    print("Mode Holiday Red Green")
    global pattern_right, pattern_left
    pattern_right = HolidayRedGreen(strip_right, ttempo)
    pattern_right.is_green = True
    pattern_left = HolidayRedGreen(strip_left, ttempo)

def mode_vu():
    print("Mode VU")
    global pattern_right, pattern_left
    pattern_right = VU(strip_right, ttempo)
    pattern_right.fg_hsv = norm_hsv((298, 60, 10))
    pattern_right.bg_hsv = norm_hsv((119, 41, 2))
    pattern_right._gravity = 0.2
    pattern_left = VU(strip_left, ttempo)
    pattern_left.fg_hsv = norm_hsv((298, 60, 10))
    pattern_left.bg_hsv = norm_hsv((119, 41, 2))
    pattern_left._gravity = 0.2

def mode_pulse():
    print("Mode Pulse")
    global pattern_right, pattern_left
    pattern_right = Pulse(strip_right, ttempo)
    pattern_right.fg_hsv = norm_hsv((298, 60, 10))
    pattern_left = Pulse(strip_left, ttempo)
    pattern_left.fg_hsv = norm_hsv((298, 60, 10))

def change_mode():
    global pattern_left, pattern_right, mode
    mode += 1
    if mode > 3: mode = 0
    if pattern_right != None: pattern_right.stop()
    if pattern_left != None: pattern_left.stop()
    pattern_right = None
    pattern_left = None
    if mode == 0: mode_sparkle()
    if mode == 1: mode_vu()
    if mode == 2: mode_pulse()
    if mode == 3: mode_xmas_tree_lights()
        

change_mode()
timer.init(period = period, callback=isr)

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=800000)
imu = MPU6050(i2c)

isr_count = 0
from utime import ticks_ms
isr_tick = ticks_ms()
def accel_isr(_):
    global isr_count, isr_tick
    imu.accel_irq()
    isr_count += 1
    if isr_count % 1000 == 0:
        now = ticks_ms()
        # print("ISR:", isr_count, " elapsed:", now - isr_tick)
        isr_tick = now

timer_accel = Timer(0)
timer_accel.init(period = 1000 // 200, callback=accel_isr)

loop.create_task(main())
loop.run_forever()
