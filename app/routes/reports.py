import csv
from io import StringIO
from flask import Blueprint, Response, render_template
from flask_login import current_user, login_required
from sqlalchemy import select
from app import db
from app.models import Transaction

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    transactions = db.session.scalars(select(Transaction).where(Transaction.user_id == current_user.id).order_by(Transaction.date.desc())).all()
    return render_template('reports/index.html', transactions=transactions)

@reports_bp.route('/export.csv')
@login_required
def export_csv():
    transactions = db.session.scalars(select(Transaction).where(Transaction.user_id == current_user.id).order_by(Transaction.date.desc())).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Category', 'Description', 'Payment Method', 'Amount', 'Notes'])
    writer.writerows([t.date, t.type, t.category.name, t.description, t.payment_method, t.amount, t.notes or ''] for t in transactions)
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=transactions.csv'})
