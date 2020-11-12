import os
import sys
from flask import (Flask, render_template, send_from_directory)
from flask import request
from flask import jsonify
from flask_cors import CORS


def local_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


libdir = local_path("lib")

if os.path.exists(libdir):
    sys.path.append(libdir)

from state import state

app = Flask(__name__)

CORS(app)

def write_command(command, arguments):
    filename = local_path('COMMAND')
    file = open(filename, "w")
    file.write(command + "\n")
    file.write(arguments + "\n")
    file.close()


@app.route('/', defaults={'u_path': 'index.html', 'type':''})
@app.route('/static/<string:type>/<string:u_path>')
@app.route('/<string:u_path>')
def index(u_path, type):
    print("HIT")
    print(u_path)
    print(type)
    if (type):
        return send_from_directory("client/build/static/"+type, u_path)
    else:
        return send_from_directory("client/build",u_path)

@app.route('/status')
def status():
    s = state.load(local_path('state.json'))
    return jsonify({"state": s.state})


@app.route('/command', methods=['POST'])
def command():
    command = request.get_json()
    print(command['command'])
    write_command(command['command'], command['arguments'])
    return "OK"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
