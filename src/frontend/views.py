from flask import Blueprint, render_template, current_app
from time import sleep

ui_blueprint = Blueprint('ui_blueprint', __name__,
                         template_folder='templates',
                         url_prefix='/ui')


@ui_blueprint.route("/")
def index():
    if current_app.config['livedings'].scenes:
        # We are here after an OSC process, wait a little before rendering
        sleep(0.0625)
        return render_template('ui.html', config=current_app.config['livedings'], parameter="?view=")
    else:
        return render_template('nodings.html')
