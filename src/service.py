#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from threading import Lock
from flask_socketio import SocketIO
from frontend.views import ui_blueprint
from osc.server import MididingsContext
import os
import json
from flask.signals import Namespace
from flask import Flask, render_template
from werkzeug.exceptions import HTTPException


''' Flask '''

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

''' Signal from the OSC thread '''

namespace = Namespace()
osc_server_signal = namespace.signal('osc_server')


''' Websockets context '''

socketio = SocketIO(app, logger=app.debug, engineio_logger=app.debug)
thread = None
thread_lock = Lock()

''' Mididings context '''

livedings = None
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    livedings = MididingsContext(
        configuration["osc_server"], osc_server_signal)


"""  Bluebrint(s) """

app.config['livedings'] = livedings
app.register_blueprint(ui_blueprint)


'''
    Api routes
'''


@app.route("/")
@app.route("/api")
@app.route("/home")
@app.route("/index")
def index():
    return render_template('index.html')


@app.route("/api/next_scene")
def api_next_scene():
    _next_scene()
    return '', 204


@app.route("/api/prev_scene")
def api_prev_scene():
    _prev_scene()
    return '', 204


@app.route("/api/next_subscene")
def api_next_subscene():
    _next_subscene()
    return '', 204


@app.route("/api/prev_subscene")
def api_prev_subscene():
    _prev_subscene()
    return '', 204


@app.route("/api/switch_scene/<int:id>")
def api_switch_scene(id):
    _switch_scene(id)
    return '', 204


@app.route("/api/switch_subscene/<int:id>")
def api_switch_subscene(id):
    _switch_subscene(id)
    return '', 204


@app.route("/api/quit")
def api_quit():
    _quit()
    return '', 204


@app.route("/api/panic")
def api_panic():
    _panic()
    return '', 204


@app.route("/api/restart")
def api_restart():
    _restart()
    return '', 204


''' Websockets event routes '''


def emit_mididings_context():
    socketio.emit('mididings_context_update', {
                  'current_scene': livedings.current_scene,
                  'current_subscene': livedings.current_subscene,
                  'scenes': livedings.scenes})


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(osc_observer_thread)


@socketio.event
def sio_get_mididings_context():
    emit_mididings_context()


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
def sio_quit():
    _quit()
    socketio.emit("application_shutdown")



''' Mididings  '''

''' OSC server signals '''

@osc_server_signal.connect
def mididings_context_changed(sender, **kwargs):
    livedings.dirty = kwargs.get('refresh', False)

def osc_observer_thread():
    while True:
        socketio.sleep(0.125)
        if livedings.dirty:
            emit_mididings_context()
            livedings.dirty = False

''' OSC controls '''

def _quit():
    livedings.quit()


def _panic():
    livedings.panic()


def _restart():
    livedings.restart()


def _next_subscene():
    livedings.next_subscene()


def _next_scene():
    livedings.next_scene()


def _prev_subscene():
    livedings.prev_subscene()


def _prev_scene():
    livedings.prev_scene()


def _switch_scene(id):
    livedings.switch_scene(id)


def _switch_subscene(id):
    livedings.switch_subscene(id)


'''
Error Handling
'''


@socketio.on_error()
def error_handler(e):
    print("socketio.on_error")


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
    socketio.run(app, host='0.0.0.0', port=5555)
