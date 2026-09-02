from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app import db
from app.models import Category

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

@categories_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_type = request.form.get('type', '').lower()
        if not name or category_type not in {'income', 'expense'}:
            flash('Enter a name and choose a valid category type.', 'error')
        elif db.session.query(Category).filter_by(user_id=current_user.id, name=name, type=category_type).first():
            flash('That category already exists.', 'error')
        else:
            db.session.add(Category(user_id=current_user.id, name=name, type=category_type))
            db.session.commit()
            flash('Category created.', 'success')
            return redirect(url_for('categories.index'))
    categories = db.session.query(Category).filter((Category.user_id == current_user.id) | (Category.user_id.is_(None))).order_by(Category.type, Category.name).all()
    return render_template('categories/index.html', categories=categories)
