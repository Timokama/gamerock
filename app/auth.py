from flask import Blueprint, render_template, redirect, url_for, request, flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from .user import User
from .image import Images
from . import db
from .level import AccessLevel
from app.models.register import Member
auth = Blueprint('auth', __name__)

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
        user = User.query.filter_by(email=email, role=role_enum).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login', role=role))

        login_user(user)
        session.pop('auth_email', None)
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

    last_name = last_name or first_name

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists', 'danger')
        return redirect(url_for('auth.signup'))

    existing_member = Member.query.filter_by(id_number=id_number).first() if id_number else None
    if existing_member:
        flash('ID number already exists. Please check your details.', 'danger')
        return redirect(url_for('auth.signup'))

    existing_member_email = Member.query.filter_by(email=email).first()
    if existing_member_email:
        flash('Email already exists. Please use a different email.', 'danger')
        return redirect(url_for('auth.signup'))

    role_enum = AccessLevel.USER

    new_user = User(surname=surname, first_name=first_name, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'), role=role_enum)

    db.session.add(new_user)
    db.session.commit()

    dob = None
    if date_of_birth:
        try:
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass

    member_id_number = None
    if id_number and str(id_number).strip():
        try:
            member_id_number = int(str(id_number).strip())
        except (ValueError, TypeError):
            member_id_number = None

    member = Member(
        firstname=first_name,
        lastname=last_name,
        surname=surname,
        date_of_birth=dob,
        phone_num=phone_num,
        email=email,
        id_number=member_id_number,
        user_id=new_user.id,
        added_by=new_user.id,
    )
    db.session.add(member)
    db.session.commit()

    usr = User.query.get(new_user.id)
    login_user(usr)
    return redirect(url_for('home.home'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/forgot-password', methods=['POST'])
def forgot_password():
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
    

