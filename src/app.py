#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

import os
import json
from threading import Lock

from flask_socketio import SocketIO
from flask import Flask, render_template, request
from werkzeug.exceptions import HTTPException

from logic.main import AppContext

app = Flask(__name__, static_url_path='/static')

if not app.debug:
    import eventlet
    eventlet.monkey_patch()


"""  Configuration """

filename = os.path.join(app.static_folder, 'config.json')
with open(filename) as FILE:
    configuration = json.load(FILE)

''' Flask config '''
app.secret_key = configuration["secret_key"]


''' Websockets context '''
socketio = SocketIO(app, logger=app.debug, engineio_logger=app.debug)
thread = None
thread_lock = Lock()


''' Mididings and OSC context '''
appContext = None
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    appContext = AppContext(
        configuration["osc_server"])


'''
    REST API endpoints
'''


@app.get("/")
def index():
    return render_template('index.html')


@app.get("/ui")
def presentation():
    return render_template('ui.html') if appContext.scene_logic.scenes else render_template('no_context.html')


@app.get("/quit", endpoint="quit")
@app.get("/panic", endpoint="panic")
@app.get("/restart", endpoint="restart")
@app.get("/prev_scene", endpoint="prev_scene")
@app.get("/next_scene", endpoint="next_scene")
@app.get("/next_subscene", endpoint="next_subscene")
@app.get("/prev_subscene", endpoint="prev_subscene")
@app.get("/switch_scene/<int:id>", endpoint="switch_scene")
@app.get("/switch_subscene/<int:id>", endpoint="switch_subscene")
def on_navigate(id=None):
    delegates[request.endpoint]() if id is None else delegates[request.endpoint](int(id))
    return '', 204


''' SocketIO events '''


@socketio.on('connect')
def on_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(osc_observer_thread)

@socketio.on('mididings')
def on_handler(payload):
    delegates[payload["command"]]() if not "id" in payload else delegates[payload["command"]](int(payload["id"]))

@socketio.on('action', namespace="/main")
def on_action_handler(payload):
    global_delegates[payload["command"]]() 


''' Methods  '''

def on_quit():
    socketio.emit("on_terminate")

def mididings_context_update():
    appContext.set_dirty(False)
    socketio.emit('mididings_context_update',
                  appContext.scene_logic.payload)


def get_mididings_context():
    mididings_context_update()


def osc_observer_thread():
    while True:
        if appContext.is_dirty():
            mididings_context_update()
        socketio.emit("on_start") if appContext.is_running(
        ) else socketio.emit("on_exit")
        socketio.sleep(0.125)


'''
Dict of methods
'''
delegates = {
    "quit" : appContext.quit,
    "panic" : appContext.panic,
    "query" : appContext.query,
    "restart" : appContext.restart,
    "next_scene" : appContext.next_scene,
    "prev_scene" : appContext.prev_scene,
    "switch_scene" : appContext.switch_scene,
    "next_subscene" : appContext.next_subscene,
    "prev_subscene" : appContext.prev_subscene,
    "switch_subscene" : appContext.switch_subscene,
    "get_mididings_context" : get_mididings_context,
    "mididings_context_update" : mididings_context_update
}


global_delegates = {
    #"on_connect": on_connect,
    #"on_refresh": on_refresh,
    "quit" : on_quit,
}

'''
Error Handling
'''


@socketio.on_error()
def error_handler(e):
    print(e)


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


if __name__ == "__main__":
    print(f"Flaskdings running on port {configuration['port']}")
    socketio.run(app, host=configuration["host"], port=configuration["port"])
