from mpu6050.imu import MPU6050
from time import sleep, ticks_us
from machine import Pin, I2C, Timer



i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=800000)
imu = MPU6050(i2c)

def isr(_):
    imu.accel_irq()

timer = Timer(-1)
timer.init(period = 1000 // 200, callback=isr)
# while True:
#     start = ticks_us()
#     print(imu.accel_irq())
    # print(imu.accel.ixyz)
    # print(imu.accel.xyz)
    # ax,ay,az = imu.accel.xyz
    # ax=round(imu.accel.x,2)
    # ay=round(imu.accel.y,2)
    # az=round(imu.accel.z,2)
    # gx,gy,gz = imu.gyro.xyz
    # gx=round(imu.gyro.x)
    # gy=round(imu.gyro.y)
    # gz=round(imu.gyro.z)
    # tem=round(imu.temperature,2)
    # elapsed = ticks_us() - start
    # print("Elapsed: ", elapsed, "us")
    # print("ax",ax,"\t","ay",ay,"\t","az",az,"\t","gx",gx,"\t","gy",gy,"\t","gz",gz,"\t","Temperature",tem,"        ",end="\r")
    # sleep(0.2)