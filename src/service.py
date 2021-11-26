#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' PRODUCTION '''
#import eventlet
# eventlet.monkey_patch()

from werkzeug.exceptions import HTTPException
from flask import Flask, render_template
from flask.signals import Namespace
import json
import os
from osc.server import MididingsContext
from frontend.views import ui_blueprint
from flask_socketio import SocketIO

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


''' Flask '''

app = Flask(__name__)

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
socketio = SocketIO(app, logger=True, engineio_logger=True)


def initialize_observer(socket, dings, observable_path):

    class Handler(FileSystemEventHandler):
        def __init__(self, socket, dings):
            super().__init__()
            self.socket = socket
            self.dings = dings

        def on_modified(self, event):
            print([self.on_modified, self, event])
            self.socket.emit('mididings_context_update', {
                'current_scene': self.dings.current_scene,
                'current_subscene': self.dings.current_subscene,
                'scenes': self.dings.scenes})

    observer = Observer()
    observer.schedule(Handler(socket, dings),
                      path=observable_path, recursive=False)
    observer.start()


livedings = None
inotify_path = None
inotify_file = None
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    livedings = MididingsContext(
        configuration["osc_server"], osc_server_signal)

    inotify_path = Path(configuration["watchdog"])
    inotify_file = Path(configuration["watchdog"]).joinpath(configuration["watchdog_file"])
    inotify_path.mkdir(parents=True, exist_ok=True)
    initialize_observer(socketio, livedings, inotify_path)


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
def osc_emit_mididings_context(sender):
    inotify_file.touch(exist_ok=True)


''' Websockets calls '''


@socketio.event
def get_mididings_context():
    inotify_file.touch(exist_ok=True)


@socketio.event
def switch_scene(data):
    livedings.switch_scene(int(data['id']))


@socketio.event
def switch_subscene(data):
    livedings.switch_subscene(int(data['id']))


@socketio.event
def next_scene():
    livedings.next_scene()
    emit_mididings_context()


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
