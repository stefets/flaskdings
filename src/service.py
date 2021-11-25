#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_socketio import SocketIO
from frontend.views import ui_blueprint
from osc.server import MididingsContext
import os
import json

''' Flask '''
from flask import Flask, render_template, jsonify
from flask.signals import Namespace
from werkzeug.exceptions import HTTPException
from werkzeug.utils import import_string


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

''' Signal '''
namespace = Namespace()
osc_message = namespace.signal('osc_message')


''' Websockets '''
socketio = SocketIO(app)


"""  Configuration """
filename = os.path.join(app.static_folder, 'config.json')
with open(filename) as FILE:
    configuration = json.load(FILE)

"""  OSC Service """
livedings = None
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    livedings = MididingsContext(configuration["osc_server"], osc_message)


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


'''
    Websockets routes
'''


@osc_message.connect
def emit_mididings_context(sender=None):
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
    socketio.run(app)
