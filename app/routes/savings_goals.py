from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import select

from app import db
from app.models import SavingsGoal

savings_goals_bp = Blueprint('savings_goals', __name__, url_prefix='/savings-goals')


def _decimal(value, default=None):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return default


def _goal_from_form(goal=None):
    name = request.form.get('name', '').strip()
    target = _decimal(request.form.get('target_amount'))
    current = _decimal(request.form.get('current_amount'), Decimal('0'))
    deadline_value = request.form.get('deadline', '').strip()
    try:
        deadline = date.fromisoformat(deadline_value) if deadline_value else None
    except ValueError:
        deadline = None
    if not name or target is None or target <= 0 or current is None or current < 0 or current > target:
        flash('Enter a name, a positive target, and saved money between zero and the target.', 'error')
        return False
    if deadline_value and deadline is None:
        flash('Enter a valid deadline date.', 'error')
        return False
    values = {'name': name, 'target_amount': target, 'current_amount': current, 'deadline': deadline}
    if goal is None:
        db.session.add(SavingsGoal(user_id=current_user.id, **values))
    else:
        for key, value in values.items():
            setattr(goal, key, value)
    db.session.commit()
    return True


def _owned_goal(goal_id):
    return db.session.scalar(select(SavingsGoal).where(
        SavingsGoal.id == goal_id, SavingsGoal.user_id == current_user.id))


@savings_goals_bp.route('/')
@login_required
def index():
    goals = db.session.scalars(select(SavingsGoal).where(
        SavingsGoal.user_id == current_user.id).order_by(SavingsGoal.created_at.desc())).all()
    return render_template('savings_goals/index.html', goals=goals, today=date.today())


@savings_goals_bp.route('/add', methods=['POST'])
@login_required
def add():
    if _goal_from_form():
        flash('Savings goal created.', 'success')
    return redirect(url_for('savings_goals.index'))


@savings_goals_bp.route('/<int:goal_id>/edit', methods=['POST'])
@login_required
def edit(goal_id):
    goal = _owned_goal(goal_id)
    if goal is None:
        return render_template('errors/404.html'), 404
    if _goal_from_form(goal):
        flash('Savings goal updated.', 'success')
    return redirect(url_for('savings_goals.index'))


@savings_goals_bp.post('/<int:goal_id>/add-money')
@login_required
def add_money(goal_id):
    goal = _owned_goal(goal_id)
    amount = _decimal(request.form.get('amount'))
    if goal is None:
        return render_template('errors/404.html'), 404
    if amount is None or amount <= 0 or goal.current_amount + amount > goal.target_amount:
        flash('Enter a positive amount that does not exceed the remaining goal.', 'error')
    else:
        goal.current_amount += amount
        db.session.commit()
        flash('Savings progress updated.', 'success')
    return redirect(url_for('savings_goals.index'))


@savings_goals_bp.post('/<int:goal_id>/delete')
@login_required
def delete(goal_id):
    goal = _owned_goal(goal_id)
    if goal is None:
        return render_template('errors/404.html'), 404
    db.session.delete(goal)
    db.session.commit()
    flash('Savings goal deleted.', 'success')
    return redirect(url_for('savings_goals.index'))