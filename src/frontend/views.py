from flask import Blueprint, render_template, current_app

ui_blueprint = Blueprint('ui_blueprint', __name__,
                         template_folder='templates',
                         url_prefix='/ui')


@ui_blueprint.route("/")
def index():
    dings_context = current_app.config['livedings']
    if dings_context.scenes:
        return render_template('ui.html')
    else:
        return render_template('nodings.html')
