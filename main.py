import json
import os

from flask import Flask, jsonify, send_from_directory
from parsers import *

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
    return '<h1>KG Authoring</h1><p>KG Authoring is a web service that generates JSON readable by KGJS from more author-friendly formats.</p>'


@app.route('/convert/<name>', methods=['GET'])
def convert_json(name):
    print('received request for ', name)
    author = open_json_file('author/'+name+'.json')
    print('opened json')
    converted = parser.parse(author)
    print('converted json')
    formatted = jsonify(converted)
    print('jsonified result')
    return allow_cors(formatted)


# Note: this will be replaced by an actual database someday
@app.route('/data/<path:path>', methods=['GET'])
def send_data(path=None):
    directory = os.path.join(APP_ROOT, 'data/')
    return allow_cors(send_from_directory(directory, path))


@app.route('/js/<path:path>', methods=['GET'])
def send_js(path=None):
    directory = os.path.join(APP_ROOT, 'static/js/')
    return allow_cors(send_from_directory(directory, path))


@app.route('/css/<path:path>', methods=['GET'])
def send_css(path=None):
    directory = os.path.join(APP_ROOT, 'static/css/')
    return allow_cors(send_from_directory(directory, path))


if __name__ == '__main__':
    app.run(debug=True)
