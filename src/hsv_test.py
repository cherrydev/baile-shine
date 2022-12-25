import time, micropython, random
from myneopixel import NeoPixel
from machine import Pin, freq
import hsv

freq(240_000_000)
np_pin = Pin(25, Pin.OUT)
np = NeoPixel(np_pin, 181, 3)

@micropython.viper
def make_rainbow(hsv_bytes_obj, sat: int, val: int):
    n_pix = int(len(hsv_bytes_obj)) // 3
    hsv_vals = ptr8(hsv_bytes_obj)
    for i in range(0, n_pix):
        hsv_vals[i * 3] = 255000 // n_pix * (i + 1) // 1000
        hsv_vals[i * 3 + 1] = sat
        hsv_vals[i * 3 + 2] = val

@micropython.viper
def set_all_sat(hsv_bytes_obj, sat: int):
    n_pix = int(len(hsv_bytes_obj)) // 3
    hsv_vals = ptr8(hsv_bytes_obj)
    for i in range(0, n_pix):
        hsv_vals[i * 3 + 1] = sat

@micropython.viper
def rotate(arr_obj, shift: int):
    arr = ptr8(arr_obj)
    len_arr = int(len(arr_obj))
    pivot = shift % len_arr
    dst = 0
    src = pivot
    while (dst != src):
        arr[dst], arr[src] = arr[src], arr[dst]
        dst += 1
        src += 1
        if src == len_arr:
            src = pivot
        elif dst == pivot:
            pivot = src


n_pixels = 181
hsv_vals = bytearray(n_pixels * 3)

rgb_vals = bytearray(len(hsv_vals))


# for i in range(0, n_pixels):
#     hsv_vals[i * 3] = 255000 // n_pixels * (i + 1) // 1000
#     hsv_vals[i * 3 + 1] = 255
#     hsv_vals[i * 3 + 2] = 50
start = time.ticks_ms()
for i in range(0,100): make_rainbow(hsv_vals, 200, 30)
# make_rainbow(hsv_vals, 200, 30)
print("Rainbow in ", time.ticks_ms() - start)
start = time.ticks_ms()
i = 0
spark_likelyhood = (5, 40)
spark_duration = (2, 6)
spark_countdown = 0
sleep_time = 15
while(True):
    rotate(hsv_vals, 3)
    hsv.hsv_rgb(hsv_vals, rgb_vals, 0, 0)
    if (spark_countdown > 0):
        set_all_sat(hsv_vals, 0)
        spark_countdown -= 1
    else:
        set_all_sat(hsv_vals, 200)

    if random.randint(0, spark_likelyhood[1]) == 0:
        spark_countdown = random.randint(spark_duration[0], spark_duration[1])

    np.buf = rgb_vals
    np.write()
    i += 1
    # if (i == n_pixels): i = 0
    if (i % 50 == 0): print("Avg frame:", (time.ticks_ms() - start) / i - sleep_time)
    time.sleep_ms(sleep_time)

print("Elapsed:" + str((time.ticks_ms() - start)) + " ms")

# for i in range(0, len(hsv_vals)//3):
#     print(int(hsv_vals[i * 3]), int(hsv_vals[i * 3 + 1]), int(hsv_vals[i * 3 + 2]))

