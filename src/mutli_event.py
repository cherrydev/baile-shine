import uasyncio



class MultiEvent:
    def __init__(self):
        self._last_arg = None
        self._e = uasyncio.Event()
        self._delegate_events = []

    def add_delegate(self, delegate_event : uasyncio.Event, event_arg):
        self._delegate_events.append( (delegate_event, event_arg) )
        uasyncio.get_event_loop().create_task(self._set_e(delegate_event, event_arg))

    async def _set_e(self, delegate, event_arg):
        await delegate.wait()
        self._last_arg = event_arg
        self._e.set()
        self._e.clear()

    async def wait(self):
        await self._e.wait()
        return self._last_arg

def demo():
    loop = uasyncio.get_event_loop()
    loop.create_task(main())
    loop.create_task(other_task())
    loop.run_forever()

e1 = uasyncio.Event()
e2 = uasyncio.Event()

async def other_task():
    await uasyncio.sleep_ms(2000)
    e1.set()

async def main():
    print("Hello")
    me = MultiEvent()
    me.add_delegate(e1, "e1")
    me.add_delegate(e2, "e2")
    print("about to wait")
    result = await me.wait()
    print("Result was", result)