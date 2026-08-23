import base64
import csv
import io
from collections import defaultdict
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, Response, jsonify
from app.deposit import bp
from flask_login import login_required, current_user
from app import db
from app.user import User
from app.level import AccessLevel
from app.models.register import Member
from app.models.community_event import CommunityEvent
from app.models.child import Child
from app.models.spouse import Spouse
from app.models.contribute import Contribution
from app.models.payments import Payment
from app.image import get_image_mime_type
from sqlalchemy.orm import joinedload, subqueryload
@bp.route('/')
@login_required
def index():
    user = User.query.get_or_404(current_user.id)
    export_csv = request.args.get('export', '')

    if user.role in (AccessLevel.ADMIN, AccessLevel.DEVEL):
        search = request.args.get('search', '')
        payment_type = request.args.get('payment_type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Eager load member relationships to avoid N+1 queries
        query = Member.query.options(
            joinedload(Member.user_account).subqueryload(User.image)
        )
        
        if search:
            search_terms = [term.strip() for term in search.split() if term.strip()]
            name_conditions = []
            for term in search_terms:
                name_conditions.append(
                    db.or_(
                        db.cast(Member.id_number, db.String).ilike(f'%{term}%'),
                        Member.firstname.ilike(f'%{term}%'),
                        Member.lastname.ilike(f'%{term}%'),
                        Member.surname.ilike(f'%{term}%')
                    )
                )
            query = query.filter(db.and_(*name_conditions))
        
        members = query.all()
        
        contribution_query = Contribution.query.options(
            joinedload(Contribution.member).joinedload(Member.user_account).subqueryload(User.image),
            joinedload(Contribution.community_event)
        )
        if search:
            contribution_query = contribution_query.join(Member).filter(
                db.or_(
                    Member.firstname.ilike(f'%{search}%'),
                    Member.lastname.ilike(f'%{search}%'),
                    Member.surname.ilike(f'%{search}%')
                )
            )
        if payment_type:
            try:
                payment_enum = Payment[payment_type] if payment_type in Payment.__members__ else Payment(payment_type)
                contribution_query = contribution_query.filter(Contribution.payment_type == payment_enum)
            except (ValueError, KeyError):
                pass
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                contribution_query = contribution_query.filter(Contribution.trans_date >= from_date)
            except (ValueError, TypeError):
                pass
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                contribution_query = contribution_query.filter(Contribution.trans_date <= to_date)
            except (ValueError, TypeError):
                pass
        
        contributions = contribution_query.order_by(Contribution.trans_date.desc()).all()
        events = CommunityEvent.query.all()
        
        contributions_by_member = defaultdict(list)
        for c in contributions:
            contributions_by_member[c.member_id].append(c)
        
        if export_csv == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Member', 'ID Number', 'Amount', 'Payment Type', 'Event', 'Date'])
            for contribution in contributions:
                writer.writerow([
                    f'{contribution.member.firstname} {contribution.member.lastname} {contribution.member.surname}' if contribution.member else 'N/A',
                    contribution.member.id_number if contribution.member else 'N/A',
                    contribution.amount,
                    contribution.payment_type.value if contribution.payment_type else 'N/A',
                    contribution.community_event.name if contribution.community_event else 'N/A',
                    contribution.trans_date.strftime('%B %d, %Y') if contribution.trans_date else 'N/A'
                ])
            response = Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=contributions.csv'}
            )
            return response
        
        # Prepare member data for dropdowns (lightweight)
        members_dropdown = [
            {'id': m.id, 'name': f"{m.firstname} {m.lastname} {m.surname}"}
            for m in members
        ]
        
        return render_template("deposit/index.html", user=user, members=members, contributions=contributions, contributions_by_member=contributions_by_member, events=events, level=Payment, filters={'search': search, 'payment_type': payment_type, 'date_from': date_from, 'date_to': date_to}, members_dropdown=members_dropdown)
    member = user.member_profile
    if not member:
        return render_template("deposit/index.html", user=user)
    
    event_id = request.args.get('event', type=int)
    payment_type = request.args.get('payment_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Contribution.query.filter_by(member_id=member.id)
    
    if event_id:
        query = query.filter_by(propose=event_id)
    if payment_type:
        try:
            payment_enum = Payment[payment_type] if payment_type in Payment.__members__ else Payment(payment_type)
            query = query.filter(Contribution.payment_type == payment_enum)
        except (ValueError, KeyError):
            pass
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Contribution.trans_date >= from_date)
        except (ValueError, TypeError):
            pass
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Contribution.trans_date <= to_date)
        except (ValueError, TypeError):
            pass
    
    contributions = query.order_by(Contribution.trans_date.desc()).all()
    events = CommunityEvent.query.all()
    
    contributions_by_member = defaultdict(list)
    for c in contributions:
        contributions_by_member[c.member_id].append(c)
    
    return render_template("deposit/index.html", user=user, register=member, contributions=contributions, contributions_by_member=contributions_by_member, events=events, level=Payment, filters={'event': event_id, 'payment_type': payment_type, 'date_from': date_from, 'date_to': date_to})

