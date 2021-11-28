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


''' Websockets '''
socketio = SocketIO(app, logger=app.debug, engineio_logger=app.debug)
thread = None
thread_lock = Lock()


def osc_observer_thread():
    while True:
        socketio.sleep(0.125)
        if livedings.dirty:
            emit_mididings_context()
            livedings.dirty = False


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


''' OSC server signals '''


@osc_server_signal.connect
def mididings_context_changed(sender, **kwargs):
    livedings.dirty = kwargs.get('refresh', False)


''' Websockets calls '''


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(osc_observer_thread)


def emit_mididings_context():
    socketio.emit('mididings_context_update', {
                  'current_scene': livedings.current_scene,
                  'current_subscene': livedings.current_subscene,
                  'scenes': livedings.scenes})


@socketio.event
def get_mididings_context():
    emit_mididings_context()


@socketio.event
def switch_scene(data):
    livedings.switch_scene(int(data['id']))


@socketio.event
def switch_subscene(data):
    livedings.switch_subscene(int(data['id']))


@socketio.event
def next_scene():
    livedings.next_scene()


@socketio.event
def prev_scene():
    livedings.prev_scene()


@socketio.event
def prev_subscene():
    livedings.prev_subscene()


@socketio.event
def next_subscene():
    livedings.next_subscene()


@socketio.event
def restart():
    livedings.restart()


@socketio.event
def panic():
    livedings.panic()


@socketio.event
def quit():
    livedings.quit()
    socketio.emit("application_shutdown")


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
