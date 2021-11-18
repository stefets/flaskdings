#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import atexit

import liblo
from osc.flaskdings import FlaskDings
from frontend.views import ui_blueprint

from flask import Flask, redirect, url_for, render_template, jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.utils import import_string

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configuration
filename = os.path.join(app.static_folder, 'config.json')
with open(filename) as FILE:
    configuration = json.load(FILE)

livedings = None
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    livedings = FlaskDings(configuration["osc_server"])


# BLUEPRINT
app.config['livedings'] = livedings
app.register_blueprint(ui_blueprint)
#

@app.route("/")
@app.route("/api")
def index():
    return render_template('api.html')


@app.route("/api/mididings/next_scene")
def next_scene():
    livedings.next_scene()
    return ('', 204)
#    return redirect(url_for('ui_blueprint.index'))


@app.route("/api/mididings/prev_scene")
def prev_scene():
    livedings.prev_scene()
    return redirect(url_for('ui_blueprint.index'))


@app.route("/api/mididings/next_subscene")
def next_subscene():
    livedings.next_subscene()
    return redirect(url_for('ui_blueprint.index'))


@app.route("/api/mididings/prev_subscene")
def prev_subscene():
    livedings.prev_subscene()
    return redirect(url_for('ui_blueprint.index'))


@app.route("/api/mididings/panic")
def panic():
    livedings.panic()
    return ('', 204)


@app.route("/api/mididings/scenes/<int:value>")
def switch_scene(value):
    livedings.switch_scene(value)
    return redirect(url_for('ui_blueprint.index'))


@app.route("/api/mididings/subscenes/<int:value>")
def switch_subscene(value):
    livedings.switch_subscene(value)
    return redirect(url_for('ui_blueprint.index'))


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
# Errors


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
    app.run()
