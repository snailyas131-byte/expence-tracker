import os
import secrets
from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from config import config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)
    selected_config = config_name or os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config.get(selected_config, config['default']))
    if not app.config.get('SECRET_KEY'):
        if selected_config == 'production':
            raise RuntimeError('SECRET_KEY must be set in production.')
        app.config['SECRET_KEY'] = secrets.token_hex(32)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models import User, Category, Transaction, Budget, SavingsGoal
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.transactions import transactions_bp
    from app.routes.categories import categories_bp
    from app.routes.budgets import budgets_bp
    from app.routes.reports import reports_bp
    from app.routes.settings import settings_bp
    from app.routes.savings_goals import savings_goals_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(savings_goals_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    with app.app_context():
        db.create_all()
        if not db.session.query(Category).filter(Category.user_id.is_(None)).first():
            defaults = {
                'expense': ['Food', 'Shopping', 'Transport', 'Bills', 'Education', 'Entertainment', 'Health', 'Rent', 'Travel', 'Other'],
                'income': ['Salary', 'Freelance', 'Business', 'Gift', 'Investment', 'Other'],
            }
            for category_type, names in defaults.items():
                db.session.add_all(Category(name=name, type=category_type) for name in names)
            db.session.commit()

    return app
