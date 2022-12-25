from machine import Pin, TouchPad
import time

class ModeTouch:
    def __init__(self, pin: Pin):
        self.touch_pad = TouchPad(pin)
        self.last_state = False # False == no touch, True == touch
        self.last_ontouch = 0 # last tick when touch started
        self.measure_timeout = 1250 # How long to re-set deltas
        self.touches_counted = 0
        self.touch_threshold = int(self.touch_pad.read() * 0.75)
        print("Touch mode startup ", self.touch_pad.read())
        self.touch_threshold = 200
        # print("Touch touch threshold ", self.touch_threshold)


    def update(self) -> bool:
        now_touch = self.is_touch()
        # if now_touch: print("mode touched: ", now_touch)
        mode_triggered = False
        if (not (self.last_state)) and now_touch:
            mode_triggered = self.on_touch()
            self.last_state = True
            

        if self.last_state and (not now_touch):
            self.on_notouch()
            self.last_state = False
        
        if mode_triggered:
            print("Mode change triggered")
            self.touches_counted = 0
        return mode_triggered

    def is_touch(self):
        return self.touch_pad.read() < self.touch_threshold

    def on_touch(self):
        now = time.ticks_ms()
        if self.last_ontouch > 0:
            delta = time.ticks_diff(now, self.last_ontouch)
            ## check timeout
            if delta > self.measure_timeout:
                print("Mode timed out, starting over")
                self.touches_counted = 0
            else:
                self.touches_counted += 1

        self.last_ontouch = now
        return self.touches_counted == 2

        

    def on_notouch(self):
        pass
    