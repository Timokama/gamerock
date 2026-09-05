from flask import render_template, request, redirect, url_for, flash, make_response, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import csv
from io import StringIO
from app.community import bp
from app import db
from app.user import User
from app.level import AccessLevel
from app.models.register import Member
from app.models.spouse import Spouse
from app.models.child import Child
from app.models.contribute import Contribution
from app.models.community_event import CommunityEvent
from app.models.payments import Payment

EVENTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'images', 'events')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_events_folder():
    os.makedirs(EVENTS_FOLDER, exist_ok=True)

@bp.route('/')
@login_required
def index():
    user = User.query.get(current_user.id)
    search = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    query = CommunityEvent.query
    
    if search:
        query = query.filter(
            db.or_(
                CommunityEvent.name.ilike(f'%{search}%'),
                CommunityEvent.details.ilike(f'%{search}%')
            )
        )
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(CommunityEvent.event_date >= from_date)
        except (ValueError, TypeError):
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(CommunityEvent.event_date <= to_date)
        except (ValueError, TypeError):
            pass
    
    events = query.order_by(CommunityEvent.sort_order.asc(), CommunityEvent.event_date.desc()).all()
    total = 0
    for event in events:
        for amount in event.contribute:
            total += amount.amount
    total = "{:,}".format(total)
    members_count = Member.query.count()
    
    # Calculate per-event totals and split into contributions and pending
    events_with_totals = []
    contributed_events = []
    pending_events = []
    for event in events:
        event_total = sum(c.amount for c in event.contribute)
        contributor_count = len(set(c.member_id for c in event.contribute))
        event_data = {
            'event': event,
            'total': event_total,
            'contributions': event.contribute,
            'contributor_count': contributor_count
        }
        events_with_totals.append(event_data)
        if event_total > 0:
            contributed_events.append(event_data)
        else:
            pending_events.append(event_data)
    
    return render_template('community/index.html', user=user, events=events_with_totals, total=total, members=members_count,
                           contributed_events=contributed_events, pending_events=pending_events,
                           search=search, date_from=date_from, date_to=date_to)


