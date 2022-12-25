from ws2812 import WS2812
from ws2812_data import get_240_colors
import time, micropython, uctypes, gc

@micropython.native
def foo():
    ring = WS2812(spi_bus=2, led_count=7)
    # gc.collect()
    # micropython.mem_info()
    t = time.ticks_us()
    # data = [
    #     (24, 0, 0),
    #     (0, 24, 0),
    #     (0, 0, 24),
    #     (12, 12, 0),
    #     (0, 12, 12),
    #     (12, 0, 12),
    #     (24, 0, 0),
    #     (21, 3, 0),
    #     (18, 6, 0),
    #     (15, 9, 0),
    #     (12, 12, 0),
    #     (9, 15, 0),
    #     (6, 18, 0),
    #     (3, 21, 0),
    #     (0, 24, 0),
    #     (8, 8, 8),
    # ]
    data = get_240_colors()
    ring.update_buf(data[:7], 0)
    ring.send_buf()
    delta = time.ticks_diff(time.ticks_us(), t)
    # print('Function {} Time = {:6.3f}ms'.format("Foo", delta/1000))

while True:
    foo()
