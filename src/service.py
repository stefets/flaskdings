#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import liblo
from flaskdings import FlaskDings
from time import sleep

from flask import Flask, redirect, url_for, render_template, make_response, request, jsonify, flash
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configuration
import json
filename = os.path.join(app.static_folder, 'config.json')
with open(filename) as f:
    configuration = json.load(f)

flask_dings = None
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    flask_dings = FlaskDings(configuration["server"])

@app.route("/")
def index():
    return render_template('index.html', config=flask_dings)

@app.route("/mididings/next_scene")
def next_scene():
    flask_dings.osc.next_scene()
    return redirect(url_for('index'))

@app.route("/mididings/prev_scene")
def prev_scene():
    flask_dings.osc.prev_scene()
    return redirect(url_for('index'))

@app.route("/mididings/next_subscene")
def next_subscene():
    flask_dings.osc.next_subscene()
    return redirect(url_for('index'))

@app.route("/mididings/prev_subscene")
def prev_subscene():
    flask_dings.osc.prev_subscene()
    return redirect(url_for('index'))

@app.route("/mididings/panic")
def panic():
    flask_dings.osc.panic()
    return ('', 204)

@app.route("/mididings/scenes/<int:value>")
def switch_scene(value):
    flask_dings.osc.switch_scene(value)
    return redirect(url_for('index'))

@app.route("/mididings/subscenes/<int:value>")
def switch_subscene(value):
    flask_dings.osc.switch_subscene(value)
    return redirect(url_for('index'))

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
