from datetime import date, timedelta

from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import func, select

from app import db
from app.models import Category, Transaction

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return dashboard()
    return render_template('landing.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    income = db.session.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == current_user.id, Transaction.type == 'income')) or 0
    expenses = db.session.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == current_user.id, Transaction.type == 'expense')) or 0
    monthly_filter = (Transaction.user_id == current_user.id,
                      func.extract('month', Transaction.date) == today.month,
                      func.extract('year', Transaction.date) == today.year)
    monthly_income = db.session.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        *monthly_filter, Transaction.type == 'income')) or 0
    monthly_expenses = db.session.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        *monthly_filter, Transaction.type == 'expense')) or 0
    recent_transactions = db.session.scalars(select(Transaction).where(
        Transaction.user_id == current_user.id).order_by(Transaction.date.desc(), Transaction.created_at.desc()).limit(6)).all()
    category_rows = db.session.execute(select(Category.name, func.sum(Transaction.amount)).join(
        Transaction, Transaction.category_id == Category.id).where(
        Transaction.user_id == current_user.id, Transaction.type == 'expense').group_by(Category.name)).all()
    month_labels, month_income, month_expenses = [], [], []
    for offset in range(5, -1, -1):
        month_number = today.month - offset
        year = today.year + (month_number - 1) // 12
        month = (month_number - 1) % 12 + 1
        month_labels.append(date(year, month, 1).strftime('%b %Y'))
        period = (Transaction.user_id == current_user.id,
                  func.extract('month', Transaction.date) == month,
                  func.extract('year', Transaction.date) == year)
        month_income.append(float(db.session.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(*period, Transaction.type == 'income')) or 0))
        month_expenses.append(float(db.session.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(*period, Transaction.type == 'expense')) or 0))
    trend_labels = [(today - timedelta(days=offset)).strftime('%d %b') for offset in range(13, -1, -1)]
    trend_values = []
    for offset in range(13, -1, -1):
        trend_day = today - timedelta(days=offset)
        trend_values.append(float(db.session.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == current_user.id, Transaction.type == 'expense', Transaction.date == trend_day)) or 0))
    return render_template('dashboard/index.html', income=income, expenses=expenses,
                           balance=income - expenses, savings=monthly_income - monthly_expenses,
                           recent_transactions=recent_transactions,
                           category_labels=[row[0] for row in category_rows],
                           category_values=[float(row[1]) for row in category_rows],
                           month_labels=month_labels, month_income=month_income,
                           month_expenses=month_expenses, trend_labels=trend_labels,
                           trend_values=trend_values)
