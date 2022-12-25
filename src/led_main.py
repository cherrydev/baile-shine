from hsv import hsv_rgb, norm_hsv
import micropython
import gc
from machine import Pin, Timer
from button_tempo import ButtonTempo
from patterns.led_strip import LedStrip
from myneopixel import NeoPixel
from patterns.vu import VU
from patterns.pulse import Pulse
from patterns.sparkle_rainbow import SparkleRainbow
from patterns.xmas_tree_lights import XmasTreeLights
from mode_button import ModeButton
import uasyncio

touch_pin = Pin(15, Pin.IN, Pin.PULL_UP)
ttempo = ButtonTempo(touch_pin)
timer = Timer(-1)
num_leds = 144
# num_leds = 54
pattern_size = num_leds // 2
hsv_bytes = bytearray(pattern_size * 3)
strip = LedStrip(hsv_buff=hsv_bytes, buff_start_idx=0, led_count=pattern_size)
np = NeoPixel(Pin(25), num_leds)

mode_touch = ModeButton(Pin(4, Pin.IN, Pin.PULL_UP))

def print_triplets(buf):
    for i in range(0, len(buf), 3):
        print((buf[i], buf[i+1], buf[i+2]))

def update(_):
    ttempo.on_update()
    if mode_touch.update(): change_mode()
    pattern.update()
    # print_triplets(strip.hsv_buff)
    hsv_rgb(strip.hsv_buff, np.buf, 0, 0, True)
    hsv_rgb(strip.hsv_buff, np.buf, 0, pattern_size * 3, False)
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

pattern = None

def mode_sparkle():
    print("Mode Sparkle")
    global pattern
    pattern = SparkleRainbow(strip)
    pattern.saturation = 255
    pattern.spark_duration = (1,3)

def mode_vu():
    print("Mode VU")
    global pattern
    pattern = VU(strip, ttempo)
    pattern.fg_hsv = norm_hsv((298, 60, 10))
    pattern.bg_hsv = norm_hsv((119, 41, 2))
    pattern._gravity = 0.2

def mode_pulse():
    print("Mode Pulse")
    global pattern
    pattern = Pulse(strip, ttempo)
    pattern.fg_hsv = norm_hsv((298, 60, 10))


def change_mode():
    global pattern, mode
    mode += 1
    if mode > 2: mode = 0
    if pattern != None: pattern.stop()
    if mode == 0: mode_sparkle()
    if mode == 1: mode_vu()
    if mode == 2: mode_pulse()

mode = -1
change_mode()
timer.init(period = period, callback=isr)

loop.create_task(main())
loop.run_forever()
