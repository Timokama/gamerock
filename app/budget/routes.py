from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.budget import bp
from app import db
from app.user import User
from app.level import AccessLevel
from app.models.budget import Budget, BudgetItem

def is_admin_or_dev():
    return current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN']

@bp.route('/')
@login_required
def index():
    if not is_admin_or_dev():
        flash('You do not have permission to manage budgets.', 'danger')
        return redirect(url_for('home.home'))
    
    search = request.args.get('search', '')
    fiscal_year = request.args.get('fiscal_year', '')
    status = request.args.get('status', '')
    
    query = Budget.query
    
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Budget.name.ilike(like),
                Budget.description.ilike(like)
            )
        )
    
    if fiscal_year:
        query = query.filter(Budget.fiscal_year == fiscal_year)
    
    if status:
        query = query.filter(Budget.status == status)
    
    budgets = query.order_by(Budget.created_at.desc()).all()
    return render_template('budget/index.html', budgets=budgets, search=search, fiscal_year=fiscal_year, status=status)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not is_admin_or_dev():
        flash('You do not have permission to create budgets.', 'danger')
        return redirect(url_for('budget.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        fiscal_year = request.form.get('fiscal_year', '').strip()
        total_amount = request.form.get('total_amount', 0, type=int)
        
        if not name or not fiscal_year:
            flash('Budget name and fiscal year are required.', 'danger')
            return redirect(url_for('budget.create'))
        
        budget = Budget(
            name=name,
            description=description,
            fiscal_year=fiscal_year,
            total_amount=total_amount,
            created_by=current_user.id
        )
        db.session.add(budget)
        db.session.flush()
        
        categories = request.form.getlist('category[]')
        amounts = request.form.getlist('amount[]')
        descriptions = request.form.getlist('item_description[]')
        item_types = request.form.getlist('item_type[]')
        
        for i, category in enumerate(categories):
            if category and i < len(amounts):
                amount = int(amounts[i]) if amounts[i] else 0
                item = BudgetItem(
                    budget_id=budget.id,
                    category=category,
                    description=descriptions[i] if i < len(descriptions) else '',
                    amount=amount,
                    item_type=item_types[i] if i < len(item_types) else 'Expense'
                )
                db.session.add(item)
        
        db.session.commit()
        flash('Budget created successfully.', 'success')
        return redirect(url_for('budget.index'))
    
    return render_template('budget/create.html')


@bp.route('/<int:budget_id>')
@login_required
def view(budget_id):
    if not is_admin_or_dev():
        flash('You do not have permission to view budgets.', 'danger')
        return redirect(url_for('budget.index'))
    
    budget = Budget.query.get_or_404(budget_id)
    return render_template('budget/view.html', budget=budget)


@bp.route('/<int:budget_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(budget_id):
    if not is_admin_or_dev():
        flash('You do not have permission to edit budgets.', 'danger')
        return redirect(url_for('budget.index'))
    
    budget = Budget.query.get_or_404(budget_id)
    
    if request.method == 'POST':
        budget.name = request.form.get('name', '').strip()
        budget.description = request.form.get('description', '').strip()
        budget.fiscal_year = request.form.get('fiscal_year', '').strip()
        budget.total_amount = request.form.get('total_amount', 0, type=int)
        budget.status = request.form.get('status', 'Draft')
        
        if request.form.get('status') == 'Approved' and not budget.approved_by:
            budget.approved_by = current_user.id
            budget.approved_at = datetime.utcnow()
        
        BudgetItem.query.filter_by(budget_id=budget.id).delete()
        
        categories = request.form.getlist('category[]')
        amounts = request.form.getlist('amount[]')
        descriptions = request.form.getlist('item_description[]')
        item_types = request.form.getlist('item_type[]')
        
        for i, category in enumerate(categories):
            if category and i < len(amounts):
                amount = int(amounts[i]) if amounts[i] else 0
                item = BudgetItem(
                    budget_id=budget.id,
                    category=category,
                    description=descriptions[i] if i < len(descriptions) else '',
                    amount=amount,
                    item_type=item_types[i] if i < len(item_types) else 'Expense'
                )
                db.session.add(item)
        
        db.session.commit()
        flash('Budget updated successfully.', 'success')
        return redirect(url_for('budget.view', budget_id=budget.id))
    
    return render_template('budget/edit.html', budget=budget)


@bp.route('/<int:budget_id>/delete', methods=['POST'])
@login_required
def delete(budget_id):
    if not is_admin_or_dev():
        flash('You do not have permission to delete budgets.', 'danger')
        return redirect(url_for('budget.index'))
    
    budget = Budget.query.get_or_404(budget_id)
    db.session.delete(budget)
    db.session.commit()
    flash('Budget deleted successfully.', 'success')
    return redirect(url_for('budget.index'))
