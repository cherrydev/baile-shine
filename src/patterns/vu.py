from .led_strip import LedStrip
from machine import Pin
from touch_tempo import TouchTempo
from hsv import norm_hsv
import uasyncio

class VU:
    def __init__(self, strip: LedStrip, tempo: TouchTempo):
        self.strip = strip
        self.tempo = tempo
        self.fg_hsv = norm_hsv((298, 60, 5))
        self.bg_hsv = norm_hsv((119, 0, 5))
        self._e = uasyncio.ThreadSafeFlag()
        self._t: uasyncio.Task = None
        self._frame = 0
        self._beat_frames = 25
        self._gravity = 2.0
        self._beat_led = Pin(5, Pin.OUT)
        self._beat_led.off()
        print("Init VU", self.fg_hsv)
        self.reset()

    def stop(self):
        if self._t is not None:
            # print("Cancelled previous task")
            self._t.cancel()
            self._t = None

    def reset(self):
        self.stop()
        if (self.tempo.bpm < 1):
            print("Not starting until bpm set")
            return
        self._frame = 0
        self._beat_frames = int( (60 / self.tempo.bpm) * 50)
        # print("set frames per beat to ", self._beat_frames)
        self._t = uasyncio.create_task(self.go())

    def update(self):
        if (self.tempo.bpm_changed):
            self.reset()
        self._e.set()
        self._frame += 1
        

    def frame_in_beat(self):
        return self._frame % self._beat_frames

    def draw_bg(self):
        self.strip.fill_hsv_all(self.bg_hsv)

    async def frame_test(self):
        while True:
            for i in range(0, self._beat_frames):
                beat_proportion = self.frame_in_beat() / self._beat_frames
                V = int(beat_proportion * 255)
                self.strip.fill_hsv_all((self.fg_hsv[0], self.fg_hsv[1], V))
                await self.next_frame()

    async def go(self):
        while True:
            height = float(self.strip.led_count)
            rising_frames = self._beat_frames // 6
            for i in range(0, rising_frames):
                leds_lit = int(self.strip.led_count * i / rising_frames)
                height = float(max(height, leds_lit))
                self.strip.fill_hsv(self.fg_hsv, 0, int(height))
                await self.next_frame()
            falling_frames = self._beat_frames - self.frame_in_beat()
            height = float(self.strip.led_count)
            speed = 0.0
            for i in range(0, falling_frames):
                speed += self._gravity
                height = max(0, height - speed)
                # leds_lit = self.strip.led_count - int(self.strip.led_count * i / falling_frames)
                self.strip.fill_hsv(self.fg_hsv, 0, int(height))
                await self.next_frame()

    async def next_frame(self):
        await self._e.wait()
        self.shift_colors()
        self.draw_bg()
        if self.frame_in_beat() == 0:
            self._beat_led.on()
        else:
            self._beat_led.off()
        # print("frame in beat ", self.frame_in_beat())

    def shift_colors(self):
        if self._frame % 3 != 0: return
        bg_h = self.bg_hsv[0] + 1
        if bg_h > 255: bg_h = bg_h - 255
        self.bg_hsv = (bg_h, self.bg_hsv[1], self.bg_hsv[2])
        fg_h = self.fg_hsv[0] + 1
        if fg_h > 255: fg_h = fg_h - 255
        self.fg_hsv = (fg_h, self.fg_hsv[1], self.fg_hsv[2])
        