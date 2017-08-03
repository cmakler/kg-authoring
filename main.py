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
    author = open_json_file('author/'+name+'.json')
    return allow_cors(jsonify(parser.parse(author)))


# Note: this will be replaced by an actual database someday
@app.route('/data/<path:path>', methods=['GET'])
def send_data(path=None):
    directory = os.path.join(APP_ROOT, 'data/')
    return allow_cors(send_from_directory(directory, path))


if __name__ == '__main__':
    app.run(debug=True)
