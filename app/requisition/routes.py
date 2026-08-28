from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.requisition import bp
from app import db
from app.user import User
from app.level import AccessLevel
from app.models.register import Member
from app.models.requisition import Requisition, RequisitionItem

REQUISITION_STATUSES = ['Pending', 'Approved', 'Cancelled']

def can_manage_requisition():
    return current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN', 'CHAIRPERSON']

@bp.route('/')
@login_required
def index():
    user = User.query.get_or_404(current_user.id)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    member_filter = request.args.get('member_id', type=int)

    query = Requisition.query.options(
        db.joinedload(Requisition.member),
        db.joinedload(Requisition.creator)
    )

    if can_manage_requisition():
        if member_filter:
            query = query.filter(Requisition.member_id == member_filter)
    else:
        if not user.member_profile:
            flash('You need a member profile to view requisitions.', 'warning')
            return redirect(url_for('home.home'))
        query = query.filter(Requisition.member_id == user.member_profile.id)

    if search:
        like = f'%{search}%'
        query = query.join(Requisition.items).join(Member).filter(
            db.or_(
                RequisitionItem.item_name.ilike(like),
                db.cast(RequisitionItem.quantity, db.String).ilike(like),
                Member.firstname.ilike(like),
                Member.lastname.ilike(like),
                Member.surname.ilike(like)
            )
        )

    if status_filter:
        if status_filter in REQUISITION_STATUSES:
            query = query.filter(Requisition.status == status_filter)

    requisitions = query.order_by(Requisition.created_at.desc()).all()
    members = Member.query.order_by(Member.firstname).all() if can_manage_requisition() else []

    return render_template(
        'requisition/index.html',
        requisitions=requisitions,
        members=members,
        search=search,
        status_filter=status_filter,
        member_filter=member_filter,
        can_manage=can_manage_requisition(),
        statuses=REQUISITION_STATUSES
    )


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    user = User.query.get_or_404(current_user.id)
    if request.method == 'POST':
        date_taken_str = request.form.get('date_taken', '').strip()
        expected_return_date_str = request.form.get('expected_return_date', '').strip()
        member_id = request.form.get('member_id', type=int)

        item_names = request.form.getlist('item_name[]')
        other_names = request.form.getlist('item_name_other[]')
        quantities = request.form.getlist('quantity[]')

        if not date_taken_str:
            members = Member.query.order_by(Member.firstname).all() if can_manage_requisition() else []
            preselected_member_id = current_user.member_profile.id if current_user.member_profile else None
            return render_template(
                'requisition/create.html',
                members=members,
                preselected_member_id=preselected_member_id,
                can_manage=can_manage_requisition(),
                error='Date taken is required.',
                form_data=request.form
            )

        if not item_names or not any(name.strip() for name in item_names):
            members = Member.query.order_by(Member.firstname).all() if can_manage_requisition() else []
            preselected_member_id = current_user.member_profile.id if current_user.member_profile else None
            return render_template(
                'requisition/create.html',
                members=members,
                preselected_member_id=preselected_member_id,
                can_manage=can_manage_requisition(),
                error='At least one item is required.',
                form_data=request.form
            )

        # Merge "Other" text inputs with selected items
        merged_names = []
        other_idx = 0
        for i, name in enumerate(item_names):
            if name == 'Other':
                other_value = other_names[other_idx].strip() if other_idx < len(other_names) else ''
                if not other_value:
                    members = Member.query.order_by(Member.firstname).all() if can_manage_requisition() else []
                    preselected_member_id = current_user.member_profile.id if current_user.member_profile else None
                    return render_template(
                        'requisition/create.html',
                        members=members,
                        preselected_member_id=preselected_member_id,
                        can_manage=can_manage_requisition(),
                        error='Please specify the item name for the "Other" selection.',
                        form_data=request.form
                    )
                merged_names.append(other_value)
                other_idx += 1
            else:
                merged_names.append(name.strip())

        first_item_name = next((name for name in merged_names if name), None)
        first_quantity = 1
        if first_item_name and quantities:
            try:
                first_quantity = int(quantities[0])
            except (ValueError, TypeError):
                first_quantity = 1

        if not member_id and user.member_profile:
            member_id = user.member_profile.id

        if not member_id:
            flash('You must be linked to a member profile to create a requisition.', 'danger')
            return redirect(url_for('requisition.index'))

        member = Member.query.get(member_id)
        if not member:
            members = Member.query.order_by(Member.firstname).all() if can_manage_requisition() else []
            preselected_member_id = current_user.member_profile.id if current_user.member_profile else None
            return render_template(
                'requisition/create.html',
                members=members,
                preselected_member_id=preselected_member_id,
                can_manage=can_manage_requisition(),
                error='Selected member does not exist.',
                form_data=request.form
            )

        if not can_manage_requisition() and member.id != user.member_profile.id:
            flash('You do not have permission to create requisitions for other members.', 'danger')
            return redirect(url_for('requisition.index'))

        try:
            date_taken = datetime.strptime(date_taken_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            members = Member.query.order_by(Member.firstname).all() if can_manage_requisition() else []
            preselected_member_id = current_user.member_profile.id if current_user.member_profile else None
            return render_template(
                'requisition/create.html',
                members=members,
                preselected_member_id=preselected_member_id,
                can_manage=can_manage_requisition(),
                error='Invalid date taken format.',
                form_data=request.form
            )

        expected_return_date = None
        if expected_return_date_str:
            try:
                expected_return_date = datetime.strptime(expected_return_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                members = Member.query.order_by(Member.firstname).all() if can_manage_requisition() else []
                preselected_member_id = current_user.member_profile.id if current_user.member_profile else None
                return render_template(
                    'requisition/create.html',
                    members=members,
                    preselected_member_id=preselected_member_id,
                    can_manage=can_manage_requisition(),
                    error='Invalid expected return date format.',
                    form_data=request.form
                )

        requisition = Requisition(
            item_name=first_item_name or 'Unspecified Item',
            quantity=first_quantity,
            date_taken=date_taken,
            expected_return_date=expected_return_date,
            status='Pending',
            member_id=member.id,
            created_by=user.id
        )
        db.session.add(requisition)
        db.session.flush()

        first_item = None
        for i, item_name in enumerate(merged_names):
            item_name = item_name.strip()
            if not item_name:
                continue
            quantity = int(quantities[i]) if i < len(quantities) and quantities[i] else 1
            item = RequisitionItem(
                requisition_id=requisition.id,
                item_name=item_name,
                quantity=quantity
            )
            db.session.add(item)
            if first_item is None:
                first_item = item

        if first_item is not None:
            requisition.item_name = first_item.item_name
            requisition.quantity = first_item.quantity

        db.session.commit()
        flash('Requisition created successfully.', 'success')
        return redirect(url_for('requisition.index'))

    members = Member.query.order_by(Member.firstname).all() if can_manage_requisition() else []
    preselected_member_id = current_user.member_profile.id if current_user.member_profile else None
    return render_template(
        'requisition/create.html',
        members=members,
        preselected_member_id=preselected_member_id,
        can_manage=can_manage_requisition()
    )


@bp.route('/<int:req_id>/edit', methods=('GET', 'POST'))
@login_required
def edit(req_id):
    user = User.query.get_or_404(current_user.id)
    requisition = Requisition.query.get_or_404(req_id)

    if not can_manage_requisition() and requisition.member_id != (user.member_profile.id if user.member_profile else None):
        flash('You do not have permission to edit this requisition.', 'danger')
        return redirect(url_for('requisition.index'))

    if request.method == 'POST':
        date_taken_str = request.form.get('date_taken', '').strip()
        expected_return_date_str = request.form.get('expected_return_date', '').strip()
        member_id = request.form.get('member_id', type=int)

        item_names = request.form.getlist('item_name[]')
        other_names = request.form.getlist('item_name_other[]')
        quantities = request.form.getlist('quantity[]')

        if not date_taken_str:
            return render_template(
                'requisition/edit.html',
                requisition=requisition,
                members=members,
                can_manage=can_manage_requisition(),
                error='Date taken is required.',
                form_data=request.form
            )

        if not item_names or not any(name.strip() for name in item_names):
            return render_template(
                'requisition/edit.html',
                requisition=requisition,
                members=members,
                can_manage=can_manage_requisition(),
                error='At least one item is required.',
                form_data=request.form
            )

        # Merge "Other" text inputs with selected items
        merged_names = []
        other_idx = 0
        for i, name in enumerate(item_names):
            if name == 'Other':
                other_value = other_names[other_idx].strip() if other_idx < len(other_names) else ''
                if not other_value:
                    return render_template(
                        'requisition/edit.html',
                        requisition=requisition,
                        members=members,
                        can_manage=can_manage_requisition(),
                        error='Please specify the item name for the "Other" selection.',
                        form_data=request.form
                    )
                merged_names.append(other_value)
                other_idx += 1
            else:
                merged_names.append(name.strip())

        try:
            requisition.date_taken = datetime.strptime(date_taken_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return render_template(
                'requisition/edit.html',
                requisition=requisition,
                members=members,
                can_manage=can_manage_requisition(),
                error='Invalid date taken format.',
                form_data=request.form
            )

        if expected_return_date_str:
            try:
                requisition.expected_return_date = datetime.strptime(expected_return_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return render_template(
                    'requisition/edit.html',
                    requisition=requisition,
                    members=members,
                    can_manage=can_manage_requisition(),
                    error='Invalid expected return date format.',
                    form_data=request.form
                )
        else:
            requisition.expected_return_date = None

        if can_manage_requisition() and member_id:
            member = Member.query.get(member_id)
            if member:
                requisition.member_id = member.id

        # Remove existing items and recreate
        RequisitionItem.query.filter_by(requisition_id=requisition.id).delete()

        first_item = None
        for i, item_name in enumerate(merged_names):
            item_name = item_name.strip()
            if not item_name:
                continue
            quantity = int(quantities[i]) if i < len(quantities) and quantities[i] else 1
            item = RequisitionItem(
                requisition_id=requisition.id,
                item_name=item_name,
                quantity=quantity
            )
            db.session.add(item)
            if first_item is None:
                first_item = item

        if first_item is not None:
            requisition.item_name = first_item.item_name
            requisition.quantity = first_item.quantity

        db.session.commit()
        flash('Requisition updated successfully.', 'success')
        return redirect(url_for('requisition.index'))

    members = Member.query.order_by(Member.firstname).all() if can_manage_requisition() else []
    return render_template(
        'requisition/edit.html',
        requisition=requisition,
        members=members,
        can_manage=can_manage_requisition()
    )


@bp.route('/<int:req_id>/delete', methods=('POST',))
@login_required
def delete(req_id):
    user = User.query.get_or_404(current_user.id)
    requisition = Requisition.query.get_or_404(req_id)

    if not can_manage_requisition():
        flash('You do not have permission to delete requisitions.', 'danger')
        return redirect(url_for('requisition.index'))

    db.session.delete(requisition)
    db.session.commit()
    flash('Requisition deleted successfully.', 'success')
    return redirect(url_for('requisition.index'))


@bp.route('/<int:req_id>/status', methods=('POST',))
@login_required
def update_status(req_id):
    user = User.query.get_or_404(current_user.id)
    if not can_manage_requisition():
        flash('You do not have permission to update requisition status.', 'danger')
        return redirect(url_for('requisition.index'))

    requisition = Requisition.query.get_or_404(req_id)
    new_status = request.form.get('status', '').strip()

    if new_status not in REQUISITION_STATUSES:
        flash('Invalid status value.', 'danger')
        return redirect(url_for('requisition.index'))

    requisition.status = new_status
    db.session.commit()
    flash(f'Requisition status updated to {new_status}.', 'success')
    return redirect(url_for('requisition.index'))
