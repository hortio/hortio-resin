#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from flask import Flask, render_template, request
import requests

# Setup app
app = Flask(__name__)

data = {
    "cycle": {
        "day": 0,
        "phase_description": u"Начало"
    },
    "sensors": {
        "l0-h": {
            "at": "2018-09-18 05:41:06.155008",
            "label": u"Влажность - верхняя полка (%)",
            "value": "70"
        },
        "l0-t": {
            "at": "2018-09-18 05:41:06.155008",
            "label": u"Температура - верхняя полка (°C)",
            "value": "19.8"
        },
        "l1-h": {
            "at": "2018-09-18 05:41:06.339425",
            "label": u"Влажность - нижняя полка (%)",
            "value": "72"
        },
        "l1-t": {
            "at": "2018-09-18 05:41:06.338959",
            "label": u"Температура - нижняя полка (°C)",
            "value": "19.7"
        },
        "solution-ec": {
            "at": "0",
            "label": u"EC раствора (mS/cm)",
            "value": "0"
        },
        "solution-ph": {
            "at": "0",
            "label": u"pH раствора",
            "value": "0"
        },
        "solution-t": {
            "at": "2018-09-18 05:41:05.971672",
            "label": u"Температура раствора (°С)",
            "value": "20.4"
        }
    }
}


@app.route('/', methods=['GET'])
def dashboard():
    global data

    try:
        url = os.getenv("API_URL", "http://api/state.json")
        r = requests.get(url)
        data = r.json()
    except requests.exceptions.ConnectionError:
        pass

    return render_template('dashboard.html', data=data)


if __name__ == "__main__":
    context = ('certs/cert.pem', 'certs/cert.key.pem')
    app.run(host='0.0.0.0', port=8081, ssl_context=context,
            threaded=True, debug=True)
