from flask import Blueprint, render_template, redirect, url_for, request, flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .user import User
from .image import Images
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # log in code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    #code to validate and user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    contact = request.form.get('contact')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, contact=contact, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

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


@auth.route("/passwordchange", methods=["GET", "POST"])
@login_required
def changepassword():
    # import mysql.connector as sqltor
    # mycon=sqltor.connect(host="localhost",user="root",passwd="root",database="gamerock")
    # db=mycon.cursor
    """"Change users' password"""

    user = User.query.get_or_404(current_user.id)
    if request.method == "POST":
        newPassword = request.form.get("newPassword")
        newConfirmation = request.form.get("newConfirmation")

        # Ensure that the user has inputted
        if (not newPassword) or (not newConfirmation):
            return apology("Please fill all of the provided fields!", 400)

        # Check to see if password confirmation were the same or not
        if newPassword != newConfirmation:
            return apology("password did not match with password (again)", 400)
        
        user_id = user.id
        
        newHash = generate_password_hash("newPassword")

        # user.password = newHash
        # db.session.add(user)
        # db.session.commit()
        db.execute("UPDATE user SET hash = ? WHERE id = ?", newHash, user_id)
        passwordChange = check_password_hash(newHash, newPassword)

        print(f'\n\n{passwordChange}\n\n')
        return redirect("/login")
    else:
        return render_template("password.html")
    

