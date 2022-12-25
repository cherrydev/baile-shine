from hsv import hsv_rgb, hsv_rgb_tup
import micropython

class LedStrip:
    def __init__(
        self,
        hsv_buff: bytearray, # buffer of hsv values, 3 bytes for each led
        buff_start_idx: int, # start index of strip within buffer
        led_count: int # number of LEDs in strip
        ):
        self.hsv_buff = hsv_buff
        self.buff_start_idx = buff_start_idx
        self.led_count = led_count

    @micropython.viper
    def set(self, idx: int, H: int, S: int, V: int):
        buff_bytes = ptr8(self.hsv_buff)
        buff_bytes[idx * 3] = H
        buff_bytes[idx * 3 + 1] = S
        buff_bytes[idx * 3 + 2] = V

    def fill_hsv_all(self, hsv_col):
        start = int(self.buff_start_idx)
        count = int(self.led_count)
        self.fill_hsv(hsv_col, start, count)

    @micropython.viper
    def fill_hsv(self, hsv_col, start: int, count: int):
        buff_bytes = ptr8(self.hsv_buff)
        buf_len = int(len(self.hsv_buff))
        if start + count > buf_len:
            raise Exception("oops")
        H = int(hsv_col[0])
        S = int(hsv_col[1])
        V = int(hsv_col[2])
        for i in range(start, start + count):
            buff_bytes[i * 3] = H
            buff_bytes[i * 3 + 1] = S
            buff_bytes[i * 3 + 2] = V