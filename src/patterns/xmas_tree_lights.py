import hsv
import random
from .led_strip import LedStrip
from hsv import norm_hsv

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

class XmasTreeLights:
    def __init__(self, strip: LedStrip):
        self.strip = strip
        self._i = 0
        self.spark_likelyhood = (5, 40)
        self.spark_duration = (2, 6)
        self.brightness = 30
        self.saturation = 255
        self.rot_period = 8
        self.light_span = 3
        self.colors = []
        self._spark_countdown = 0
        self.reset()

    def make_lights(self):
        strip = self.strip
        span = self.light_span
        for i in range(0, self.strip.led_count, span):
            color_idx = i // span % len(self.colors)
            for j in range(0, span):
                color = self.colors[color_idx]
                strip.set(i + j, color[0], color[1], color[2])

    def reset(self):
        self.colors = [
            norm_hsv((120, self.saturation, self.brightness)), # green
            norm_hsv((0, self.saturation, self.brightness)), # red
            norm_hsv((240, self.saturation, self.brightness)), # blue
            norm_hsv((60, self.saturation, self.brightness)), # yellow
            norm_hsv((300, self.saturation, self.brightness)), # magenta
        ]
        self.make_lights()

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