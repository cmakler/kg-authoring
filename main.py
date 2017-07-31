import json
import os

from flask import Flask, jsonify

from viewObjects import point

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


def open_json_file(open_file):
    with open(os.path.join(APP_ROOT, open_file), 'r') as datafile:
        return json.load(datafile)


@app.route('/')
def hello_world():
    return '<h1>Hello world!</h1>'


@app.route('/<name>', methods=['GET'])
def test_json(name):
    c1 = open_json_file('data/'+name+'.json')
    response = jsonify(c1)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run(debug=True)
