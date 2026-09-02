from datetime import datetime, timezone
from decimal import Decimal

from app import db


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship('User', back_populates='transactions')
    category = db.relationship('Category', back_populates='transactions')

    @property
    def signed_amount(self):
        return self.amount if self.type == 'income' else -self.amount

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.amount is not None and Decimal(self.amount) <= 0:
            raise ValueError('Transaction amount must be positive.')
