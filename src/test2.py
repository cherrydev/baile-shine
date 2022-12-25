import machine, uasyncio, time, micropython
from neoI2S import NeoPixel 

machine.freq(240_000_000)


pin = machine.Pin(25, machine.Pin.OUT)
np = NeoPixel(1, pin, 182, rate=92_000)

# Blank the whole set
# np[:] = (0,0,0)
# Set the first 10 pixels to dark blue
# np[0:10] = (0,0,40)
# Set the second pixel to green
# np[1] = (128,0,0)
# Set the third pixel's red value to full brightness
# np[2,2] = 255
# Copy the 2nd pixel to the 5th
# np[4] = np[1]
# Copy the first 16 pixels to the last 16 pixels
# np[-16:] = np[:16]
# np.write()

@micropython.native
def shift_colors(cur_color):
    max = 20
    r = cur_color[0] + 3
    g = cur_color[1] + 5
    b = cur_color[2] + 7
    if r > max : r -= max
    if g > max : g -= max
    if b > max : b -= max
    return (r, g, b)

loop_count = 0

# @micropython.native
def fill(pattern):
    patlen = len(pattern)
    for i in range(np.n):
        np[i] = pattern[i % patlen]

@micropython.native
def rgb(red, green, blue):
    return (green, red, blue)

# @micropython.native
async def foo():
    frames = 0
    atten = 0.1
    pink_stream = ( rgb(51, 0, 51), rgb(102, 0, 102), rgb(153, 0, 153), rgb(204, 0, 204), rgb(255, 0, 255), rgb(255, 51, 255), rgb(255, 201, 255), rgb(255, 153, 255), rgb(255, 204, 255))
    pink_stream = tuple(map( lambda cols: (int(cols[0] * atten), int(cols[1] * atten), int(cols[2] * atten)), pink_stream))
    color = ((80, 40, 40), (40, 80, 40), (40, 40, 80))
    fill(pink_stream)
    last_write = None
    rotate = 1
    while True:
        start = time.ticks_us()
        if last_write: await last_write
        wait_for_write = time.ticks_diff(time.ticks_us(), start)
        start = time.ticks_us()
        np.rotate(rotate)
        if frames % 10 == 0:
            rotate = rotate * -1
        # for i in range(np.n):
        #     color = shift_colors(color)
        #     np[i] = color
        
        last_write = uasyncio.create_task(np.write_nonblock())
        uasyncio.sleep_ms(1)
        if frames % 100 == 0:
            elapsed = time.ticks_diff(time.ticks_us(), start)
            print(elapsed, "us", "wait_for_write", wait_for_write)
        frames += 1
        # color = shift_colors(color)
        # np[0:7] = color
        # np.write()
        await uasyncio.sleep_ms(1)

# np[:] = rgb(0,0,0)
# np.write()
# np[:] = ( (1,1,1) )
np[:] = ( rgb(1,2,3) )


uasyncio.run(np.write_async())
# np._i2s.deinit()

# np.write()

# loop = uasyncio.new_event_loop()
# loop.create_task(foo())
# gc.collect()
# micropython.mem_info()
# loop.run_forever()