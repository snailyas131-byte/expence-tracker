from app import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(10), nullable=False)

    user = db.relationship('User', back_populates='categories')
    transactions = db.relationship('Transaction', back_populates='category')
    budgets = db.relationship('Budget', back_populates='category')

    __table_args__ = (db.UniqueConstraint('user_id', 'name', 'type', name='uq_category_owner_name_type'),)
