import os
from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, current_app, Response, send_file
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db
from .image import Images, get_image_mime_type
from .user import User
from .level import AccessLevel
from app.models.register import Member
from app.models.contribute import Contribution
from app.models.community_event import CommunityEvent
from app.models.spouse import Spouse
from app.models.child import Child
from app.models.faq import FAQ
import os
import base64
import io
from sqlalchemy.orm import joinedload, subqueryload

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    # Redirect USER role to their dashboard
    if current_user.role == AccessLevel.USER:
        return redirect(url_for('register.dashboard'))
    
    # Developer and Admin dashboard stats - use single aggregated query
    stats = db.session.query(
        db.func.count(Member.id).label('total_members'),
        db.func.count(Spouse.id).label('total_spouses'),
        db.func.count(Child.id).label('total_children'),
        db.func.count(CommunityEvent.id).label('total_events'),
        db.func.sum(Contribution.amount).label('total_contributions')
    ).select_from(Member).outerjoin(
        Contribution, Contribution.member_id == Member.id
    ).outerjoin(
        Spouse, Spouse.member_id == Member.id
    ).outerjoin(
        Child, Child.member_id == Member.id
    ).outerjoin(
        CommunityEvent
    ).first()
    
    total_members = stats.total_members or 0
    total_spouses = stats.total_spouses or 0
    total_children = stats.total_children or 0
    total_events = stats.total_events or 0
    total_contributions = stats.total_contributions or 0
    
    # Eager load relationships to avoid N+1 queries
    recent_deposits = (
        Contribution.query
        .options(
            joinedload(Contribution.member)
            .joinedload(Member.user_account)
            .subqueryload(User.image)
        )
        .order_by(Contribution.trans_date.desc())
        .limit(10)
        .all()
    )
    
    recent_members = (
        Member.query
        .options(
            joinedload(Member.user_account)
            .subqueryload(User.image)
        )
        .order_by(Member.created_at.desc())
        .limit(5)
        .all()
    )

    total_deposits = sum(d.amount or 0 for d in recent_deposits)
    unique_members = len(set(d.member_id for d in recent_deposits))
    unique_payment_types = len(set(d.payment_type.value for d in recent_deposits if d.payment_type))

    # Limit members query and eager load images - only need for dropdown
    all_members = (
        Member.query
        .with_entities(Member.id, Member.firstname, Member.lastname, Member.surname)
        .order_by(Member.created_at.desc())
        .limit(50)
        .all()
    )
    
    # Get current user and member profile
    user = User.query.get_or_404(current_user.id)
    member = user.member_profile
    
    # Defer image encoding - use URL instead of base64
    member_image_url = None
    if member and member.user_account and member.user_account.image:
        member_image_url = url_for('main.member_image', member_id=member.id)
    
    # Use URL-based images instead of base64 encoding
    for deposit in recent_deposits:
        deposit.member_image_url = None
        if deposit.member and deposit.member.user_account and deposit.member.user_account.image:
            deposit.member_image_url = url_for('main.member_image', member_id=deposit.member.id)
    
    return render_template('admin_dashboard.html',
                         name=current_user.first_name,
                         contact=current_user.phone_num,
                         email=current_user.role.value,
                         total_members=total_members,
                         total_contributions=total_contributions,
                         total_events=total_events,
                         recent_members=recent_members,
                         recent_deposits=recent_deposits,
                         member=member,
                         member_image_url=member_image_url,
                         total_deposits=total_deposits,
                         unique_members=unique_members,
                         unique_payment_types=unique_payment_types,
                         all_members=all_members,
                         total_spouses=total_spouses,
                         total_children=total_children)

@main.route('/member/<int:member_id>/image')
@login_required
def member_image(member_id):
    """Serve member profile image efficiently."""
    member = Member.query.get_or_404(member_id)
    if member.user_account and member.user_account.image:
        img = member.user_account.image[0]
        if img and img.image:
            return Response(img.image, mimetype=get_image_mime_type(img.image))
    return redirect(url_for('static', filename='img/default-avatar.png'))

