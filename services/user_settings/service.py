import os
from threading import Lock
import json

from bottle import run, abort, request, post, get, response

global_lock = Lock()
SETTINGS_PATH = "/etc/command_center/user-settings.json"

urls = (
    '/', 'All'
         '/(\w+)', 'Setting'
)


@get('/')
def get_all_settings():
    with global_lock:
        if not os.path.exists(SETTINGS_PATH):
            settings = {}
        else:
            with open(SETTINGS_PATH, 'r') as f:
                settings = json.load(f)
        response.content_type = 'application/json'
        return json.dumps(settings)


@get('/<name>')
def get_setting(name):
    with global_lock:
        if not os.path.exists(SETTINGS_PATH):
            settings = {}
        else:
            with open(SETTINGS_PATH, 'r') as f:
                settings = json.load(f)

        if name not in settings:
            abort(404, 'Setting not found.')

        response.content_type = 'application/json'
        return json.dumps(settings[name])


@post('/<name>')
def update_setting(name):
    with global_lock:
        if not os.path.exists(SETTINGS_PATH):
            settings = {}
        else:
            with open(SETTINGS_PATH, 'r') as f:
                settings = json.load(f)
        try:
            body = json.load(request.body)
        except ValueError:
            abort(400, 'Content is not valid JSON object')
            return

        settings[name] = body
        with open(SETTINGS_PATH, 'w') as out:
            json.dump(settings, out)


if __name__ == "__main__":
    run(host='0.0.0.0', port=8085)
