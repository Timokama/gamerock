import base64
import csv
import io
import json
from collections import defaultdict
from flask import render_template, request, url_for, Response, jsonify
from app.reports import bp
from flask_login import login_required, current_user
from app.user import User
from app.models.register import Member
from app import db
from app.models.contribute import Contribution
from app.models.community_event import CommunityEvent
from app.models.payments import Payment
from datetime import datetime


def _build_filtered_query():
    search = request.args.get('search', '')
    payment_type_filter = request.args.get('payment_type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    event_filter = request.args.get('event', '')

    query = Contribution.query.join(Contribution.member).join(Contribution.community_event)

    if search:
        search_terms = [term.strip() for term in search.split() if term.strip()]
        term_conditions = []
        for term in search_terms:
            term_conditions.append(
                db.or_(
                    db.cast(Member.id_number, db.String).ilike(f'%{term}%'),
                    Member.firstname.ilike(f'%{term}%'),
                    Member.lastname.ilike(f'%{term}%'),
                    Member.surname.ilike(f'%{term}%'),
                    Contribution.transaction_ref.ilike(f'%{term}%'),
                    CommunityEvent.name.ilike(f'%{term}%')
                )
            )
        if term_conditions:
            query = query.filter(db.and_(*term_conditions))

    if payment_type_filter:
        try:
            payment_enum = Payment(payment_type_filter)
            query = query.filter(Contribution.payment_type == payment_enum)
        except ValueError:
            pass

    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Contribution.trans_date >= from_date)
        except (ValueError, TypeError):
            pass

    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(Contribution.trans_date <= to_date)
        except (ValueError, TypeError):
            pass

    if event_filter:
        try:
            event_id = int(event_filter)
            query = query.filter(Contribution.propose == event_id)
        except (ValueError, TypeError):
            pass

    return query


def _get_filtered_contributions():
    return _build_filtered_query().order_by(Contribution.trans_date.desc()).all()


@bp.route('/chart-data')
@login_required
def chart_data():
    contributions = _get_filtered_contributions()
    total = sum(c.amount for c in contributions)

    by_month = defaultdict(float)
    by_payment = defaultdict(float)
    by_member = defaultdict(float)
    by_event = defaultdict(float)

    for c in contributions:
        if c.trans_date:
            month_key = c.trans_date.strftime('%Y-%m')
            by_month[month_key] += c.amount

        if c.payment_type:
            by_payment[c.payment_type.value] += c.amount

        if c.member:
            member_name = f"{c.member.firstname} {c.member.lastname}"
            by_member[member_name] += c.amount

        if c.community_event and c.community_event.name:
            by_event[c.community_event.name] += c.amount

    monthly_data = dict(sorted(by_month.items()))
    top_members = dict(sorted(by_member.items(), key=lambda x: x[1], reverse=True)[:10])
    event_data = dict(sorted(by_event.items(), key=lambda x: x[1], reverse=True)[:10])
    payment_data = dict(by_payment)

    return jsonify({
        'total': total,
        'count': len(contributions),
        'average': int(total / len(contributions)) if contributions else 0,
        'monthly': monthly_data,
        'payment_types': payment_data,
        'top_members': top_members,
        'events': event_data
    })


@bp.route('/')
@login_required
def index():
    user = User.query.get_or_404(current_user.id)
    search = request.args.get('search', '')
    payment_type_filter = request.args.get('payment_type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    event_filter = request.args.get('event', '')
    export_csv = request.args.get('export', '')

    query = Contribution.query

    if search:
        search_terms = [term.strip() for term in search.split() if term.strip()]
        term_conditions = []
        for term in search_terms:
            term_conditions.append(
                db.or_(
                    db.cast(Member.id_number, db.String).ilike(f'%{term}%'),
                    Member.firstname.ilike(f'%{term}%'),
                    Member.lastname.ilike(f'%{term}%'),
                    Member.surname.ilike(f'%{term}%'),
                    Contribution.transaction_ref.ilike(f'%{term}%'),
                    CommunityEvent.name.ilike(f'%{term}%')
                )
            )
        query = query.join(Contribution.member).join(Contribution.community_event).outerjoin(Member.user_account).filter(
            db.and_(*term_conditions)
        )

    if payment_type_filter:
        try:
            payment_enum = Payment(payment_type_filter)
            query = query.filter(Contribution.payment_type == payment_enum)
        except ValueError:
            pass

    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Contribution.trans_date >= from_date)
        except (ValueError, TypeError):
            pass

    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(Contribution.trans_date <= to_date)
        except (ValueError, TypeError):
            pass

    if event_filter:
        try:
            event_id = int(event_filter)
            query = query.filter(Contribution.propose == event_id)
        except (ValueError, TypeError):
            pass

    all_contribution_accounts = query.order_by(Contribution.trans_date.desc()).all()
    total = sum(c.amount for c in all_contribution_accounts)
    count = len(all_contribution_accounts)
    avg_amount = int(total / count) if count else 0

    if export_csv == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'Member', 'Phone Number', 'Amount', 'Type', 'Event'])
        for contribute in all_contribution_accounts:
            writer.writerow([
                contribute.trans_date.strftime('%Y-%m-%d') if contribute.trans_date else '',
                f'{contribute.member.firstname} {contribute.member.lastname} {contribute.member.surname}' if contribute.member else '',
                contribute.member.phone_num if contribute.member and contribute.member.phone_num else '',
                contribute.amount,
                contribute.payment_type.value if contribute.payment_type else '',
                contribute.community_event.name if contribute.community_event else 'N/A'
            ])
        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=contribution_reports_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
        return response

    events = CommunityEvent.query.order_by(CommunityEvent.name).all()
    payment_types = [pt.value for pt in Payment]

    return render_template("reports/index.html",
                           total=total,
                           members=count,
                           user=user,
                           all_contribution_accounts=all_contribution_accounts,
                           search=search,
                           payment_type_filter=payment_type_filter,
                           date_from=date_from,
                           date_to=date_to,
                           event_filter=event_filter,
                           events=events,
                           payment_types=payment_types,
                           avg_amount=avg_amount)

@bp.route('/<int:depo_id>/reports')
def reports(depo_id):
    contribute = Contribution.query.get_or_404(depo_id)
    member = contribute.member
    total = contribute.amount
    count = 1
    member_total = sum(c.amount for c in member.contribute)
    member_total = "{:,}".format(member_total)
    recent_contributions = Contribution.query.filter_by(member_id=member.id).order_by(Contribution.trans_date.desc()).limit(5).all()

    member_profile_image = None
    if member.user_account and member.user_account.image:
        user_img = member.user_account.image[0] if isinstance(member.user_account.image, list) else member.user_account.image
        if user_img and user_img.image:
            member_profile_image = base64.b64encode(user_img.image).decode('ascii')

    event_image_url = None
    if contribute.community_event and contribute.community_event.image:
        event_image_url = url_for('static', filename='images/events/' + contribute.community_event.image)

    return render_template("reports/reports.html",
                           contribute=contribute,
                           member=member,
                           total=total,
                           members=count,
                           member_total=member_total,
                           recent_contributions=recent_contributions,
                           member_profile_image=member_profile_image,
                           event_image_url=event_image_url)