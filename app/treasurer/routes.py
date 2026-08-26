from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.treasurer import bp
from app import db
from app.user import User
from app.level import AccessLevel
from app.models.treasurer import TreasurerRecord

def can_manage_treasurer():
    return current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN', 'TREASURER']

def is_admin_or_dev():
    return current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN']

@bp.route('/')
@login_required
def index():
    if not can_manage_treasurer():
        flash('You do not have permission to view treasurer records.', 'danger')
        return redirect(url_for('home.home'))
    
    search = request.args.get('search', '')
    record_type = request.args.get('record_type', '')
    category = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    query = TreasurerRecord.query
    
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                TreasurerRecord.description.ilike(like),
                TreasurerRecord.reference.ilike(like),
                TreasurerRecord.category.ilike(like)
            )
        )
    
    if record_type:
        query = query.filter(TreasurerRecord.record_type == record_type)
    
    if category:
        query = query.filter(TreasurerRecord.category == category)
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(TreasurerRecord.transaction_date >= from_date)
        except (ValueError, TypeError):
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(TreasurerRecord.transaction_date <= to_date)
        except (ValueError, TypeError):
            pass
    
    records = query.order_by(TreasurerRecord.transaction_date.desc()).all()
    
    # Summary
    total_income = db.session.query(db.func.sum(TreasurerRecord.amount)).filter(
        TreasurerRecord.record_type == 'Income'
    ).scalar() or 0
    
    total_expenses = db.session.query(db.func.sum(TreasurerRecord.amount)).filter(
        TreasurerRecord.record_type == 'Expense'
    ).scalar() or 0
    
    balance = total_income - total_expenses
    
    return render_template('treasurer/index.html', 
                         records=records, 
                         search=search,
                         record_type=record_type,
                         category=category,
                         date_from=date_from,
                         date_to=date_to,
                         total_income=total_income,
                         total_expenses=total_expenses,
                         balance=balance)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not can_manage_treasurer():
        flash('You do not have permission to create treasurer records.', 'danger')
        return redirect(url_for('treasurer.index'))
    
    if request.method == 'POST':
        record_type = request.form.get('record_type', 'Transaction').strip()
        category = request.form.get('category', '').strip()
        amount = request.form.get('amount', 0, type=int)
        description = request.form.get('description', '').strip()
        reference = request.form.get('reference', '').strip()
        transaction_date_str = request.form.get('transaction_date', '')
        
        if not category or not transaction_date_str:
            flash('Category and transaction date are required.', 'danger')
            return redirect(url_for('treasurer.create'))
        
        try:
            transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('treasurer.create'))
        
        record = TreasurerRecord(
            record_type=record_type,
            category=category,
            amount=amount,
            description=description,
            reference=reference,
            transaction_date=transaction_date,
            created_by=current_user.id
        )
        db.session.add(record)
        db.session.commit()
        flash('Treasurer record created successfully.', 'success')
        return redirect(url_for('treasurer.index'))
    
    return render_template('treasurer/create.html')


@bp.route('/<int:record_id>')
@login_required
def view(record_id):
    if not can_manage_treasurer():
        flash('You do not have permission to view treasurer records.', 'danger')
        return redirect(url_for('treasurer.index'))
    
    record = TreasurerRecord.query.get_or_404(record_id)
    return render_template('treasurer/view.html', record=record)


@bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(record_id):
    if not can_manage_treasurer():
        flash('You do not have permission to edit treasurer records.', 'danger')
        return redirect(url_for('treasurer.index'))
    
    record = TreasurerRecord.query.get_or_404(record_id)
    
    if request.method == 'POST':
        record.record_type = request.form.get('record_type', 'Transaction').strip()
        record.category = request.form.get('category', '').strip()
        record.amount = request.form.get('amount', 0, type=int)
        record.description = request.form.get('description', '').strip()
        record.reference = request.form.get('reference', '').strip()
        transaction_date_str = request.form.get('transaction_date', '')
        
        try:
            record.transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('treasurer.edit', record_id=record_id))
        
        db.session.commit()
        flash('Treasurer record updated successfully.', 'success')
        return redirect(url_for('treasurer.view', record_id=record.id))
    
    return render_template('treasurer/edit.html', record=record)


@bp.route('/<int:record_id>/delete', methods=['POST'])
@login_required
def delete(record_id):
    if not is_admin_or_dev():
        flash('You do not have permission to delete treasurer records.', 'danger')
        return redirect(url_for('treasurer.index'))
    
    record = TreasurerRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash('Treasurer record deleted successfully.', 'success')
    return redirect(url_for('treasurer.index'))
