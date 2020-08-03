import os
import sys
from flask import Flask
from flask import request
from flask import jsonify

def local_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

libdir = local_path("lib")

if os.path.exists(libdir):
    sys.path.append(libdir)

from state import state

app = Flask(__name__)

def write_command(command, arguments):
    filename = local_path('COMMAND')
    file = open(filename, "w")
    file.write(command + "\n")
    file.write(arguments + "\n")
    file.close()

@app.route('/status')
def status():
    s = state.load(local_path('state.dat'))
    return jsonify({"state": s.state})

@app.route('/command', methods=['POST'])
def command():
    command = request.get_json()
    print(command['command'])
    write_command(command['command'], command['arguments'])
    return "OK"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