@bp.route('/<int:depo_id>/')
def deposit(depo_id):
    register = Member.query.get_or_404(depo_id)
    deposit = Contribution.query.options(
        joinedload(Contribution.member),
        joinedload(Contribution.community_event)
    ).filter_by(member_id=register.id).order_by(Contribution.trans_date.desc()).all()
    
    member_contribution_events = db.select(Contribution.propose).where(
        Contribution.member_id == register.id
    ).distinct()
    pending_contributions = CommunityEvent.query.filter(
        ~CommunityEvent.id.in_(member_contribution_events)
    ).all()
    total = sum(c.amount for c in deposit)
    total = "{:,}".format(total)
    events = CommunityEvent.query.all()

    member_profile_image = None
    member_profile_mime_type = 'image/jpeg'
    if register.user_account:
        user_img = register.user_account.image
        if user_img:
            first_img = user_img[0] if isinstance(user_img, list) else user_img
            if first_img and first_img.image:
                member_profile_image = base64.b64encode(first_img.image).decode('ascii')
                member_profile_mime_type = get_image_mime_type(first_img.image)

    return render_template('deposit/deposit.html', register=register, total=total, deposit=deposit, pending_contributions=pending_contributions, events=events, level=Payment, member_profile_image=member_profile_image, member_profile_mime_type=member_profile_mime_type)

@bp.route('/<int:depo_id>/edit', methods=('POST', 'GET'))
@login_required
def edit_contribution(depo_id):
    user = User.query.get_or_404(current_user.id)
    contribution = Contribution.query.get_or_404(depo_id)
    register = contribution.member
    if user.role not in (AccessLevel.ADMIN, AccessLevel.DEVEL) and contribution.added_by != user.id:
        flash("You do not have permission to edit this contribution.", "danger")
        return redirect(url_for('deposit.index'))
    events = CommunityEvent.query.all()

    if request.method == 'POST':
        contribution.amount = request.form['amount']
        # Convert string value to Payment enum
        payment_value = request.form['payment']
        contribution.payment_type = Payment(payment_value)
        contribution.propose = request.form.get('propose')
        db.session.commit()
        flash("Contribution updated successfully.", "success")
        return redirect(url_for('deposit.deposit', depo_id=register.id))
    payment_options = [(pt.name, pt.value) for pt in Payment]
    return render_template("deposit/edit.html", register=register, deposit=contribution, user=user, payment_options=payment_options, events=events)

