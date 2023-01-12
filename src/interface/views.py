# SPDX-License-Identifier: GPL-2.0-or-later

from flask import Blueprint, render_template, current_app

ui_blueprint = Blueprint('ui_blueprint', __name__,
                         template_folder='templates',
                         url_prefix='/ui')


@ui_blueprint.route("/")
def index():
    ld = current_app.config['livedings']
    return render_template('ui.html') if ld.scenes else render_template('no_ui.html')
