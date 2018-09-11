#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time

import Adafruit_GPIO as GPIO
import Adafruit_GPIO.I2C as I2C
import Adafruit_GPIO.MCP230xx as MCP
from flask import Flask, render_template, request
from flask_basicauth import BasicAuth
from lsm import LSM
import pyownet
from waitress import serve

import lib.Adafruit_BME280 as BME280

PCA9548A_ADDR = 0x70
PCA9548A_CH0 = 0b00000001
PCA9548A_CH1 = 0b00000010

DEFAULT_STATES = {
    # L0 - Upper
    # L0 - Lower
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
    "air-in": 0,
    "air-out": 0,
    "pump": 0,
    # State
    "day-of-cycle": 0
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
    "air-out":{
        "gpio": 1,
        "label": u"Воздух - выдув",
    },
    "pump": {
        "gpio": 7,
        "label": u"Насос",
    }
}

def pca9548a_setup(pca9548a_channel):
    """
    Set i2c multiplexer (pca9548a) channel
    """
    pca9548a = I2C.get_i2c_device(PCA9548A_ADDR)
    pca9548a.writeRaw8(pca9548a_channel)
    time.sleep(0.1)
    print "PCA9548A I2C channel status:", bin(pca9548a.readRaw8())


# Setup DB
db = LSM('/data/hortio.ldb')
mcp = MCP.MCP23008()

for out in range(8):
    mcp.setup(out, GPIO.OUT)

def db_get(key):
    if key not in DEFAULT_STATES:
        return None 

    try:
        db[key]
    except KeyError:
        db[key] = DEFAULT_STATES[key]
    
    return db[key]

def db_set(key, value):
    if key in DEFAULT_STATES:
        db[key] = value

def get_outputs():
    outputs = {}
    for k, v in OUTPUTS.iteritems():
        outputs[k] = {
            "label": v["label"],
            "value": db_get(k)
        }
    return outputs

def set_output(key, value):
    db_set(key, value)
    mcp.output(OUTPUTS[key]["gpio"], bool(int(value)))

# Server
app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = os.getenv('ADMIN_USERNAME', 'admin')
app.config['BASIC_AUTH_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'password')
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

@app.route('/', methods=('GET','POST'))
def dashboard():
    if request.method == 'POST':
        for key in OUTPUTS:

            try:
                value = request.form[key]
            except KeyError:
                continue

            set_output(key, value)

    return render_template('dashboard.html', outputs = get_outputs())

def run_inputs():
    while True:
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

        time.sleep(int(os.getenv('REPORT_PERIOD', '10')))

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)    
