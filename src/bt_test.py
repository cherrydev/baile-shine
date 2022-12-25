from bt import LampBluetooth
from machine import Pin
import uasyncio

l = LampBluetooth("Gramp", "#884422", "#224488")
led = Pin(5, Pin.OUT)
l.bt_scan(True)
l.bt_adv(True)


e = uasyncio.Event()

async def blink():
    print("Blinking!")
    while True:
        led.value(not led.value())
        await e.wait()


async def pulse():
    while True:
        e.set()
        e.clear()
        await uasyncio.sleep_ms(1000)

loop = uasyncio.get_event_loop()

loop.create_task(pulse())
loop.create_task(blink())
# loop.run_forever()