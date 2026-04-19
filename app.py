from flask import Flask, request, abort
from pylips import Pylips, args
import os
import importlib
import re
import sys
import subprocess

app = Flask(__name__)
pylips = Pylips(args.config)
if not hasattr(pylips, "available_commands"):
    print("Could not start pylips, please check logs", file=sys.stderr)
    exit(1)

TOKEN = os.environ.get("HTTP_TOKEN")

def assert_token():
    if TOKEN is None:
        return
    
    get_token = request.args.get("token", default="", type=str)
    auth_token = request.headers.get('Authorization', '').removeprefix("Bearer ")

    if TOKEN != get_token and TOKEN != auth_token:
        print("Invalid token")
        abort(401, "Invalid token")


@app.route('/')
def index():
    assert_token()
    result = {}
    for method, commands in pylips.available_commands.items():
        array = {}
        if method == "get":
            result["query"] = array
        elif method == "post":
            result["command"] = array
        else:
            result[method] = array

        for key, configuration in commands.items():
            array[key] = configuration.get("path", None)

    return result


# GET is required as some of my clients are only capable of sending GET requests
@app.route('/command/<command>', methods=['GET', 'POST'])
def command(command: str):
    assert_token()
    return pylips.run_command(command)


@app.route('/query/<command>', methods=['GET', 'POST'])
def query(command: str):
    assert_token()
    return pylips.run_command(command)

@app.route('/script/<script>', methods=['GET', 'POST'])
def script(script: str):
    assert_token()

    script_name = re.sub(r'\W+', '', script)

    try:
        script_module = importlib.import_module(f"scripts.{script_name}")
        importlib.reload(script_module)
        return script_module.run(pylips, request)
    except ModuleNotFoundError:
        abort(404, f"No script with name {script_name} found")


@app.route('/adb/<command>', methods=['GET', 'POST'])
def adb(command: str):
    assert_token()
    adb_commands = pylips.available_commands["adb"]
    if (command not in adb_commands):
        abort(404, f"Unknown command: {command}")
        return

    connect = subprocess.run(['adb', 'connect', f"{pylips.config["TV"]["host"]}:5555"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if connect.returncode != 0:
        abort(400, f"Cannot connect to adb device, got: ${connect.stdout.decode("utf-8")}")
        return

    devices = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if ("unauthorized" in devices.stdout.decode("utf-8")):
        abort(401, "Need to authorize device first.")
        return

    shell_command = adb_commands[command]["shell"]    
    result = subprocess.run(['adb', 'shell', shell_command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    subprocess.run(['adb', 'kill-server'])

    if result.returncode == 0:
        return result.stdout.decode("utf-8")
    else:
        abort(400, result.stdout.decode("utf-8"))

if __name__ == '__main__':
    app.run()
