# import led_main
import led__holiday_main
import 
# from machine import SoftI2C, I2C, Pin, sleep

# from mpu6050 import accel
# # i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000) 
# i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000) 
# accelerometer = accel(i2c)
# while True:
#     print(accelerometer.get_values())
#     sleep(100)
# print(results)




# i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000) 
# scan = i2c.scan()
# accel_address = 104
# # i2c.start()
# # i2c.writeto_mem(accel_address, 0x6b, bytearray(0x00))
# i2c.writeto(accel_address, bytearray(0x6b)) # Talk to the register 6B
# i2c.writeto(accel_address, bytearray(0x00)) # Make reset - place a 0 into the 6B register

# i2c.writeto(accel_address, bytearray(0x1c)) # Talk to the ACCEL_CONFIG register (1C hex)
# i2c.writeto(accel_address, bytearray(0x10)) # Set the register bits as 00010000 (+/- 8g full scale range)


# while True:
#     i2c.writeto(accel_address, bytearray(0x3B)) # Start with register 0x3B (ACCEL_XOUT_H)

#     result = i2c.readfrom(accel_address, 6)
#     print(result)
#   Wire.requestFrom(MPU, 6, true); // Read 6 registers total, each axis value is stored in 2 registers
#   //For a range of +-2g, we need to divide the raw values by 16384, according to the datasheet
#   AccX = (Wire.read() << 8 | Wire.read()) / 16384.0; // X-axis value
#   AccY = (Wire.read() << 8 | Wire.read()) / 16384.0; // Y-axis value
#   AccZ = (Wire.read() << 8 | Wire.read()) / 16384.0; // Z-axis value

# import _thread
# from machine import Pin
# import utime

# led = Pin(5, Pin.OUT)

# def led_thread():
#     while True:
#         led.value(1)
#         utime.sleep(0.1)
#         led.value(0)
#         utime.sleep(0.1)

# def print_thread():
#     while True:
#         print(".", end="")
#         utime.sleep(0.1)
#         led.value(0)
#         utime.sleep(0.1)


# _thread.start_new_thread(led_thread, ())
# _thread.start_new_thread(print_thread, ())
# print_thread()

