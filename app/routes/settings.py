from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app import db

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        theme = request.form.get('theme', 'light')
        if not name or theme not in {'light', 'dark'}:
            flash('Please provide a valid name and theme.', 'error')
        else:
            current_user.name, current_user.theme = name, theme
            db.session.commit()
            flash('Settings updated.', 'success')
            return redirect(url_for('settings.index'))
    return render_template('settings/index.html')
