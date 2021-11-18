from flask import Blueprint, render_template, current_app
import json

ui_blueprint = Blueprint('ui_blueprint', __name__,
                            template_folder='templates',
                            url_prefix='/ui')



@ui_blueprint.route("/")
def index():
    if current_app.config['livedings'].scenes:
        return render_template('ui.html', config=current_app.config['livedings'])
    else:
        return render_template('nodings.html')
