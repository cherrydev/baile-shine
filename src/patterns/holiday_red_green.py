from .led_strip import LedStrip
from machine import Pin
from touch_tempo import TouchTempo
from hsv import norm_hsv
import uasyncio

class HolidayRedGreen:
    def __init__(self, strip: LedStrip, tempo: TouchTempo):
        self.strip = strip
        self.tempo = tempo
        self.fg_hsv = norm_hsv((298, 60, 5))
        self.max_bright = 30
        self.red = norm_hsv((0, 100, 30))
        self.green = norm_hsv((120, 100, 30))
        self._e = uasyncio.ThreadSafeFlag()
        self._t: uasyncio.Task = None
        self._frame = 0
        self._beat_frames = 25
        self._beat_led = Pin(5, Pin.OUT)
        self._beat_led.off()
        self.is_green = False
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

    def set_brightness(self, brightness):
        self.fg_hsv = (self.fg_hsv[0], self.fg_hsv[1], brightness)
        self.strip.fill_hsv(self.fg_hsv, 0, self.strip.led_count)

    async def go(self):
        while True:
            self.fg_hsv = self.green if self.is_green else self.red
            rising_frames = self._beat_frames // 6

            for i in range(0, rising_frames):
                self.set_brightness(int(self.max_bright * (i / rising_frames)))
                await self.next_frame()

            falling_frames = self._beat_frames - self.frame_in_beat()
            for i in range(0, falling_frames):
                brightness = self.max_bright - int(self.max_bright * (i / falling_frames))
                self.set_brightness(brightness)
                await self.next_frame()
            self.is_green = not self.is_green

    async def next_frame(self):
        await self._e.wait()
        if self.frame_in_beat() == 0:
            self._beat_led.on()
        else:
            self._beat_led.off()
        # print("frame in beat ", self.frame_in_beat())

    def shift_colors(self):
        if self._frame % 3 != 0: return
        fg_h = self.fg_hsv[0] + 1
        if fg_h > 255: fg_h = fg_h - 255
        self.fg_hsv = (fg_h, self.fg_hsv[1], self.fg_hsv[2])
        