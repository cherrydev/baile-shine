# Notes
So, we're going to have _gestures_ and _expressions_
Expressions would be long-term behaviours that might be described 'delaratively', like 

    "it adjusts its brightness down from a maxiumum according to how many nearby lamps there are".
or

    "it’s base color is a stacked rainbow of the colors of nearby base colors instead of a solid color"

This is opposed to festures, which are a short-term, momentary behaviour that might normally be described 'procedurally':

    "Every once in a while it flighers randomly for a half-second or so."

    "It would blush in response to the arrival of a nearby lamp it likes."

What about an API where both expressions and gestures were implemented as asynchronous functions to allow them to be readily readable:

```python
async def my_shy_expression(self):
    nearby_lamp_tolerance = 2
    min_brightness_nearby = 5
    while True:
        await self.until_nearby_change()
        nearby_count = len(self.nearby)
        if nearby_count > nearby_lamp_tolerance:
            brightness = self.tween_value(min = 2, max = 5, cur = nearby_count)
            new_color = self.base_color.scale_brightness(brightness)
            await self.untilTweenCompleted(new_color)
        else:
            await self.untilTweenCompleted(self.base_color)
```

```python

async def tween_in_and_out(in_col, in_l, out_col out_l):
    await self.untilTweenCompleted(in_col, in_l, tween.out_cubic)
    await self.untilTweenCompleted(out_col, out_l, tween.in_cubic)

async def my_blushing_expression(self):
    while True:
        arrived, departed = await self.until_nearby_change()
        if "cutie_pie" in arrived:
            await self.gesture(my_blushing_gesture())
            flushed_color = self.base_color.blend(colors.RED, 0.3)
            await self.untilTweenCompleted(flushed_color, 5000)
        if "cutie_pie" in departed:
            await self.sleep_ms(10000)
            await self.untilTweenCompleted(self.base_color, 5000)
            


async def my_blushing_gesture(self):
    original_color = self.current_color()
    blushing_color = colors.PINK.scale_brightness(original_color.brightness())
    # Woo, woo!
    await self.tween_in_and_out(original_color, blushing_color, 1500, 2250)
    await self.tween_in_and_out(original_color, blushing_color, 2500, 3250)
    # On, they saw me, eep!
    await self.sleep_ms(10000)
    # Haha, Boop!
    await await self.tween_in_and_out(original_color, blushing_color, 750, 1000)
    # Will return to the original expression color automatically
    # before resuming the expression this interrupted
```

