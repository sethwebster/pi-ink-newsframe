import os
from flask import Flask
from flask import request

app = Flask(__name__)


def local_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def write_command(command, arguments):
    filename = local_path('COMMAND')
    file = open(filename, "w")
    file.write(command + "\n")
    file.write(arguments + "\n")
    file.close()

@app.route('/status')
def status():
    return 'OK'

@app.route('/command', methods=['POST'])
def command():
    command = request.get_json()
    print(command['command'])
    write_command(command['command'], command['arguments'])
    return "OK"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
