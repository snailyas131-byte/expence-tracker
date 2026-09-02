from datetime import date
from decimal import Decimal, InvalidOperation
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func, select
from app import db
from app.models import Budget, Category, Transaction

budgets_bp = Blueprint('budgets', __name__, url_prefix='/budgets')

@budgets_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    today = date.today()
    if request.method == 'POST':
        try:
            amount = Decimal(request.form.get('amount', '0'))
            month, year = int(request.form.get('month', today.month)), int(request.form.get('year', today.year))
            category_id = request.form.get('category_id') or None
            category_id = int(category_id) if category_id else None
        except (InvalidOperation, ValueError):
            amount = 0
        if amount <= 0 or not 1 <= month <= 12 or year < 2000:
            flash('Enter a valid positive budget and period.', 'error')
        else:
            existing = db.session.scalar(select(Budget).where(Budget.user_id == current_user.id, Budget.category_id == category_id, Budget.month == month, Budget.year == year))
            if existing:
                existing.amount = amount
            else:
                db.session.add(Budget(user_id=current_user.id, category_id=category_id, amount=amount, month=month, year=year))
            db.session.commit()
            flash('Budget saved.', 'success')
            return redirect(url_for('budgets.index'))
    budgets = db.session.scalars(select(Budget).where(Budget.user_id == current_user.id).order_by(Budget.year.desc(), Budget.month.desc())).all()
    for budget in budgets:
        spent_query = select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == current_user.id, Transaction.type == 'expense', func.extract('month', Transaction.date) == budget.month, func.extract('year', Transaction.date) == budget.year)
        if budget.category_id:
            spent_query = spent_query.where(Transaction.category_id == budget.category_id)
        budget.spent = db.session.scalar(spent_query) or 0
    categories = db.session.scalars(select(Category).where((Category.user_id == current_user.id) | (Category.user_id.is_(None)), Category.type == 'expense')).all()
    return render_template('budgets/index.html', budgets=budgets, categories=categories, today=today)


@budgets_bp.post('/<int:budget_id>/delete')
@login_required
def delete(budget_id):
    budget = db.session.scalar(select(Budget).where(
        Budget.id == budget_id, Budget.user_id == current_user.id))
    if budget is None:
        return render_template('errors/404.html'), 404
    db.session.delete(budget)
    db.session.commit()
    flash('Budget deleted.', 'success')
    return redirect(url_for('budgets.index'))
