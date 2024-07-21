from flask import Flask, request, abort
from pylips import Pylips, args
import os

TOKEN = os.environ.get("HTTP_TOKEN")
def assert_token():
    if TOKEN is None:
        return
    
    if TOKEN != request.args.get("token", default="", type=str):
        abort(401)


app = Flask(__name__)
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
def command(commandString: str):
    assert_token()
    return pylips.run_command(commandString)

@app.route('/query/<command>')
def command(commandString: str):
    assert_token()
    return pylips.run_command(commandString)

pylips: Pylips
if __name__ == '__main__':
    pylips = Pylips(args.config)
    app.run()