@bp.post('/<int:depo_id>/delete')
@login_required
def delete_contribution(depo_id):
    user = User.query.get_or_404(current_user.id)
    if user.role not in (AccessLevel.ADMIN, AccessLevel.DEVEL):
        flash("You do not have permission to delete contributions.", "danger")
        return redirect(url_for('deposit.index'))
    contribution = Contribution.query.get_or_404(depo_id)
    register_id = contribution.member.id
    db.session.delete(contribution)
    db.session.commit()
    flash("Contribution deleted successfully.", "success")
    return redirect(url_for('register.deposit', depo_id=register_id))

@bp.route('/<int:depo_id>/amount', methods=('POST', 'GET'))
@login_required
def amount(depo_id):
    user = User.query.get_or_404(current_user.id)
    if user.role not in (AccessLevel.ADMIN, AccessLevel.DEVEL):
        flash("You do not have permission to add contributions.", "danger")
        return redirect(url_for('deposit.index'))
    level = Payment

    # If depo_id is 0, redirect to members list
    if depo_id == 0:
        flash("Please select a member first to add a contribution.")
        return redirect(url_for('register.index'))

    register = Member.query.get_or_404(depo_id)
    events = CommunityEvent.query.all()
    
    # Get pre-selected event from query parameter (from pending contributions)
    preselected_event = request.args.get('event_id', type=int)

    if request.method == 'POST':
        try:
            propose_id = request.form.get('propose')
            propose = int(propose_id) if propose_id else None
            payment_value = request.form['payment']
            # Convert string value to Payment enum
            payment_type = Payment(payment_value)
            amount = Contribution(amount = request.form['amount'], payment_type = payment_type, transaction_ref=request.form['transaction_ref'], propose = propose, member = register, user = user)
            db.session.add(amount)
            db.session.commit()
            return redirect(url_for('register.deposit', depo_id=register.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error saving contribution: {str(e)}", "danger")
            payment_options = [(pt.name, pt.value) for pt in Payment]
            return render_template("deposit/amount.html", register=register, user=user, payment_options=payment_options, events=events, form_data=request.form, preselected_event=preselected_event)
    payment_options = [(pt.name, pt.value) for pt in Payment]
    return render_template("deposit/amount.html", register=register, user=user, payment_options=payment_options, events=events, preselected_event=preselected_event)


@bp.route('/api/member/<int:member_id>/pending-contributions')
@login_required
def api_member_pending_contributions(member_id):
    """API endpoint to fetch pending contributions for a member."""
    user = User.query.get_or_404(current_user.id)
    if user.role not in (AccessLevel.ADMIN, AccessLevel.DEVEL):
        return jsonify({'error': 'Unauthorized'}), 403

    member = Member.query.get_or_404(member_id)

    # Get events the member has already contributed to - optimized query
    member_contribution_events = db.session.query(Contribution.propose).filter(
        Contribution.member_id == member_id,
        Contribution.propose.isnot(None)
    ).subquery()

    # Get pending events (events not yet contributed to by this member)
    pending_events = (
        CommunityEvent.query
        .filter(~CommunityEvent.id.in_(member_contribution_events))
        .order_by(CommunityEvent.event_date.asc())
        .all()
    )

    # Build response without base64 encoding (deferred to separate endpoint)
    pending_contributions = []
    for event in pending_events:
        pending_contributions.append({
            'id': event.id,
            'name': event.name,
            'details': event.details,
            'event_date': event.event_date.strftime('%b %d, %Y') if event.event_date else 'TBD',
            'created_at': event.created_at.strftime('%b %d, %Y') if event.created_at else ''
        })

    # Check if member has profile image (don't encode here - use URL instead)
    has_profile_image = False
    if member.user_account and member.user_account.image:
        has_profile_image = True

    return jsonify({
        'member_id': member.id,
        'member_name': f"{member.firstname} {member.lastname} {member.surname}",
        'pending_contributions': pending_contributions,
        'count': len(pending_contributions),
        'has_profile_image': has_profile_image,
        'member_image_url': url_for('main.member_image', member_id=member_id) if has_profile_image else None
    })

