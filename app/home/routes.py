from flask import render_template, url_for
from flask_login import login_required, current_user
from app.home import bp
from app import db
from app.models.register import Member
from app.models.contribute import Contribution
from app.models.community_event import CommunityEvent
from app.models.spouse import Spouse
from app.models.child import Child
from app.level import AccessLevel
from datetime import datetime

@bp.route('/overview')
@login_required
def home():
    total_members = 0
    total_contributions = 0
    total_events = 0
    member_details = None
    family_stats = None
    avatar_url = None

    if current_user.role.name in ['DEVEL', 'ADMIN']:
        total_members = Member.query.count()
        total_contributions = db.session.query(db.func.sum(Contribution.amount)).scalar() or 0
        total_events = CommunityEvent.query.count()
    else:
        member = current_user.member_profile
        if member:
            all_contributions = member.contribute
            total_contributions = sum(c.amount for c in all_contributions)
            spouses = list(member.spouse) if member.spouse else []
            children = list(member.child) if member.child else []
            all_children = list(children)
            for spouse in spouses:
                for child in spouse.child:
                    if child.id not in [c.id for c in all_children]:
                        all_children.append(child)
            member_details = {
                'firstname': member.firstname,
                'lastname': member.lastname,
                'surname': member.surname,
                'date_of_birth': member.date_of_birth,
                'created_at': member.created_at,
                'id_number': member.id_number,
                'phone_num': member.phone_num,
                'spouses': spouses,
                'children': children,
                'all_children': all_children,
            }
            family_stats = {
                'spouse_count': len(spouses),
                'direct_children_count': len(children),
                'all_children_count': len(all_children),
                'total_family_members': len(spouses) + len(all_children),
            }
            if member.user_account and member.user_account.image:
                avatar_url = url_for('main.member_image', member_id=member.id)

    if not avatar_url:
        avatar_url = url_for('main.avatar')

    return render_template(
        "overview.html",
        name=current_user.first_name,
        contact=current_user.phone_num,
        email=current_user.role.value,
        role=current_user.role.value,
        total_members=total_members,
        total_contributions=total_contributions,
        total_events=total_events,
        member_details=member_details,
        family_stats=family_stats,
        now=datetime.now,
        avatar_url=avatar_url,
    )