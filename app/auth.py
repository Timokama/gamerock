from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from .user import User
from .image import Images
from . import db
from .level import AccessLevel
from app.models.register import Member
from app.models.spouse import Spouse
from app.models.child import Child

auth = Blueprint('auth', __name__)
def get_family_member_redirect(user):
    """
    Query spouse and child tables for user's identifier.
    If found in either, return redirect to family dashboard.
    Otherwise, return None to use standard redirect logic.
    """
    if not user or not user.is_authenticated:
        return None
    
    # 1. Query spouse table for user's unique identifier
    spouse_record = Spouse.query.filter_by(user_id=user.id).first()
    if spouse_record and spouse_record.member_id:
        return redirect(url_for('register.dashboard_member', member_id=spouse_record.member_id))
    
    # 2. Query child table for user's unique identifier
    child_record = Child.query.filter_by(user_id=user.id).first()
    if child_record and child_record.member_id:
        return redirect(url_for('register.dashboard_member', member_id=child_record.member_id))
    
    # 3. No match in spouse or child tables
    return None


@auth.route('/', methods=['POST', 'GET'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))
    level = AccessLevel
    detected_role = None
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please enter your email address.', 'danger')
            return redirect(url_for('auth.index'))
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No account found with that email address.', 'danger')
            return redirect(url_for('auth.index'))
        detected_role = user.role.value
        session['auth_email'] = email
        session['auth_user_id'] = user.id
        return redirect(url_for('auth.login', role=detected_role))
    return render_template('index.html', level=level, detected_role=detected_role)

# @auth.route('/login')
# def login():
     


@auth.route('/<role>/login', methods=['POST', 'GET'])
def login(role):
    level = AccessLevel
    session_email = session.get('auth_email')
    if request.method == 'POST':
        email = request.form.get('email') or session_email
        password = request.form.get('password')
        
        # Validate role parameter from URL - accept both enum names (SPOUSE) and values (Spouse)
        role_enum = None
        role_upper = role.upper()
        if role_upper in AccessLevel.__members__:
            role_enum = AccessLevel[role_upper]
        elif role in AccessLevel.__members__:
            role_enum = AccessLevel[role]
        else:
            # Try matching by enum value (case-insensitive)
            for member in AccessLevel:
                if member.value.lower() == role.lower():
                    role_enum = member
                    break
        
        user_id = session.get('auth_user_id')
        if user_id:
            user = User.query.filter_by(id=user_id, email=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login', role=role))

        # Role parameter from URL is just a hint; allow any valid user to log in
        # The actual role-based redirect happens after successful authentication below

        # Check if user is a spouse/child by querying relationship tables directly
        is_spouse = Spouse.query.filter_by(user_id=user.id).first() is not None
        is_child = Child.query.filter_by(user_id=user.id).first() is not None
        is_family_member = is_spouse or is_child
        
        # Auto-approve spouse/child accounts (they should always be active)
        if is_family_member and user.status != 'active':
            user.status = 'active'
            # Also fix the role if it's wrong
            if is_spouse and user.role != AccessLevel.SPOUSE:
                user.role = AccessLevel.SPOUSE
            elif is_child and user.role != AccessLevel.CHILD:
                user.role = AccessLevel.CHILD
            user.is_primary_account = False
            user.family_relation_type = 'spouse' if is_spouse else 'child'
            db.session.commit()
        
        if user.status != 'active':
            flash('Your account is pending approval. Please wait for an administrator to approve your account.', 'warning')
            return redirect(url_for('auth.login', role=role))

        login_user(user)
        session.pop('auth_email', None)
        session.pop('auth_user_id', None)
        
        # Admin/Developer users should always go to admin dashboard
        if user.role in (AccessLevel.DEVEL, AccessLevel.ADMIN):
            return redirect(url_for('home.home'))
        
        # Staff roles go to staff dashboard
        if user.role in (AccessLevel.WELFARE_OFFICER, AccessLevel.TREASURER, AccessLevel.SECRETARY, AccessLevel.CHAIRPERSON):
            return redirect(url_for('home.home'))
        
        # Primary member (USER) goes to user dashboard (home interface)
        if user.role == AccessLevel.USER:
            return redirect(url_for('home.home'))
        
        # Family members (spouse/child) go to family dashboard
        if user.role in (AccessLevel.SPOUSE, AccessLevel.CHILD):
            return redirect(url_for('register.dashboard'))
        
        # Fallback
        return redirect(url_for('home.home'))
    return render_template('login.html', level=level, role=role, session_email=session_email)
@auth.route('/signup')
def signup():
    level = AccessLevel
    return render_template('signup.html', level=level)

@auth.route('/signup', methods=['POST'])
def signup_post():
    surname = request.form.get('surname')
    first_name = request.form.get('first_name')
    middle_name = request.form.get('middle_name')
    phone_num = request.form.get('phone_num')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    date_of_birth = request.form.get('date_of_birth')
    id_number = request.form.get('id_number')

    if not first_name or not surname:
        flash('First name and surname are required.', 'danger')
        return redirect(url_for('auth.signup'))

    if not email:
        flash('Email address is required.', 'danger')
        return redirect(url_for('auth.signup'))

    if not password:
        flash('Password is required.', 'danger')
        return redirect(url_for('auth.signup'))

    if password != confirm_password:
        flash('Passwords do not match.', 'danger')
        return redirect(url_for('auth.signup'))

    if len(password) < 6:
        flash('Password must be at least 6 characters long.', 'danger')
        return redirect(url_for('auth.signup'))

    # Only Primary Member account type is supported
    role_enum = AccessLevel.USER
    account_status = 'pending'
    is_primary = True
    family_relation = 'primary'

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email address already exists', 'danger')
        return redirect(url_for('auth.signup'))

    existing_member_email = Member.query.filter_by(email=email).first()
    if existing_member_email:
        flash('Email already exists. Please use a different email.', 'danger')
        return redirect(url_for('auth.signup'))

    member_id_number = None
    if id_number and str(id_number).strip():
        try:
            member_id_number = int(str(id_number).strip())
        except (ValueError, TypeError):
            member_id_number = None

    if member_id_number:
        existing_user_id = User.query.filter_by(id_number=member_id_number).first()
        if existing_user_id:
            flash('ID number already exists. Please check your details.', 'danger')
            return redirect(url_for('auth.signup'))
        existing_member = Member.query.filter_by(id_number=member_id_number).first()
        if existing_member:
            flash('ID number already exists. Please check your details.', 'danger')
            return redirect(url_for('auth.signup'))

    dob = None
    if date_of_birth:
        try:
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass

    new_user = User(
        surname=surname,
        first_name=first_name,
        email=email,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        phone_num=phone_num,
        id_number=member_id_number,
        date_of_birth=dob,
        role=role_enum,
        status=account_status,
        is_primary_account=is_primary,
        family_relation_type=family_relation,
    )

    db.session.add(new_user)
    db.session.commit()

    flash('Your account has been created and is pending approval. Please wait for an administrator to approve your account.', 'info')
    return redirect(url_for('auth.signup'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.index'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.index'))

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('auth.index'))

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No account found with that email address.', 'danger')
            return redirect(url_for('auth.index'))

        user.password = generate_password_hash(password, method='pbkdf2:sha256')
        db.session.commit()
        flash('Password has been reset successfully. You can now login.', 'success')
        return redirect(url_for('auth.index'))

    return render_template('forgot_password.html')

