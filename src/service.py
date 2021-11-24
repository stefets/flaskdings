#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_socketio import SocketIO
from frontend.views import ui_blueprint
from osc.server import MididingsContext
import os
import json
import jinja2
from time import sleep

''' Flask '''
from flask import Flask, redirect, url_for, render_template, jsonify, request, make_response
from werkzeug.exceptions import HTTPException
from werkzeug.utils import import_string

''' Websockets '''

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
socketio = SocketIO(app)


# Configuration
filename = os.path.join(app.static_folder, 'config.json')
with open(filename) as FILE:
    configuration = json.load(FILE)

livedings = None
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    livedings = MididingsContext(configuration["osc_server"])


# BLUEPRINT
app.config['livedings'] = livedings
app.register_blueprint(ui_blueprint)
#

'''
    Api routes
'''


@app.route("/")
@app.route("/api")
def index():
    return render_template('index.html')


'''
    Websockets routes
'''


@socketio.event
def switch_scene(data):
    update_ui(livedings.switch_scene, int(data['id']))


@socketio.event
def switch_subscene(data):
    update_ui(livedings.switch_subscene, int(data['id']))


@socketio.event
def next_scene():
    update_ui(livedings.next_scene)


@socketio.event
def prev_scene():
    update_ui(livedings.prev_scene)


@socketio.event
def prev_subscene():
    update_ui(livedings.prev_subscene)


@socketio.event
def next_subscene():
    update_ui(livedings.next_subscene)


@socketio.event
def restart():
    update_ui(livedings.restart)


@socketio.event
def panic():
    update_ui(livedings.panic)


@socketio.event
def quit():
    update_ui(livedings.quit)


def update_ui(action, action_value=None):

    livedings()  # Set the ready flag to False TODO REWORKS

    action(action_value) if action_value else action()

    ''' TODO REWORKS '''
    timeout = 0
    while not livedings.ready:
        sleep(0.0625)
        timeout += 1
        if timeout % 32 == 0:
            break

    ''' WIP '''
    socketio.emit('mididings.update', {
                  'current_scene': livedings.current_scene,
                  'current_subscene': livedings.current_subscene,
                  'scenes': livedings.scenes})


@app.route("/api/help")
def help():
    """
    API Home
    """
    routes = []
    for rule in app.url_map.iter_rules():
        try:
            if rule.endpoint != 'static':
                if hasattr(app.view_functions[rule.endpoint], 'import_name'):
                    import_name = app.view_functions[rule.endpoint].import_name
                    obj = import_string(import_name)
                    routes.append({rule.rule: "%s\n%s" %
                                  (",".join(list(rule.methods)), obj.__doc__)})
                else:
                    routes.append(
                        {rule.rule: app.view_functions[rule.endpoint].__doc__})
        except Exception as exc:
            routes.append({rule.rule:
                           "(%s) INVALID ROUTE DEFINITION!!!" % rule.endpoint})
            route_info = "%s => %s" % (rule.rule, rule.endpoint)
            app.logger.error("Invalid route: %s" % route_info, exc_info=True)
            # func_list[rule.rule] = obj.__doc__

    return jsonify(code=200, data=routes)


@app.route("/api/ping")
def ping():
    return '', 204


'''
Jinja2 Filters
This filter serve the API to determine if we render a view
'''


def inject_endpoint(param):
    return param + request.endpoint


jinja2.filters.FILTERS['inject_endpoint'] = inject_endpoint

'''
Errors
'''


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
