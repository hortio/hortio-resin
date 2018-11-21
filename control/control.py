#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
from datetime import datetime


import Adafruit_GPIO as GPIO
import Adafruit_GPIO.I2C as I2C
import Adafruit_GPIO.MCP230xx as MCP
import Adafruit_PureIO.smbus
import pyownet
import schedule
from dateutil.parser import parse
from lsm import LSM

import lib.Adafruit_BME280 as BME280
import lib.MCP342x as MCP342x
from lib.smsc_api import SMSC

PCA9548A_ADDR = 0x70
PCA9548A_CH0 = 0b00000001
PCA9548A_CH1 = 0b00000010

DEFAULT_STATES = {
    # L0 - Upper
    # L1 - Lower
    # Inputs
    "l0-t": 0,
    "l0-h": 0,
    "l1-t": 0,
    "l1-h": 0,
    "solution-t": 0,
    "solution-ph": 0,
    "solution-ec": 0,
    # Outputs
    "l0-light": 0,
    "l1-light": 0,
    "air-in": 1,
    "air-out": 1,
    "pump": 1,
    # State
    "cycle-start-date": "2018-09-13"
}

OUTPUTS = {
    "l0-light": {
        "gpio": 6,
        "label": u"Свет - верхняя полка",
    },
    "l1-light": {
        "gpio": 5,
        "label": u"Свет - нижняя полка",
    },
    "air-in": {
        "gpio": 0,
        "label": u"Воздух - забор",
    },
    "air-out": {
        "gpio": 1,
        "label": u"Воздух - выдув",
    },
    "pump": {
        "gpio": 7,
        "label": u"Насос",
    }
}

SMS_NOTIFICATIONS = dict([
    (10, "10д. Долейте воду и удобрения: Micro-12.5мл, Grow-12.5мл, Bloom-12.5мл"),
    (20, "20д. Долейте воду и удобрения: Micro-25мл, Grow-25мл, Bloom-25мл"),
    (30, "30д. Долейте воду и удобрения: Micro-25мл, Grow-25мл, Bloom-25мл"),
    (45, "45д. Начните новый цикл. Детали: http://admin.vhnh.hort.io/today")
])

# Setup IO
mcp = MCP.MCP23008()

for out in range(8):
    mcp.setup(out, GPIO.OUT)

# Setup DB
db = LSM(os.getenv("DB_FILE", "/data/hortio.ldb"))


def pca9548a_setup(pca9548a_channel):
    """
    Set i2c multiplexer (pca9548a) channel
    """
    pca9548a = I2C.get_i2c_device(PCA9548A_ADDR)
    pca9548a.writeRaw8(pca9548a_channel)
    time.sleep(0.1)


def db_get(key):
    if key in DEFAULT_STATES:
        default_value = DEFAULT_STATES[key]
    else:
        default_value = 0

    try:
        value = db[key]
    except KeyError:
        db[key] = value = default_value

    return value


def db_set(key, value):
    db[key] = value


def set_output(key, value):
    mcp.output(OUTPUTS[key]["gpio"], bool(int(value)))


def set_outputs():
    for k in OUTPUTS:
        set_output(k, db_get(k))


def day_of_cycle():
    """Return day of cycle (0 - 45)"""
    try:
        timestamp = parse(db_get('cycle-start-date'))
    except ValueError:
        timestamp = parse(DEFAULT_STATES["cycle-start-date"])

    return (datetime.now() - timestamp).days


def update_sensors_data():
    """Read all sensors and set data to DB"""
    owproxy = pyownet.protocol.proxy(host="owfs", port=4304)

    ow_sensors = owproxy.dir()
    if len(ow_sensors) > 0:
        temperature = float(owproxy.read(ow_sensors[0] + 'temperature'))
        db_set("solution-t", '{:.1f}'.format(temperature))
        db_set("solution-t-at", '{}'.format(datetime.now()))

     
        # Setup pH and EC
        bus =  Adafruit_PureIO.smbus.SMBus(I2C.get_default_bus())
        ec_adc = MCP342x.MCP342x(bus, 0x68, channel=0, resolution=18)
        ph_adc = MCP342x.MCP342x(bus, 0x68, channel=1, resolution=18)

        # EC
        ec_voltage = ec_adc.convert_and_read()
        RES2 = 820.0
        ECREF = 200.0
        raw_ec = 1000 * ec_voltage / RES2 / ECREF
        # temperature compensation
        ec = raw_ec / (1.0+0.0185*(temperature-25.0))

        if ec > 0.1:
            db_set("solution-ec", '{:.1f}'.format(float(ec)))
            db_set("solution-ec-at", '{}'.format(datetime.now()))

        # pH

        ph_voltage = ph_adc.convert_and_read()
        # TODO: should be calibrated
        ph = -5.70 * ph_voltage + 10

        if ph > 2 and ph < 10:
            db_set("solution-ph", '{:.1f}'.format(float(ph)))
            db_set("solution-ph-at", '{}'.format(datetime.now()))

    for idx, channel in enumerate([PCA9548A_CH0, PCA9548A_CH1]):
        pca9548a_setup(channel)

        bme280 = BME280.BME280(
            address=0x76,
            t_mode=BME280.BME280_OSAMPLE_8,
            p_mode=BME280.BME280_OSAMPLE_8,
            h_mode=BME280.BME280_OSAMPLE_8)

        degrees = bme280.read_temperature()
        db_set("l{}-t".format(idx), '{:.1f}'.format(degrees))
        db_set("l{}-t-at".format(idx), '{}'.format(datetime.now()))

        humidity = bme280.read_humidity()
        db_set("l{}-h".format(idx), '{:.0f}'.format(humidity))
        db_set("l{}-h-at".format(idx), '{}'.format(datetime.now()))


def notify_users():
    """Send SMS notifications, if necessary"""
    today = day_of_cycle()
    if today in SMS_NOTIFICATIONS:
        smsc = SMSC()
        phone_numbers = filter(None, os.getenv('SMS_NUMBERS', '').split(','))
        for number in phone_numbers:
            smsc.send_sms(number, SMS_NOTIFICATIONS[today])


def turn_off_lights():
    """Turn off lights if necessary"""
    if day_of_cycle() > 3:
        db_set("l0-light", 0)
        db_set("l1-light", 0)


def turn_on_lights():
    """Turn on lights if necessary"""
    if day_of_cycle() > 3:
        db_set("l0-light", 1)
        db_set("l1-light", 1)


def setup_scheduler():
    """Setup scheduler"""

    report_period = int(os.getenv('REPORT_PERIOD', '5'))
    schedule.every(report_period).seconds.do(update_sensors_data)

    output_period = int(os.getenv('OUTPUT_PERIOD', '10'))
    schedule.every(output_period).seconds.do(set_outputs)

    schedule.every().day.at(os.getenv("LIGHT_ON_TIME", "5:00")).do(turn_on_lights)
    schedule.every().day.at(os.getenv("LIGHT_OFF_TIME", "21:00")).do(turn_off_lights)

    schedule.every().day.at(os.getenv("SMS_NOTIFICATION_TIME", "9:30")).do(notify_users)


if __name__ == "__main__":
    setup_scheduler()

    while True:
        schedule.run_pending()
        time.sleep(1)