@main.route('/profile')
@login_required
def profile():
    user = User.query.get_or_404(current_user.id)
    img = user.image
    if not img:
        return redirect(url_for('main.upload_file'))

    # read image data from db back to form a rendable in html
    image_list = []
    for user_img in img:
        image = base64.b64encode(user_img.image).decode('ascii')
        image_list.append(image)

    # Detect MIME type for the profile avatar data URL
    image_mime_type = 'image/jpeg'
    if img and len(img) > 0 and img[0].image:
        image_mime_type = get_image_mime_type(img[0].image)

    # Get the first image for the update button
    first_img = img[0] if img else None

    # Get member profile and contributions
    member = user.member_profile
    contributions = []
    total_contributions = "Ksh. 0"
    spouses = []
    children = []
    all_children = []
    if member:
        contributions = sorted(
            member.contribute,
            key=lambda c: (c.trans_date is not None, c.trans_date),
            reverse=True,
        )
        total_contributions = "Ksh. {:,}".format(sum(c.amount or 0 for c in contributions))
        spouses = member.spouse
        children = member.child
        all_children = list(member.child)
        for spouse in spouses:
            for child in spouse.child:
                if child.id not in [c.id for c in all_children]:
                    all_children.append(child)

    total_amount = sum(c.amount or 0 for c in contributions)
    dated = [c for c in contributions if c.trans_date]
    payment_breakdown = {}
    for contribution in contributions:
        label = contribution.payment_type.value if contribution.payment_type else 'Other'
        entry = payment_breakdown.setdefault(label, {'count': 0, 'amount': 0})
        entry['count'] += 1
        entry['amount'] += contribution.amount or 0

    # Engagement metrics
    from collections import defaultdict
    from datetime import datetime, timedelta
    monthly_contributions = defaultdict(int)
    for c in contributions:
        if c.trans_date:
            month_key = c.trans_date.strftime('%Y-%m')
            monthly_contributions[month_key] += 1
    
    active_months = len(monthly_contributions)
    avg_per_month = round(len(contributions) / active_months, 1) if active_months else 0
    
    # Calculate streak (consecutive months with contributions)
    streak = 0
    if monthly_contributions:
        today = datetime.now()
        current_month = today.replace(day=1)
        check_month = current_month
        while True:
            if check_month.strftime('%Y-%m') in monthly_contributions:
                streak += 1
                check_month = check_month - timedelta(days=1)
                check_month = check_month.replace(day=1)
            else:
                break
            if streak > 24:
                break

    profile_stats = {
        'total_amount': total_amount,
        'count': len(contributions),
        'average': int(total_amount / len(contributions)) if contributions else 0,
        'last_date': dated[0].trans_date if dated else None,
        'first_date': dated[-1].trans_date if dated else None,
        'payment_breakdown': dict(sorted(payment_breakdown.items())),
        'family_count': len(spouses) + len(all_children),
        'spouse_count': len(spouses),
        'children_count': len(all_children),
        'active_months': active_months,
        'avg_per_month': avg_per_month,
        'streak': streak,
    }

    # Profile completeness: highlight what the member still needs to provide
    checks = [
        ('Profile photo', bool(image_list)),
        ('First name', bool(user.first_name)),
        ('Surname', bool(user.surname)),
        ('Email address', bool(user.email)),
        ('Phone number', bool(user.phone_num)),
        ('Member record', member is not None),
        ('Family details', bool(spouses or all_children)),
    ]
    completed = [label for label, ok in checks if ok]
    missing = [label for label, ok in checks if not ok]
    completeness = {
        'percent': int(round(len(completed) / len(checks) * 100)),
        'completed': len(completed),
        'total': len(checks),
        'missing': missing,
    }

    # Professional summary data
    summary_data = {
        'member_since': member.created_at.strftime('%B %d, %Y') if member and member.created_at else None,
        'primary_payment': max(payment_breakdown.items(), key=lambda x: x[1]['amount'])[0] if payment_breakdown else None,
        'total_family': len(spouses) + len(all_children),
        'engagement_score': min(100, (active_months * 5) + (len(contributions) * 2) + (len(spouses) * 5) + (len(all_children) * 3)),
    }

    return render_template('profile.html',
                         user = user,
                         name = current_user.first_name,
                         contact = current_user.phone_num,
                         email = current_user.role.value,
                         image_list=image_list,
                         image_mime_type=image_mime_type,
                         img = first_img,
                         member=member,
                         contributions=contributions,
                         total_contributions=total_contributions,
                         spouses=spouses,
                         children=children,
                         all_children=all_children,
                         profile_stats=profile_stats,
                         completeness=completeness,
                         summary_data=summary_data)

