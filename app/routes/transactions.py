from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import select

from app import db
from app.models import Category, Transaction

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')


def _categories(transaction_type):
    return db.session.scalars(select(Category).where(
        (Category.user_id == current_user.id) | (Category.user_id.is_(None)),
        Category.type == transaction_type).order_by(Category.name)).all()


def _save_transaction(transaction=None):
    transaction_type = request.form.get('type', '').lower()
    try:
        amount = Decimal(request.form.get('amount', '0'))
        transaction_date = date.fromisoformat(request.form.get('date', ''))
        category_id = int(request.form.get('category_id', '0'))
    except (InvalidOperation, ValueError):
        flash('Enter a valid amount, date, and category.', 'error')
        return False
    category = db.session.scalar(select(Category).where(
        Category.id == category_id,
        (Category.user_id == current_user.id) | (Category.user_id.is_(None)),
        Category.type == transaction_type))
    if transaction_type not in {'income', 'expense'} or amount <= 0 or category is None:
        flash('Please provide valid transaction details.', 'error')
        return False
    values = dict(type=transaction_type, amount=amount, category_id=category.id,
                  description=request.form.get('description', '').strip(),
                  payment_method=request.form.get('payment_method', '').strip(),
                  date=transaction_date, notes=request.form.get('notes', '').strip())
    if not values['description'] or not values['payment_method']:
        flash('Description and payment method are required.', 'error')
        return False
    if transaction is None:
        transaction = Transaction(user_id=current_user.id, **values)
        db.session.add(transaction)
    else:
        for key, value in values.items():
            setattr(transaction, key, value)
    db.session.commit()
    return True


@transactions_bp.route('/')
@login_required
def index():
    query = select(Transaction).where(Transaction.user_id == current_user.id)
    search = request.args.get('search', '').strip()
    transaction_type = request.args.get('type', '').lower()
    if search:
        query = query.join(Category).where((Transaction.description.ilike(f'%{search}%')) | (Category.name.ilike(f'%{search}%')) | (Transaction.payment_method.ilike(f'%{search}%')))
    if transaction_type in {'income', 'expense'}:
        query = query.where(Transaction.type == transaction_type)
    sort = request.args.get('sort', 'newest')
    query = query.order_by(Transaction.amount.asc() if sort == 'lowest' else Transaction.amount.desc() if sort == 'highest' else Transaction.date.asc() if sort == 'oldest' else Transaction.date.desc())
    return render_template('transactions/index.html', transactions=db.session.scalars(query).all())


@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST' and _save_transaction():
        flash('Transaction added successfully.', 'success')
        return redirect(url_for('transactions.index'))
    return render_template('transactions/form.html', categories=_categories(request.form.get('type', 'expense').lower() or 'expense'), transaction=None, today=date.today())


@transactions_bp.route('/<int:transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(transaction_id):
    transaction = db.session.scalar(select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == current_user.id))
    if transaction is None:
        return render_template('errors/404.html'), 404
    if request.method == 'POST' and _save_transaction(transaction):
        flash('Transaction updated successfully.', 'success')
        return redirect(url_for('transactions.index'))
    return render_template('transactions/form.html', categories=_categories(transaction.type), transaction=transaction, today=date.today())


@transactions_bp.post('/<int:transaction_id>/delete')
@login_required
def delete(transaction_id):
    transaction = db.session.scalar(select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == current_user.id))
    if transaction is None:
        return render_template('errors/404.html'), 404
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted.', 'success')
    return redirect(url_for('transactions.index'))