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
    next_scene()
    return '', 204


@app.get("/prev_scene")
def api_prev_scene():
    prev_scene()
    return '', 204


@app.get("/next_subscene")
def api_next_subscene():
    next_subscene()
    return '', 204


@app.get("/prev_subscene")
def api_prev_subscene():
    prev_subscene()
    return '', 204


@app.get("/switch_scene/<int:id>")
def api_switch_scene(id):
    switch_scene(id)
    return '', 204


@app.get("/switch_subscene/<int:id>")
def api_switch_subscene(id):
    switch_subscene(id)
    return '', 204


@app.get("/quit")
def api_quit():
    quit()
    return '', 204


@app.get("/panic")
def api_panic():
    panic()
    return '', 204


@app.get("/restart")
def api_restart():
    restart()
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
    switch_scene(int(data['id']))


@socketio.event
def sio_switch_subscene(data):
    switch_subscene(int(data['id']))


@socketio.event
def sio_next_scene():
    next_scene()


@socketio.event
def sio_prev_scene():
    prev_scene()


@socketio.event
def sio_prev_subscene():
    prev_subscene()


@socketio.event
def sio_next_subscene():
    next_subscene()


@socketio.event
def sio_restart():
    restart()


@socketio.event
def sio_panic():
    panic()


@socketio.event
def sio_query():
    query()


@socketio.event
def sio_quit():
    quit()
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


def quit():
    live_context.quit()


def panic():
    live_context.panic()


def query():
    live_context.query()


def restart():
    live_context.restart()


def next_subscene():
    live_context.next_subscene()


def next_scene():
    live_context.next_scene()


def prev_subscene():
    live_context.prev_subscene()


def prev_scene():
    live_context.prev_scene()


def switch_scene(id):
    live_context.switch_scene(id)


def switch_subscene(id):
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
