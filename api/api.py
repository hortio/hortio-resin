#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
from datetime import datetime
from collections import OrderedDict

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, request, redirect, jsonify
from flask_basicauth import BasicAuth
from flask_cors import CORS
from lsm import LSM
from waitress import serve

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

OUTPUTS = [
    {
        "key": "l0-light",
        "gpio": 6,
        "label": u"Свет - верхняя полка",
    },
    {
        "key": "l1-light",
        "gpio": 5,
        "label": u"Свет - нижняя полка",
    },
    {
        "key": "air-in",
        "gpio": 0,
        "label": u"Воздух - забор",
    },
    {
        "key": "air-out",
        "gpio": 1,
        "label": u"Воздух - выдув",
    },
    {
        "key": "pump",
        "gpio": 7,
        "label": u"Насос",
    }
]

SENSORS = [
    {"key":  "l0-t",
     "label": u"Температура - верхняя полка (°C)"},
    {"key": "l0-h",
     "label": u"Влажность - верхняя полка (%)"},
    {"key": "l1-t",
     "label": u"Температура - нижняя полка (°C)"},
    {"key": "l1-h",
     "label":  u"Влажность - нижняя полка (%)"},
    {"key": "solution-t",
     "label":  u"Температура раствора (°С)"},
    {"key": "solution-ph",
     "label":  u"pH раствора"},
    {"key": "solution-ec",
     "label": u"EC раствора (mS/cm)"}
]

# Setup DB
db = LSM(os.getenv("DB_FILE", "/data/hortio.ldb"))


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


def get_outputs():
    outputs = OrderedDict()
    for v in OUTPUTS:
        k = v["key"]
        outputs[k] = {
            "label": v["label"],
            "value": db_get(k)
        }
    return outputs


def get_sensors():
    sensors = OrderedDict()
    for v in SENSORS:
        k = v["key"]
        sensors[k] = {
            "label": v["label"],
            "value": db_get(k),
            "at": db_get("{}-at".format(k))
        }
    return sensors


def set_output(key, value):
    db_set(key, value)


# Server
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['BASIC_AUTH_USERNAME'] = os.getenv('ADMIN_USERNAME', 'admin')
app.config['BASIC_AUTH_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'password')
CORS(app)

basic_auth = BasicAuth(app)


def day_of_cycle():
    """Return day of cycle (0 - 45)"""
    try:
        timestamp = parse(db_get('cycle-start-date'))
    except ValueError:
        timestamp = parse(DEFAULT_STATES["cycle-start-date"])

    start_date = timestamp.date()
    return relativedelta(datetime.now().date(), start_date).days


def phase_description(day):
    if day < 4:
        description = u"Прорастание семян"
    elif day < 10:
        description = u"Укоренениe проростков"
    elif day < 19:
        description = u"Микрозелень"
    else:
        description = u"Вегетационный период"

    return description


@app.route('/', methods=['GET', 'POST'])
@basic_auth.required
def dashboard():
    if request.method == 'POST':
        for v in OUTPUTS:
            key = v["key"]

            try:
                value = request.form[key]
            except KeyError:
                continue

            set_output(key, value)

    return render_template('dashboard.html',
                           outputs=get_outputs(),
                           sensors=get_sensors(),
                           day_of_cycle=day_of_cycle(),
                           current_time=datetime.now())


@app.route('/cycle_date/', methods=['POST'])
@basic_auth.required
def cycle_date():
    try:
        date = request.form["cycle-date"]
    except KeyError:
        date = str(datetime.now().date())

    db_set("cycle-start-date", date)

    return redirect('/')

@app.route('/today')
def today():
    return render_template('today.html',
                           sensors=get_sensors(),
                           day_of_cycle=day_of_cycle(),
                           current_time=datetime.now())

@app.route('/state.json')
def api():
    day = day_of_cycle()
    state = {
        "sensors": get_sensors(),
        "cycle": {
            "day": day,
            "phase_description": phase_description(day)
        }
    }
    return jsonify(state)


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
