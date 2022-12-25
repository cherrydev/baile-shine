import hsv
import random
from .led_strip import LedStrip

@micropython.viper
def make_rainbow(strip, sat: int, val: int):
    n_pix = int(strip.led_count)
    start_idx = int(strip.buff_start_idx)
    hsv_vals = ptr8(strip.hsv_buff)
    for i in range(0, n_pix):
        base = i * 3 + start_idx
        hsv_vals[base] = 255000 // n_pix * (i + 1) // 1000
        hsv_vals[base + 1] = sat
        hsv_vals[base + 2] = val

@micropython.viper
def set_all_sat(strip, sat: int):
    n_pix = int(strip.led_count)
    start_idx = int(strip.buff_start_idx)
    hsv_vals = ptr8(strip.hsv_buff)
    for i in range(0, n_pix):
        base = i * 3 + start_idx
        hsv_vals[base + 1] = sat

@micropython.viper
def rotate(strip, shift: int):
    arr = ptr8(strip.hsv_buff)
    len_arr = int(strip.led_count) * 3
    idx_start = int(strip.buff_start_idx)
    pivot = shift % len_arr
    dst = 0
    src = pivot
    while (dst != src):
        arr[dst + idx_start], arr[src + idx_start] = arr[src + idx_start], arr[dst + idx_start]
        dst += 1
        src += 1
        if src == len_arr:
            src = pivot
        elif dst == pivot:
            pivot = src

class SparkleRainbow:
    def __init__(self, strip: LedStrip):
        self.strip = strip
        self._i = 0
        self.spark_likelyhood = (5, 40)
        self.spark_duration = (2, 6)
        self.brightness = 30
        self.saturation = 200
        self.rot_period = 2
        self._spark_countdown = 0
        self.reset()

    def reset(self):
        make_rainbow(self.strip, self.saturation, self.brightness)

    def stop(self):
        pass

    def update(self):
        if self._i % self.rot_period == 0:
            rotate(self.strip, 3)

        if (self._spark_countdown > 0):
            set_all_sat(self.strip, 0)
            self._spark_countdown -= 1
        else:
            set_all_sat(self.strip, self.saturation)
            pass

        if random.randint(0, self.spark_likelyhood[1]) == 0:
            self._spark_countdown = random.randint(self.spark_duration[0], self.spark_duration[1])
        self._i += 1