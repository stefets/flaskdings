from flask import Blueprint, render_template, current_app
from time import sleep

ui_blueprint = Blueprint('ui_blueprint', __name__,
                         template_folder='templates',
                         url_prefix='/ui')


@ui_blueprint.route("/")
def index():
    timeout = 0
    dings_context = current_app.config['livedings']
    while not dings_context.ready:
        sleep(0.0625) # We are here after an OSC process, wait a little before rendering
        timeout += 1
        if timeout % 32 == 0:
            break
    if dings_context.ready and dings_context.scenes:
        return render_template('ui.html', context=current_app.config['livedings'], parameter="?view=")
    else:
        return render_template('nodings.html')
