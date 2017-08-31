import json
import os

from flask import Flask, jsonify, send_from_directory, render_template

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


def open_json_file(open_file):
    with open(os.path.join(APP_ROOT, open_file), 'r') as datafile:
        return json.load(datafile)


def allow_cors(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/')
def index():
    return send_from_directory(APP_ROOT, 'index.html')


@app.route('/examples/<path:path>', methods=['GET'])
def send_example(path=None):
    return render_template(path)


@app.route('/<path:path>', methods=['GET'])
def send_file(path=None):
    directory = os.path.join(APP_ROOT, 'static/')
    return allow_cors(send_from_directory(directory, path))


if __name__ == '__main__':
    app.run(debug=True)
