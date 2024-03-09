#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later


from flask import Blueprint, render_template, current_app


_presenter = Blueprint('frontend', __name__, template_folder='templates', url_prefix='/ui')


@_presenter.route("/")
def index():
    context = current_app.config['live_context']
    return render_template('ui.html') if context.scenes else render_template('no_context.html')
