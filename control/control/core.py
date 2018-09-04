#!/usr/bin/python

import Adafruit_GPIO as GPIO
import Adafruit_GPIO.I2C as I2C
import Adafruit_GPIO.MCP230xx as MCP
import time
import lib.Adafruit_BME280 as BME280
import pyownet

PCA9548A_ADDR = 0x70
PCA9548A_CH0 = 0b00000001
PCA9548A_CH1 = 0b00000010


def pca9548a_setup(pca9548a_channel):
    """
    Set i2c multiplexer (pca9548a) channel
    """
    pca9548a = I2C.get_i2c_device(PCA9548A_ADDR)
    pca9548a.writeRaw8(pca9548a_channel)
    time.sleep(0.1)
    print "PCA9548A I2C channel status:", bin(pca9548a.readRaw8())


if __name__ == '__main__':
  # Setup
    mcp = MCP.MCP23008()
    for out in range(8):
        mcp.setup(out, GPIO.OUT)

    while True:
        # mcp.output(0, GPIO.HIGH)  # Pin 0 High
        # time.sleep(5)
        # mcp.output(0, GPIO.LOW)  # Pin 0 Low
        # time.sleep(5)
        owproxy = pyownet.protocol.proxy(host="owfs", port=4304)
        print(owproxy.dir())
        print(owproxy.read(owproxy.dir()[0] + 'temperature'))

        for channel in [PCA9548A_CH0, PCA9548A_CH1]:
            pca9548a_setup(channel)

            bme280 = BME280.BME280(
                address=0x76,
                t_mode=BME280.BME280_OSAMPLE_8,
                p_mode=BME280.BME280_OSAMPLE_8,
                h_mode=BME280.BME280_OSAMPLE_8)

            degrees = bme280.read_temperature()
            humidity = bme280.read_humidity()

            print('Temp      = {0:0.3f} deg C'.format(degrees))
            print('Humidity  = {0:0.2f} %'.format(humidity))

        time.sleep(5)
