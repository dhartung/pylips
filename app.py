from flask import Flask, request, abort
from pylips import Pylips, args
import os
import importlib
import re

app = Flask(__name__)
pylips = Pylips(args.config)

TOKEN = os.environ.get("HTTP_TOKEN")

def assert_token():
    if TOKEN is None:
        return

    if TOKEN != request.args.get("token", default="", type=str):
        print("Invalid token")
        abort(401)


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


@app.route('/command/<command>')
def command(command: str):
    assert_token()
    return pylips.run_command(command)


@app.route('/query/<command>')
def query(command: str):
    assert_token()
    return pylips.run_command(command)

@app.route('/script/<script>')
def script(script: str):
    assert_token()

    script_name = re.sub(r'\W+', '', script)

    try:
        script_module = importlib.import_module(f"scripts.{script_name}")
        importlib.reload(script_module)
        return script_module.run(pylips, request)
    except ModuleNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run()
