import os

from flask import Flask, render_template, request
import requests

# Setup app
app = Flask(__name__)


@app.route('/', methods=['GET'])
def dashboard():
    url = os.getenv("API_URL", "http://api/state.json") 
    r = requests.get(url)
    return render_template('dashboard.html', data = r.json())

if __name__ == "__main__":
    context = ('certs/cert.pem', 'certs/cert.key.pem')
    app.run(host='0.0.0.0', port=8081, ssl_context=context,
            threaded=True, debug=True)
