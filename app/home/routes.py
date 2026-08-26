from flask import render_template, url_for
from flask_login import login_required, current_user
from app.home import bp
from app import db
from app.models.register import Member
from app.models.contribute import Contribution
from app.models.community_event import CommunityEvent
from app.models.spouse import Spouse
from app.models.child import Child
from app.models.budget import Budget, BudgetItem
from app.models.treasurer import TreasurerRecord
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

    budget_stats = None
    treasurer_stats = None
    recent_budgets = []
    recent_treasurer_records = []

    if current_user.role.name in ['DEVEL', 'ADMIN']:
        total_members = Member.query.count()
        total_contributions = db.session.query(db.func.sum(Contribution.amount)).scalar() or 0
        total_events = CommunityEvent.query.count()

        budgets = Budget.query.all()
        budget_stats = {
            'total_budgets': len(budgets),
            'total_amount': sum(b.total_amount for b in budgets),
            'approved': sum(1 for b in budgets if b.status == 'Approved'),
            'active': sum(1 for b in budgets if b.status == 'Active'),
            'draft': sum(1 for b in budgets if b.status == 'Draft'),
            'closed': sum(1 for b in budgets if b.status == 'Closed'),
        }
        recent_budgets = Budget.query.order_by(Budget.created_at.desc()).limit(5).all()

    elif current_user.role.name == 'TREASURER':
        pass

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

    if current_user.role.name in ['DEVEL', 'ADMIN', 'TREASURER']:
        total_income = db.session.query(db.func.sum(TreasurerRecord.amount)).filter(
            TreasurerRecord.record_type == 'Income'
        ).scalar() or 0
        total_expenses = db.session.query(db.func.sum(TreasurerRecord.amount)).filter(
            TreasurerRecord.record_type == 'Expense'
        ).scalar() or 0
        treasurer_stats = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': total_income - total_expenses,
            'total_records': TreasurerRecord.query.count(),
        }
        recent_treasurer_records = TreasurerRecord.query.order_by(
            TreasurerRecord.transaction_date.desc()
        ).limit(5).all()

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
        budget_stats=budget_stats,
        treasurer_stats=treasurer_stats,
        recent_budgets=recent_budgets,
        recent_treasurer_records=recent_treasurer_records,
        now=datetime.now,
        avatar_url=avatar_url,
    )