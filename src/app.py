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
from services.dings import OscContext


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

''' Mididings OSC context '''
dings_context = None
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    dings_context = OscContext(
        configuration["osc_server"])


"""  Bluebrint(s) """
app.config['dings_context'] = dings_context
app.register_blueprint(frontend)


'''
    Api routes
'''


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/next_scene")
def api_next_scene():
    _next_scene()
    return '', 204


@app.route("/prev_scene")
def api_prev_scene():
    _prev_scene()
    return '', 204


@app.route("/next_subscene")
def api_next_subscene():
    _next_subscene()
    return '', 204


@app.route("/prev_subscene")
def api_prev_subscene():
    _prev_subscene()
    return '', 204


@app.route("/switch_scene/<int:id>")
def api_switch_scene(id):
    _switch_scene(id)
    return '', 204


@app.route("/switch_subscene/<int:id>")
def api_switch_subscene(id):
    _switch_subscene(id)
    return '', 204


@app.route("/quit")
def api_quit():
    _quit()
    return '', 204


@app.route("/panic")
def api_panic():
    _panic()
    return '', 204


@app.route("/restart")
def api_restart():
    _restart()
    return '', 204


''' Websockets event routes '''


def mididings_context_update():
    dings_context.dirty = False
    socketio.emit('mididings_context_update', {
                  'current_scene': dings_context.current_scene,
                  'current_subscene': dings_context.current_subscene,
                  'scenes': dings_context.scenes,
                  "scene_name" : dings_context.scene_name,
                  "subscene_name" : dings_context.subscene_name,
                  "has_subscene" : dings_context.has_subscene
                  })


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
        if dings_context.dirty:
            mididings_context_update()
        socketio.emit("on_start") if dings_context.running else socketio.emit("on_exit")
        socketio.sleep(0.125)


''' API calls  '''

def _quit():
    dings_context.quit()


def _panic():
    dings_context.panic()


def _query():
    dings_context.query()


def _restart():
    dings_context.restart()


def _next_subscene():
    dings_context.next_subscene()


def _next_scene():
    dings_context.next_scene()


def _prev_subscene():
    dings_context.prev_subscene()


def _prev_scene():
    dings_context.prev_scene()


def _switch_scene(id):
    dings_context.switch_scene(id)


def _switch_subscene(id):
    dings_context.switch_subscene(id)


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