upload_folder = os.path.join('static')

def gen_file_name(filename):
    """
    If file was exist already, rename it and return a new name
    """
    filename = current_app.config['UPLOAD_FOLDER'] 

    return filename

@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    user = User.query.get_or_404(current_user.id)
   
    if request.method == 'POST':
        file = request.files['image']
        existing = Images.query.filter_by(user_id=user.id).first()
        if existing:
            existing.name = file.filename
            existing.image = file.read()
            db.session.add(existing)
        else:
            newFile = Images(
                name=file.filename,
                image=file.read(),
                user_id=user.id
            )
            db.session.add(newFile)
        db.session.commit()
        return redirect(url_for('main.profile'))
    return render_template('other.html')

@main.route('/image')
def get_images():
    images = db.session.query(Images).all()
    image_list = []
    for img in images:
        image = base64.b64encode(img.image).decode('ascii')
        image_list.append(image)
    return render_template('image.html', image_list=image_list)

@main.route('/avatar')
@login_required
def avatar():
    user = User.query.get_or_404(current_user.id)
    try:
        img = user.image
        image_data = None
        
        if img and len(img) > 0:
            image_data = img[0].image
        
        if not image_data:
            initial = user.first_name[0].upper() if user.first_name else '?'
            svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80">
                <rect width="80" height="80" fill="%23667eea" rx="40"/>
                <text x="40" y="40" text-anchor="middle" dy=".35em" fill="white" font-family="Arial,sans-serif" font-size="32" font-weight="700">{initial}</text>
            </svg>'''
            return Response(svg, mimetype='image/svg+xml')
        
        mime_type = 'image/jpeg'
        if isinstance(image_data, bytes):
            if image_data.startswith(b'\xff\xd8\xff'):
                mime_type = 'image/jpeg'
            elif image_data.startswith(b'\x89PNG\r\n\x1a\n'):
                mime_type = 'image/png'
            elif image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a'):
                mime_type = 'image/gif'
            elif image_data.startswith(b'RIFF') and len(image_data) > 12 and image_data[8:12] == b'WEBP':
                mime_type = 'image/webp'

        # Serve the raw bytes so <img src="/avatar"> renders in every browser
        return Response(image_data, mimetype=mime_type, headers={'Cache-Control': 'private, max-age=300'})
    except Exception:
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80">
            <rect width="80" height="80" fill="%23667eea" rx="40"/>
            <text x="40" y="40" text-anchor="middle" dy=".35em" fill="white" font-family="Arial,sans-serif" font-size="32" font-weight="700">?</text>
        </svg>'''
        return Response(svg, mimetype='image/svg+xml')

# @main.route('/download')
# def download():
#     file_data = Images.query.filter_by(id=1).first()

#     return send_file(io.BytesIO(file_data.image),
# attachment_filename='user.jpg',as_attachment=True) 

@main.route('/<int:img_id>/new_upload', methods=['GET', 'POST'])
def uploadNew(img_id):
    user = User.query.get_or_404(current_user.id)
    image = Images.query.get_or_404(img_id)
    if request.method == 'POST':
        file = request.files['image']
        # newFile=Images(
        # name=file.filename,
        # image=file.read()
        # )
        image.name = file.filename
        image.image = file.read()

        db.session.add(image)
        db.session.commit()
        return redirect(url_for('main.profile'))
    return render_template('other.html')

