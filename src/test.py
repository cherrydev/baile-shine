from machine import Pin, Timer, TouchPad, freq, ADC
from myneopixel import NeoPixel
from moving_average import MovingAverage
import micropython, time, uasyncio, gc
import pytweening
# import bt_test

freq(240_000_000)
period = 1000
frame_ms = 1000 // 30

use_white = False

start = time.ticks_ms()
inOut = False
tween = pytweening.easeInOutQuint

touchpin = Pin(15, Pin.IN)
touch = TouchPad(touchpin)
touch_ma = MovingAverage(0.2)
touch.config(500)

button = Pin(0, Pin.IN)
np_pin = Pin(25, Pin.OUT)

@micropython.native
def rgb(red, green, blue):
    return (green, red, blue)

boards = {
    "strip190rgb" : {
        "pixels" : 181,
        "bpp" : 3
    },
    "ring7rgb" : {
        "pixels" : 7,
        "bpp" : 3
    },
    "ring16rgbw" : {
        "pixels" : 16,
        "bpp" : 4
    },
    "singlergb":{
        "pixels":1,
        "bpp": 3
    }
}
board = boards["strip190rgb"]
np = NeoPixel(np_pin, board["pixels"], board["bpp"])

black_pattern = ( (0, 0, 0), )
rainbow_pattern = (rgb(255, 0, 0), rgb(255, 201, 0), rgb(0, 255, 0), rgb(0, 0, 255), rgb(102, 0, 253), rgb(255, 51, 204), rgb(204, 0, 51))
pink_stream = ( rgb(51, 0, 51), rgb(102, 0, 102), rgb(153, 0, 153), rgb(204, 0, 204), rgb(255, 0, 255), rgb(255, 51, 255), rgb(255, 201, 255), rgb(255, 153, 255), rgb(255, 204, 255))
purple_stream = ( rgb(25, 0, 51), rgb(51, 0, 102), rgb(76, 0, 153), rgb(102, 0, 204), rgb(127, 0, 255), rgb(153, 51, 255), rgb(178, 102, 255), rgb(204, 153, 255), rgb(229, 204, 255) )
earth_tones = ( rgb(153, 150, 165), rgb(23, 127, 117), rgb(182, 33, 45), rgb(127, 23, 51), rgb(182, 119, 33), rgb(255, 192, 0) )
potentially_ugly = ( rgb(38, 55, 85), rgb(94, 90, 91), rgb(224, 208, 182), rgb(80, 80, 0), rgb(169, 151, 111), rgb(53, 57, 69))


@micropython.native
def convert_to_rgbw(rgb_val):
    white_val = min(rgb_val)
    adjusted_rgb = tuple(map(lambda v: v - white_val, rgb_val))
    # rgbw = adjusted_rgb + (white_val,)
    # print(rgb_val, rgbw)
    return adjusted_rgb + (white_val,)

@micropython.native
def convert_to_pixel_value(rgb_val, board):
    global use_white
    if (board["bpp"] == 4):
        # return convert_to_rgbw(rgb_val)
        return convert_to_rgbw(rgb_val) if use_white else rgb_val + (0,) 
    else:
        return rgb_val

@micropython.native
def clamp(low, high, val):
    return max(low, min(val, high))

def animate(t):
    global start, inOut, tween, np, board
    now = time.ticks_ms()
    passed_ticks = time.ticks_diff(now, start)
    is_elapsed = passed_ticks > period
    in_val = clamp(0, 1, passed_ticks / period)
    # in_val = max(0, min(passed_ticks / period, 1))
    frame_val = 1.0 - tween(in_val) if inOut else tween(in_val)
    if (is_elapsed):
        start = now
        inOut = not inOut
    np.fill(tuple(map( lambda v: int(frame_val * v), convert_to_pixel_value( (50, 200, 50), board ) )))
    np.write()
    # print(frame_val)

# for x in range(pixels):
#     np[x] = (150, (150 * x + 3) // pixels, 0)
    # np[x] = (50, 50, 50)
# np.fill( (50, 140, 12) )
# np.write()
# micropython.schedule(np.write)
# ani_timer = Timer(-1)
# ani_timer.init(period=frame_ms, mode=Timer.PERIODIC, callback=lambda t: micropython.schedule(animate, 0))
def change_mapping(x):
    global use_white
    use_white = not use_white
    print("using white:", use_white)
button.irq(change_mapping, Pin.IRQ_FALLING)

