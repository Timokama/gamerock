from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.sponsor import bp
from app import db
from app.user import User
from app.level import AccessLevel
from app.models.sponsor import Sponsor, SponsorItem

def can_manage_sponsor():
    return current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN', 'CHAIRPERSON']

@bp.route('/')
@login_required
def index():
    if not can_manage_sponsor():
        flash('You do not have permission to view sponsors.', 'danger')
        return redirect(url_for('home.home'))

    search = request.args.get('search', '')
    sponsorship_type = request.args.get('type', '')
    status = request.args.get('status', '')

    query = Sponsor.query

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Sponsor.name.ilike(like),
                Sponsor.contact_person.ilike(like),
                Sponsor.email.ilike(like),
                Sponsor.phone.ilike(like)
            )
        )

    if sponsorship_type:
        query = query.filter(Sponsor.sponsorship_type == sponsorship_type)

    if status:
        query = query.filter(Sponsor.status == status)

    sponsors = query.order_by(Sponsor.created_at.desc()).all()

    return render_template(
        'sponsor/index.html',
        sponsors=sponsors,
        search=search,
        sponsorship_type=sponsorship_type,
        status=status
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not can_manage_sponsor():
        flash('You do not have permission to create sponsors.', 'danger')
        return redirect(url_for('sponsor.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        sponsorship_type = request.form.get('sponsorship_type', '').strip()
        amount = request.form.get('amount', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date = request.form.get('end_date', '').strip()
        status = request.form.get('status', 'Active')
        notes = request.form.get('notes', '').strip()

        if not name:
            flash('Sponsor name is required.', 'danger')
            return redirect(url_for('sponsor.create'))

        sponsor = Sponsor(
            name=name,
            contact_person=contact_person or None,
            email=email or None,
            phone=phone or None,
            address=address or None,
            sponsorship_type=sponsorship_type or None,
            amount=int(amount) if amount else None,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None,
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
            status=status,
            notes=notes or None,
            created_by=current_user.id
        )

        db.session.add(sponsor)
        db.session.commit()

        flash('Sponsor created successfully.', 'success')
        return redirect(url_for('sponsor.index'))

    return render_template('sponsor/create.html')

@bp.route('/<int:sponsor_id>')
@login_required
def view(sponsor_id):
    if not can_manage_sponsor():
        flash('You do not have permission to view sponsors.', 'danger')
        return redirect(url_for('sponsor.index'))

    sponsor = Sponsor.query.get_or_404(sponsor_id)
    return render_template('sponsor/view.html', sponsor=sponsor)

@bp.route('/<int:sponsor_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(sponsor_id):
    if not can_manage_sponsor():
        flash('You do not have permission to edit sponsors.', 'danger')
        return redirect(url_for('sponsor.index'))

    sponsor = Sponsor.query.get_or_404(sponsor_id)

    if request.method == 'POST':
        sponsor.name = request.form.get('name', '').strip()
        sponsor.contact_person = request.form.get('contact_person', '').strip() or None
        sponsor.email = request.form.get('email', '').strip() or None
        sponsor.phone = request.form.get('phone', '').strip() or None
        sponsor.address = request.form.get('address', '').strip() or None
        sponsor.sponsorship_type = request.form.get('sponsorship_type', '').strip() or None
        amount = request.form.get('amount', '').strip()
        sponsor.amount = int(amount) if amount else None
        start_date = request.form.get('start_date', '').strip()
        sponsor.start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_date = request.form.get('end_date', '').strip()
        sponsor.end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        sponsor.status = request.form.get('status', 'Active')
        sponsor.notes = request.form.get('notes', '').strip() or None

        db.session.commit()

        flash('Sponsor updated successfully.', 'success')
        return redirect(url_for('sponsor.view', sponsor_id=sponsor.id))

    return render_template('sponsor/edit.html', sponsor=sponsor)

@bp.route('/<int:sponsor_id>/delete', methods=['POST'])
@login_required
def delete(sponsor_id):
    if not can_manage_sponsor():
        flash('You do not have permission to delete sponsors.', 'danger')
        return redirect(url_for('sponsor.index'))

    sponsor = Sponsor.query.get_or_404(sponsor_id)
    db.session.delete(sponsor)
    db.session.commit()

    flash('Sponsor deleted successfully.', 'success')
    return redirect(url_for('sponsor.index'))


@bp.route('/<int:sponsor_id>/items/create', methods=['GET', 'POST'])
@login_required
def create_item(sponsor_id):
    if not can_manage_sponsor():
        flash('You do not have permission to manage sponsor items.', 'danger')
        return redirect(url_for('sponsor.index'))

    sponsor = Sponsor.query.get_or_404(sponsor_id)

    if request.method == 'POST':
        item_name = request.form.get('item_name', '').strip()
        description = request.form.get('description', '').strip()
        quantity = request.form.get('quantity', '1').strip()
        unit_price = request.form.get('unit_price', '0').strip()
        item_type = request.form.get('item_type', '').strip()
        status = request.form.get('status', 'Pending')
        notes = request.form.get('notes', '').strip()

        if not item_name:
            flash('Item name is required.', 'danger')
            return redirect(url_for('sponsor.view', sponsor_id=sponsor_id))

        quantity_int = int(quantity) if quantity else 1
        unit_price_int = int(unit_price) if unit_price else 0
        total_price_int = quantity_int * unit_price_int

        item = SponsorItem(
            sponsor_id=sponsor.id,
            item_name=item_name,
            description=description or None,
            quantity=quantity_int,
            unit_price=unit_price_int,
            total_price=total_price_int,
            item_type=item_type or None,
            status=status,
            notes=notes or None
        )

        db.session.add(item)
        db.session.commit()

        flash('Sponsor item created successfully.', 'success')
        return redirect(url_for('sponsor.view', sponsor_id=sponsor_id))

    return render_template('sponsor/items/create.html', sponsor=sponsor)


@bp.route('/<int:sponsor_id>/items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(sponsor_id, item_id):
    if not can_manage_sponsor():
        flash('You do not have permission to manage sponsor items.', 'danger')
        return redirect(url_for('sponsor.index'))

    sponsor = Sponsor.query.get_or_404(sponsor_id)
    item = SponsorItem.query.filter_by(id=item_id, sponsor_id=sponsor_id).first_or_404()

    if request.method == 'POST':
        item.item_name = request.form.get('item_name', '').strip()
        item.description = request.form.get('description', '').strip() or None
        quantity = request.form.get('quantity', '1').strip()
        unit_price = request.form.get('unit_price', '0').strip()
        item.item_type = request.form.get('item_type', '').strip() or None
        item.status = request.form.get('status', 'Pending')
        item.notes = request.form.get('notes', '').strip() or None

        item.quantity = int(quantity) if quantity else 1
        item.unit_price = int(unit_price) if unit_price else 0
        item.total_price = item.quantity * item.unit_price

        db.session.commit()

        flash('Sponsor item updated successfully.', 'success')
        return redirect(url_for('sponsor.view', sponsor_id=sponsor_id))

    return render_template('sponsor/items/edit.html', sponsor=sponsor, item=item)


@bp.route('/<int:sponsor_id>/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(sponsor_id, item_id):
    if not can_manage_sponsor():
        flash('You do not have permission to manage sponsor items.', 'danger')
        return redirect(url_for('sponsor.index'))

    sponsor = Sponsor.query.get_or_404(sponsor_id)
    item = SponsorItem.query.filter_by(id=item_id, sponsor_id=sponsor_id).first_or_404()
    db.session.delete(item)
    db.session.commit()

    flash('Sponsor item deleted successfully.', 'success')
    return redirect(url_for('sponsor.view', sponsor_id=sponsor_id))