@bp.route('/export_csv')
@login_required
def export_csv():
    search = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    query = CommunityEvent.query
    
    if search:
        query = query.filter(
            db.or_(
                CommunityEvent.name.ilike(f'%{search}%'),
                CommunityEvent.details.ilike(f'%{search}%')
            )
        )
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(CommunityEvent.event_date >= from_date)
        except (ValueError, TypeError):
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(CommunityEvent.event_date <= to_date)
        except (ValueError, TypeError):
            pass
    
    events = query.order_by(CommunityEvent.sort_order.asc(), CommunityEvent.event_date.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Event Name', 'Event Date', 'Details', 'Total Contributions', 'Contributors'])
    
    for event in events:
        event_total = sum(c.amount for c in event.contribute)
        contributor_count = len(set(c.member_id for c in event.contribute))
        writer.writerow([
            event.name,
            event.event_date.strftime('%Y-%m-%d') if event.event_date else '',
            event.details or '',
            event_total,
            contributor_count
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=community_events.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response


@bp.route('/add_event', methods=['POST', 'GET'])
@login_required
def add_event():
    user = User.query.get(current_user.id)
    if user.role not in (AccessLevel.ADMIN, AccessLevel.DEVEL):
        flash("You do not have permission to add events.", "danger")
        return redirect(url_for('community.index'))
    events = CommunityEvent.query.filter_by(created_by = user.id).all()
    
    if request.method == 'POST':
        name = request.form['name']
        details = request.form['details']
        event_date = datetime.strptime(request.form['event_date'], '%Y-%m-%d').date()
        location = request.form.get('location', '')
        goal_amount = request.form.get('goal_amount', type=float)
        is_featured = request.form.get('is_featured', 'false') == 'true'
        sort_order = request.form.get('sort_order', default=0, type=int)
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename != '' and allowed_file(image.filename):
                ensure_events_folder()
                filename = secure_filename(image.filename)
                unique_filename = f"event_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                image.save(os.path.join(EVENTS_FOLDER, unique_filename))
                image_filename = unique_filename
        
        com_event = CommunityEvent(
            name=name,
            details=details,
            event_date=event_date,
            created_by=user.id,
            update_by=user.first_name,
            user=user,
            image=image_filename,
            location=location,
            goal_amount=goal_amount,
            is_featured=is_featured,
            sort_order=sort_order
        )
        db.session.add(com_event)
        db.session.commit()
        return redirect(url_for('community.index'))
    return render_template('community/add_event.html', events=events)

@bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    user = User.query.get_or_404(current_user.id)
    if user.role not in (AccessLevel.ADMIN, AccessLevel.DEVEL, AccessLevel.CHAIRPERSON):
        flash("You do not have permission to delete events.", "danger")
        return redirect(url_for('community.index'))
    event = CommunityEvent.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted successfully.", "success")
    return redirect(url_for('community.index'))


@bp.route('/<int:event_id>/edit_event', methods=['POST', 'GET'])
@login_required
def edit_event(event_id):
    user = User.query.get(current_user.id)
    if user.role not in (AccessLevel.ADMIN, AccessLevel.DEVEL):
        flash("You do not have permission to edit events.", "danger")
        return redirect(url_for('community.index'))
    event = CommunityEvent.query.get_or_404(event_id)
    
    if request.method == 'POST':
        event.name = request.form['name']
        event.details = request.form['details']
        event.event_date = datetime.strptime(request.form['event_date'], '%Y-%m-%d').date()
        event.location = request.form.get('location', '')
        event.goal_amount = request.form.get('goal_amount', type=float)
        event.is_featured = request.form.get('is_featured', 'false') == 'true'
        event.sort_order = request.form.get('sort_order', default=0, type=int)
        event.update_by = user.first_name
        
        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename != '' and allowed_file(image.filename):
                ensure_events_folder()
                filename = secure_filename(image.filename)
                unique_filename = f"event_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                image.save(os.path.join(EVENTS_FOLDER, unique_filename))
                event.image = unique_filename
        
        db.session.commit()
        return redirect(url_for('community.index'))
    
    return render_template('community/edit_event.html', event=event, events=CommunityEvent.query.all())

@bp.route('/contribute/<path:tag_name>/')
def contribute(tag_name):
    user = User.query.get_or_404(current_user.id)
    register = user.family
    
    event = CommunityEvent.query.filter_by(name=tag_name).order_by(CommunityEvent.id.desc()).first_or_404()
    
    search = request.args.get('search', '')
    payment_type = request.args.get('payment_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    all_event_contributions = Contribution.query.filter_by(propose=event.id).all()
    contributed_member_ids = [c.member_id for c in all_event_contributions]

    query = Contribution.query.filter_by(propose=event.id)
    
    if search:
        search_terms = [term.strip() for term in search.split() if term.strip()]
        member_conditions = []
        for term in search_terms:
            member_conditions.append(
                db.or_(
                    db.cast(Member.id_number, db.String).ilike(f'%{term}%'),
                    Member.firstname.ilike(f'%{term}%'),
                    Member.lastname.ilike(f'%{term}%'),
                    Member.surname.ilike(f'%{term}%'),
                    Contribution.transaction_ref.ilike(f'%{term}%')
                )
            )
        query = query.join(Member).filter(db.and_(*member_conditions))
    
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
    
    pending_query = Member.query.filter(~Member.id.in_(contributed_member_ids)) if contributed_member_ids else Member.query
    if search:
        search_terms = [term.strip() for term in search.split() if term.strip()]
        pending_conditions = []
        for term in search_terms:
            pending_conditions.append(
                db.or_(
                    db.cast(Member.id_number, db.String).ilike(f'%{term}%'),
                    Member.firstname.ilike(f'%{term}%'),
                    Member.lastname.ilike(f'%{term}%'),
                    Member.surname.ilike(f'%{term}%')
                )
            )
        pending_query = pending_query.filter(db.and_(*pending_conditions))
    pending_members = pending_query.all()
    
    return render_template('contribute/tag.html', event=event, user=user, register=register, 
                           pending_members=pending_members, contributions=contributions, level=Payment,
                           search=search,
                           filters={'search': search, 'payment_type': payment_type, 'date_from': date_from, 'date_to': date_to})


@bp.route('/contribute/<path:tag_name>/export_csv')
def export_contributions_csv(tag_name):
    event = CommunityEvent.query.filter_by(name=tag_name).order_by(CommunityEvent.id.desc()).first_or_404()
    
    search = request.args.get('search', '')
    payment_type = request.args.get('payment_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Contribution.query.filter_by(propose=event.id)
    
    if search:
        search_terms = [term.strip() for term in search.split() if term.strip()]
        member_conditions = []
        for term in search_terms:
            member_conditions.append(
                db.or_(
                    db.cast(Member.id_number, db.String).ilike(f'%{term}%'),
                    Member.firstname.ilike(f'%{term}%'),
                    Member.lastname.ilike(f'%{term}%'),
                    Member.surname.ilike(f'%{term}%'),
                    Contribution.transaction_ref.ilike(f'%{term}%')
                )
            )
        query = query.join(Member).filter(db.and_(*member_conditions))
    
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
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Member Name', 'ID Number', 'Phone Number', 'Payment Type', 'Amount', 'Date'])
    
    for contrib in contributions:
        writer.writerow([
            f"{contrib.member.firstname} {contrib.member.lastname}" if contrib.member else '',
            contrib.member.id_number or '' if contrib.member else '',
            contrib.member.phone_num or '' if contrib.member else '',
            contrib.payment_type.value if contrib.payment_type else 'N/A',
            contrib.amount,
            contrib.trans_date.strftime('%Y-%m-%d') if contrib.trans_date else ''
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={event.name}_contributions.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response


@bp.route('/<int:event_id>/stats')
@login_required
def event_stats(event_id):
    event = CommunityEvent.query.get_or_404(event_id)
    
    search = request.args.get('search', '')
    payment_type = request.args.get('payment_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Contribution.query.filter_by(propose=event_id)
    
    if search:
        search_terms = [term.strip() for term in search.split() if term.strip()]
        member_conditions = []
        for term in search_terms:
            member_conditions.append(
                db.or_(
                    db.cast(Member.id_number, db.String).ilike(f'%{term}%'),
                    Member.firstname.ilike(f'%{term}%'),
                    Member.lastname.ilike(f'%{term}%'),
                    Member.surname.ilike(f'%{term}%'),
                    Contribution.transaction_ref.ilike(f'%{term}%')
                )
            )
        query = query.join(Member).filter(db.and_(*member_conditions))
    
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
    
    contributions = query.order_by(Contribution.trans_date.asc()).all()

    total = sum(c.amount for c in contributions)
    contributor_count = len(set(c.member_id for c in contributions))

    by_day = {}
    by_payment = {}
    by_member = {}
    for c in contributions:
        if c.trans_date:
            day_key = c.trans_date.strftime('%Y-%m-%d')
            by_day[day_key] = by_day.get(day_key, 0) + c.amount
        if c.payment_type:
            by_payment[c.payment_type.value] = by_payment.get(c.payment_type.value, 0) + c.amount
        if c.member:
            member_name = f"{c.member.firstname} {c.member.lastname}"
            by_member[member_name] = by_member.get(member_name, 0) + c.amount

    top_members = dict(sorted(by_member.items(), key=lambda x: x[1], reverse=True)[:5])
    return jsonify({
        'event_id': event.id,
        'event_name': event.name,
        'total': total,
        'contributor_count': contributor_count,
        'goal_amount': event.goal_amount,
        'location': event.location,
        'by_day': by_day,
        'by_payment': by_payment,
        'top_members': top_members
    })


@bp.post('/<int:event_id>/contribute')
@login_required
def quick_contribute(event_id):
    user = User.query.get_or_404(current_user.id)
    member = user.family
    if not member:
        return jsonify({'success': False, 'message': 'Member profile not found.'}), 400

    event = CommunityEvent.query.get_or_404(event_id)
    amount = request.form.get('amount', type=float)
    payment_type = request.form.get('payment_type')
    if not amount or amount <= 0 or not payment_type:
        return jsonify({'success': False, 'message': 'Invalid contribution data.'}), 400

    try:
        payment_enum = Payment[payment_type] if payment_type in Payment.__members__ else Payment(payment_type)
    except (ValueError, KeyError):
        return jsonify({'success': False, 'message': 'Invalid payment type.'}), 400

    contribution = Contribution(
        amount=amount,
        payment_type=payment_enum,
        propose=event.id,
        member_id=member.id,
        trans_date=datetime.utcnow().date()
    )
    db.session.add(contribution)
    db.session.commit()

    contributions = Contribution.query.filter_by(propose=event.id).all()
    new_total = sum(c.amount for c in contributions)
    contributor_count = len(set(c.member_id for c in contributions))
    return jsonify({
        'success': True,
        'new_total': new_total,
        'contributor_count': contributor_count,
        'message': 'Contribution recorded successfully.'
    })


@bp.post('/<int:event_id>/bookmark')
@login_required
def toggle_bookmark(event_id):
    user = User.query.get_or_404(current_user.id)
    bookmarks = list(user.bookmarks or [])
    if event_id in bookmarks:
        bookmarks.remove(event_id)
        action = 'removed'
    else:
        bookmarks.append(event_id)
        action = 'added'

    user.bookmarks = bookmarks
    db.session.commit()
    return jsonify({'success': True, 'action': action, 'bookmarks': bookmarks})


@bp.route('/events/upcoming')
@login_required
def upcoming_events():
    today = datetime.utcnow().date()
    events = CommunityEvent.query.filter(CommunityEvent.event_date >= today).order_by(CommunityEvent.event_date.asc()).limit(5).all()
    data = []
    for event in events:
        data.append({
            'id': event.id,
            'name': event.name,
            'event_date': event.event_date.strftime('%Y-%m-%d') if event.event_date else None,
            'location': event.location,
            'goal_amount': event.goal_amount
        })
    return jsonify({'upcoming': data})


@bp.post('/<int:depo_id>/delete')
def delete(depo_id):
    user = User.query.get_or_404(current_user.id)
    contribute = Contribution.query.get_or_404(depo_id)
    for cont in contribute.deposit:
        db.session.delete(cont)
    db.session.delete(contribute)
    db.session.commit()
    return redirect(url_for('account.index'))