# @auth.route('/<int:user_id>/changePassword', methods=['POST', 'GET'])
# @login_required
# def password(user_id):
#     user = User.query.get_or_404(user_id)
#     #code to validate and user to database goes here
#     password = generate_password_hash(password=user.password)
#     passwrd = check_password_hash(user.password, password)
#     if request.method == 'POST':
#         passwords = request.form.get('password')
#         user.password = passwords

#         db.session.add(user)
#         db.session.commit()
#         return redirect(url_for('main.profie'))
#     return render_template('password.html', user = user, passwrd = passwrd)


# @auth.route("/passwordchange", methods=["GET", "POST"])
# @login_required
# def changepassword():
#     # import mysql.connector as sqltor
#     # mycon=sqltor.connect(host="localhost",user="root",passwd="root",database="gamerock")
#     # db=mycon.cursor
#     """"Change users' password"""
#
#     user = User.query.get_or_404(current_user.id)
#     if request.method == "POST":
#         newPassword = request.form.get("newPassword")
#         newConfirmation = request.form.get("newConfirmation")
#
#         # Ensure that the user has inputted
#         if (not newPassword) or (not newConfirmation):
#             return apology("Please fill all of the provided fields!", 400)
#
#         # Check to see if password confirmation were the same or not
#         if newPassword != newConfirmation:
#             return apology("password did not match with password (again)", 400)
#         
#         user_id = user.id
#         
#         newHash = generate_password_hash("newPassword")
#
#         # user.password = newHash
#         # db.session.add(user)
#         # db.session.commit()
#         db.execute("UPDATE user SET hash = ? WHERE id = ?", newHash, user_id)

@auth.route('/debug/user/<email>')
@login_required
def debug_user(email):
    """Debug endpoint to check user status and role."""
    if current_user.role.name not in ['DEVEL', 'ADMIN']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'surname': user.surname,
        'role': user.role.name,
        'role_value': user.role.value,
        'status': user.status,
        'is_primary_account': user.is_primary_account,
        'family_relation_type': user.family_relation_type,
        'primary_member_id': user.primary_member_id,
        'has_spouse': user.spouse is not None,
        'has_child': user.child is not None,
        'spouse_member_id': user.spouse.member_id if user.spouse else None,
        'child_member_id': user.child.member_id if user.child else None,
        'member_profile_id': user.member_profile.id if user.member_profile else None,
    })
#         passwordChange = check_password_hash(newHash, newPassword)

#         print(f'\n\n{passwordChange}\n\n')
#         return redirect("/login")
#     else:
#         return render_template("password.html")
    

