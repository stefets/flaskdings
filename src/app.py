#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

import os
import json
from threading import Lock

from flask_socketio import SocketIO
from flask import Flask, render_template, request
from werkzeug.exceptions import HTTPException

from services.logic import LogicService
from flasgger import Swagger

app = Flask(__name__, static_url_path='/static')
app.config['SWAGGER'] = {
    "swagger": "2.0",
    'title': 'FlaskDings API',
    'uiversion': 3,
    'description' : 'The mididings REST API specifications',
    'termsOfService': "",
    "version": "1.0.0",
}
swagger = Swagger(app)

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
logic = None
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    logic = LogicService(
        configuration["osc_server"])


'''
    REST API endpoints
'''


@app.route("/", endpoint="home")
@app.get("/ui/", endpoint="view")
def index():
    return \
    render_template('index.html') if request.endpoint == "home" else \
    render_template('ui.html') if logic.scene_context.scenes else render_template('no_context.html')


@app.get("/api/quit", endpoint="quit")
@app.get("/api/panic", endpoint="panic")
@app.get("/api/restart", endpoint="restart")
@app.get("/api/query", endpoint="query")
def on_command():
    """
    Execute command endpoint
    ---
    tags:
      - Options    
    responses:
      204:
        description: No content
    """
    delegates[request.endpoint]()
    return '', 204

@app.get("/api/prev_scene", endpoint="prev_scene")
@app.get("/api/next_scene", endpoint="next_scene")
@app.get("/api/next_subscene", endpoint="next_subscene")
@app.get("/api/prev_subscene", endpoint="prev_subscene")
def on_switch_scene_subscene():
    """
    Execute navigation endpoint
    ---
    tags:
      - Navigation
    responses:
      204:
        description: No content
    """
    delegates[request.endpoint]()
    return '', 204

@app.get("/api/switch_scene/<int:id>", endpoint="switch_scene")
@app.get("/api/switch_subscene/<int:id>", endpoint="switch_subscene")
def on_get_with_id(id):
    """
    Switch to a specific [sub]scene
    ---
    tags:
      - Navigation
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the [sub]scene to switch to
    responses:
      204:
        description: No content
    """
    delegates[request.endpoint](int(id))
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
    logic.set_dirty(False)
    socketio.emit('mididings_context_update',
                  logic.scene_context.payload)


def get_mididings_context():
    mididings_context_update()


def osc_observer_thread():
    while True:
        if logic.is_dirty():
            mididings_context_update()
        socketio.emit("on_start") if logic.is_running(
        ) else socketio.emit("on_exit")
        socketio.sleep(0.125)


'''
Dict of methods
'''
delegates = {
    "quit" : logic.quit,
    "panic" : logic.panic,
    "query" : logic.query,
    "restart" : logic.restart,
    "next_scene" : logic.next_scene,
    "prev_scene" : logic.prev_scene,
    "switch_scene" : logic.switch_scene,
    "next_subscene" : logic.next_subscene,
    "prev_subscene" : logic.prev_subscene,
    "switch_subscene" : logic.switch_subscene,
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
