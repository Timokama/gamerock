from app import db
from sqlalchemy.sql import func

class Budget(db.Model):
    __tablename__ = 'budget'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    fiscal_year = db.Column(db.String(10), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='Draft')
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    creator = db.relationship('User', foreign_keys=[created_by], backref='created_budgets')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_budgets')
    items = db.relationship('BudgetItem', backref='budget', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<Budget {self.name} ({self.fiscal_year})>'


class BudgetItem(db.Model):
    __tablename__ = 'budget_item'
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.String(20), nullable=False, default='Expense')

    def __repr__(self):
        return f'<BudgetItem {self.category}: {self.amount}>'
