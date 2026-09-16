from flask import Blueprint, render_template, redirect, url_for, request, flash,session
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

def get_primary_member_id():
    """Returns the primary member ID if the current user is a spouse/child of a member."""
    if not current_user.is_authenticated:
        return None
    if current_user.role.name in ['DEVEL', 'ADMIN', 'WELFARE_OFFICER', 'TREASURER']:
        return None
    spouse_link = current_user.spouse
    if spouse_link and spouse_link.member_id:
        return spouse_link.member_id
    child_link = current_user.child
    if child_link and child_link.member_id:
        return child_link.member_id
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
        role_enum = None
        if role in AccessLevel.__members__:
            role_enum = AccessLevel[role]
        else:
            for member in AccessLevel:
                if member.value == role:
                    role_enum = member
                    break
        user_id = session.get('auth_user_id')
        if user_id:
            user = User.query.filter_by(id=user_id, email=email, role=role_enum).first()
        else:
            user = User.query.filter_by(email=email, role=role_enum).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login', role=role))

        if user.status != 'active':
            flash('Your account is pending approval. Please wait for an administrator to approve your account.', 'warning')
            return redirect(url_for('auth.login', role=role))

        login_user(user)
        session.pop('auth_email', None)
        session.pop('auth_user_id', None)
        
        # Check if user is a spouse/child of a primary member
        primary_member_id = get_primary_member_id()
        if primary_member_id:
            return redirect(url_for('register.dashboard_member', member_id=primary_member_id))
        
        # Regular user redirect
        if current_user.role == AccessLevel.USER:
            member = user.member_profile
            if member:
                return redirect(url_for('register.dashboard_member', member_id=member.id))
        
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
    last_name = request.form.get('last_name')
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

    role_enum = AccessLevel.USER

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
        status='pending',
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

#     user = User.query.get_or_404(current_user.id)
#     if request.method == "POST":
#         newPassword = request.form.get("newPassword")
#         newConfirmation = request.form.get("newConfirmation")

#         # Ensure that the user has inputted
#         if (not newPassword) or (not newConfirmation):
#             return apology("Please fill all of the provided fields!", 400)

#         # Check to see if password confirmation were the same or not
#         if newPassword != newConfirmation:
#             return apology("password did not match with password (again)", 400)
        
#         user_id = user.id
        
#         newHash = generate_password_hash("newPassword")

#         # user.password = newHash
#         # db.session.add(user)
#         # db.session.commit()
#         db.execute("UPDATE user SET hash = ? WHERE id = ?", newHash, user_id)
#         passwordChange = check_password_hash(newHash, newPassword)

#         print(f'\n\n{passwordChange}\n\n')
#         return redirect("/login")
#     else:
#         return render_template("password.html")
    

