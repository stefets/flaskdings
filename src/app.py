#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

import os
import json
from threading import Lock

from flask_socketio import SocketIO
from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

from blueprint.views import frontend
from services.live import LiveContext


app = Flask(__name__)

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
live_context = None
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    live_context = LiveContext(
        configuration["osc_server"])


"""  Bluebrint(s) """
app.config['live_context'] = live_context.scene_context
app.register_blueprint(frontend)


'''
    Api routes
'''


@app.get("/")
def index():
    return render_template('index.html')


@app.get("/next_scene")
def api_next_scene():
    _next_scene()
    return '', 204


@app.get("/prev_scene")
def api_prev_scene():
    _prev_scene()
    return '', 204


@app.get("/next_subscene")
def api_next_subscene():
    _next_subscene()
    return '', 204


@app.get("/prev_subscene")
def api_prev_subscene():
    _prev_subscene()
    return '', 204


@app.get("/switch_scene/<int:id>")
def api_switch_scene(id):
    _switch_scene(id)
    return '', 204


@app.get("/switch_subscene/<int:id>")
def api_switch_subscene(id):
    _switch_subscene(id)
    return '', 204


@app.get("/quit")
def api_quit():
    _quit()
    return '', 204


@app.get("/panic")
def api_panic():
    _panic()
    return '', 204


@app.get("/restart")
def api_restart():
    _restart()
    return '', 204


''' Websockets event routes '''


def mididings_context_update():
    live_context.set_dirty(False)
    socketio.emit('mididings_context_update',
                  live_context.scene_context.payload)


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(osc_observer_thread)


@socketio.event
def sio_get_mididings_context():
    mididings_context_update()


@socketio.event
def sio_switch_scene(data):
    _switch_scene(int(data['id']))


@socketio.event
def sio_switch_subscene(data):
    _switch_subscene(int(data['id']))


@socketio.event
def sio_next_scene():
    _next_scene()


@socketio.event
def sio_prev_scene():
    _prev_scene()


@socketio.event
def sio_prev_subscene():
    _prev_subscene()


@socketio.event
def sio_next_subscene():
    _next_subscene()


@socketio.event
def sio_restart():
    _restart()


@socketio.event
def sio_panic():
    _panic()


@socketio.event
def sio_query():
    _query()


@socketio.event
def sio_quit():
    _quit()
    socketio.emit("on_terminate")


''' Mididings  '''


def osc_observer_thread():
    while True:
        if live_context.is_dirty():
            mididings_context_update()
        socketio.emit("on_start") if live_context.is_running(
        ) else socketio.emit("on_exit")
        socketio.sleep(0.125)


''' API calls  '''


def _quit():
    live_context.quit()


def _panic():
    live_context.panic()


def _query():
    live_context.query()


def _restart():
    live_context.restart()


def _next_subscene():
    live_context.next_subscene()


def _next_scene():
    live_context.next_scene()


def _prev_subscene():
    live_context.prev_subscene()


def _prev_scene():
    live_context.prev_scene()


def _switch_scene(id):
    live_context.switch_scene(id)


def _switch_subscene(id):
    live_context.switch_subscene(id)


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
    socketio.run(app, host=configuration["host"], port=configuration["port"])