_touch_i = 0
allPixels = list( () )
for i in range(board["pixels"]):
    r = 200 if i % 2 == 0 else 0
    allPixels.append( (r,0,0, 100) )

# @micropython.native
# @micropython.viper
# @micropython.native

def pulsing_intensity():
    i = 0
    max = 50
    backwards = False
    while True:
        yield i
        i = i - 1 if backwards else i + 1
        if i == 0: backwards = False
        if i == max: backwards = True
intensity_gen = pulsing_intensity()

def readTouch(_) :
    global _touch_i, intensity_gen
    # print(touch.read())
    
    high = 1000
    low = 300
    touch_ma.add_value(clamp(0, 1, (high - touch.read() - low) / (high - low)))
    touch_val = int( touch_ma.average() * 255)
    start = time.ticks_us()
    # touch_val = int( (1000 - touch.read()) / 1000  * 255)
    # print(touch_val)
    
    # np.fill(tuple (map( lambda v: v * touch_val // 255, convert_to_pixel_value((100, 20, 20), board)  )))
    # np.fill(tuple (map( lambda v: int(touch_ma.average() * v), (100, 20, 20, 0)  )))
    # if _touch_i % 10 == 0: swirlvip()
    
    np.fill_pattern( pink_stream , next(intensity_gen) )
    # swirlvip()
    # np.fill_pattern(pink_stream, 50)
    # blitrainbow()

    elapsed = time.ticks_diff(time.ticks_us(), start)
    # np.fill( (153, 150, 165))
    np.write()
    elapsed2 = time.ticks_diff(time.ticks_us(), start) - elapsed
    if (_touch_i % (1000 // frame_ms) == 0): print("Fill", elapsed, "us", "Write", elapsed2, "us")
    _touch_i = _touch_i + 1

@micropython.native
def blitrainbow():
    pixels = board["pixels"]
    for i in range(pixels):
        color = ()
        for j in range(3):
            x = (i + j) % pixels * 255 // pixels
            color = color + (x,)
        np[i] = color + (0,)

_swirltmp = bytearray(board["bpp"])
# @micropython.native
def swirl():
    global _swirltmp
    pixels = board["pixels"]
    bpp = board["bpp"]
    bufptr = np.buf
    # _swirltmp = bytearray(bpp)
    for j in range(bpp):
        _swirltmp[j] = bufptr[j]
    for i in range(pixels - 1):
        for j in range(bpp):
            bufptr[i * bpp + j] = bufptr[(i + 1) * bpp + j]
    for j in range(bpp):
        bufptr[ (pixels - 1) * bpp + j] = _swirltmp[j]



@micropython.viper
def swirlvip():
    global _swirltmp
    pixels = int(board["pixels"])
    bpp = int(board["bpp"])
    bufptr = ptr8(np.buf)
    tmp = ptr8(_swirltmp)
    for j in range(bpp):
        tmp[j] = bufptr[j]
    for i in range(pixels - 1):
        for j in range(bpp):
            bufptr[i * bpp + j] = bufptr[(i + 1) * bpp + j]
    for j in range(bpp):
        bufptr[ (pixels - 1) * bpp + j] = tmp[j]



# @micropython.viper
# def blit(even, odd):
#     evenPtr = ptr8(bytes(even))
#     oddPtr = ptr8(bytes(odd))
#     fooptr = ptr8(np.buf)
#     i : int = 0
#     while (i < 200):
#         colors = evenPtr if i % 2 == 0 else oddPtr
#         for v in range(4):
#             offset = i * 4 + v
#             old = fooptr[offset]
#             fooptr[offset] = colors[v]
#         i += 1
    #     i += 1

    # for i in range(board["pixels"]):
    #     pixel = np.pixelstruct.pixels[i]
    #     pixel.r = 200 if i % 2 == 0 else 0
    #     pixel.g = 0
    #     pixel.b = 0
    #     pixel.g = 50

# blitrainbow()
np.fill_pattern( ( (100, 0, 0, 10), (0, 100, 0, 10), (0, 0, 100, 10) ), 50)

# touch_timer = Timer(-1)
# touch_timer.init(period=frame_ms, mode=Timer.PERIODIC, callback=lambda t: micropython.schedule(readTouch, 0))

# np.fill( (5, 10, 15) )
# np.fill((50, 50, 50))
# np.write()

async def main():
    while True:
        readTouch(None)
        await uasyncio.sleep_ms(frame_ms)

loop = uasyncio.get_event_loop()
loop.create_task(main())
gc.collect()
micropython.mem_info()
loop.run_forever()