@main.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get_or_404(current_user.id)
    
    first_name = request.form.get('first_name', '').strip()
    surname = request.form.get('surname', '').strip()
    phone_num = request.form.get('phone_num', '').strip()
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if first_name:
        user.first_name = first_name
    if surname:
        user.surname = surname
    if phone_num:
        user.phone_num = phone_num
    
    if new_password:
        if not current_password:
            flash('Current password is required to change password.', 'danger')
            return redirect(url_for('main.profile'))
        
        if not user.verify_passwords(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('main.profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('main.profile'))
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('main.profile'))
        
        user.passwords = new_password
        flash('Password updated successfully!', 'success')
    
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('main.profile'))

@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get_or_404(current_user.id)
    member = user.member_profile
    
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        surname = request.form.get('surname', '').strip()
        phone_num = request.form.get('phone_num', '').strip()
        email = request.form.get('email', '').strip()
        
        if not first_name or not surname:
            flash('First name and surname are required.', 'danger')
            return redirect(url_for('main.edit_profile'))
        
        existing_email = User.query.filter(User.email == email, User.id != user.id).first()
        if existing_email:
            flash('Email address is already in use by another account.', 'danger')
            return redirect(url_for('main.edit_profile'))
        
        user.first_name = first_name
        user.surname = surname
        user.phone_num = phone_num
        user.email = email
        
        if member:
            member.firstname = first_name
            member.surname = surname
            member.phone_num = phone_num
            member.email = email
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('edit_profile.html', user=user, member=member)

@main.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = User.query.get_or_404(current_user.id)
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('main.change_password'))
        
        if not user.verify_passwords(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('main.change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('main.change_password'))
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('main.change_password'))
        
        user.passwords = new_password
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('change_password.html', user=user)

@main.route('/about')
def about():
    member_count = Member.query.count()
    event_count = CommunityEvent.query.count()
    total_contrib = db.session.query(db.func.coalesce(db.func.sum(Contribution.amount), 0)).scalar() or 0
    return render_template('about.html',
                         member_count=member_count,
                         event_count=event_count,
                         total_contrib=int(total_contrib))

FAQ_CATEGORY_ICONS = {
    'general': '📋',
    'membership': '🪪',
    'contributions': '💰',
    'deposits': '💰',
    'events': '🎉',
    'family': '👨‍👩‍👧‍👦',
    'account': '👤',
    'support': '🛟',
    'payments': '💳',
    'reports': '📊',
}


@main.route('/faq')
def faq():
    """Public knowledge base, grouped by category with optional search."""
    search = request.args.get('q', '').strip()
    active_category = request.args.get('category', '').strip()

    all_faqs = FAQ.query.order_by(FAQ.category.asc(), FAQ.created_at.asc()).all()

    faqs = all_faqs
    if search:
        needle = search.lower()
        faqs = [
            f for f in faqs
            if needle in (f.question or '').lower()
            or needle in (f.answer or '').lower()
            or needle in (f.category or '').lower()
        ]
    if active_category:
        faqs = [f for f in faqs if (f.category or 'General') == active_category]

    groups = {}
    for item in faqs:
        groups.setdefault(item.category or 'General', []).append(item)

    category_groups = [
        {
            'name': name,
            'icon': FAQ_CATEGORY_ICONS.get(name.lower(), '📁'),
            'faqs': items,
            'count': len(items),
        }
        for name, items in sorted(groups.items(), key=lambda pair: pair[0].lower())
    ]

    all_category_counts = {}
    for item in all_faqs:
        key = item.category or 'General'
        all_category_counts[key] = all_category_counts.get(key, 0) + 1

    categories = [
        {
            'name': name,
            'icon': FAQ_CATEGORY_ICONS.get(name.lower(), '📁'),
            'count': count,
        }
        for name, count in sorted(all_category_counts.items(), key=lambda pair: pair[0].lower())
    ]

    stats = {
        'total': len(all_faqs),
        'categories': len(categories),
        'matching': len(faqs),
    }

    return render_template(
        'faq.html',
        faqs=faqs,
        category_groups=category_groups,
        categories=categories,
        stats=stats,
        search=search,
        active_category=active_category,
    )

@main.route('/contact')
def contact():
    return render_template('contact.html')