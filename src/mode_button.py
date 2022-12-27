from machine import Pin, TouchPad
import time

class ModeButton:
    def __init__(self, *signals: Pin):
        self.signals = signals
        self.last_state = False # False == no touch, True == touch
        self.last_ontouch = 0 # last tick when touch started
        self.measure_timeout = 1250 # How long to re-set deltas
        self.touches_counted = 0

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
        for signal in self.signals:
            if signal.value() == 1:
                # print("Pin pressed")
                return True
        return False
        # return any(pin.value() == 1 for pin in self.pins)

    def on_touch(self):
        return True

        

    def on_notouch(self):
        pass
    