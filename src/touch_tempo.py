import time, micropython
from machine import Pin, TouchPad, Timer




class TouchTempo:
    def __init__(self, pin: Pin):
        self.last_state = False # False == no touch, True == touch
        self.last_ontouch = 0 # last tick when touch started
        self.measure_timeout = 1500 # How long to re-set deltas
        self.min_deltas = 4 # How many counts before giving a bpm
        self.bpm = 0.0
        self.last_deltas = list()
        self.bpm_changed = False # Did bpm change this update
        self.beats_counted = 0 # Can help find the downbeat

        self.touchpin = pin
        self.touch_pad = TouchPad(self.touchpin)
        print("Touch tempo startup ", self.touch_pad.read())
        # self.touch_threshold = int(self.touch_pad.read() * 0.50)
        self.touch_threshold = 200

        print("Touch tempo threshold ", self.touch_threshold)


    def on_update(self):
        self.bpm_changed = False
        now_touch = self.is_touch()
        if (not (self.last_state)) and now_touch:
            self.on_touch()
            self.last_state = True
            

        if self.last_state and (not now_touch):
            self.on_notouch()
            self.last_state = False


    def is_touch(self):
        return self.touch_pad.read() < self.touch_threshold

    def on_notouch(self):
        # print("OnNoTouch!")
        pass

    def on_touch(self):
        now = time.ticks_ms()
        if self.last_ontouch > 0:
            delta = time.ticks_diff(now, self.last_ontouch)
            ## check timeout
            if delta > self.measure_timeout:
                print("Timed out, starting over")
                self.last_deltas.clear()
                self.beats_counted = 1
            else:
                self.last_deltas.append(delta)
                self.beats_counted += 1

        if len(self.last_deltas) >= self.min_deltas:
            self.set_bpm(len(self.last_deltas) / (sum(self.last_deltas) / 60000))

        self.last_ontouch = now

    def set_bpm(self, bpm: float):
        self.bpm = bpm
        self.bpm_changed = True

if __name__ == "__main__":
    touchTempo = TouchTempo(Pin(15, Pin.IN))

    def update(_):
        touchTempo.on_update()
        if touchTempo.bpm_changed:
            print("bpm now ", touchTempo.bpm)

    def isr(_: Timer):
        micropython.schedule(update, None)


    timer = Timer(-1)
    timer.init(period = 1000 // 50, callback=isr)