from flask import render_template, url_for
from flask_login import login_required, current_user
from app.home import bp
from app import db
from app.user import User

@bp.route('/')
@login_required
def home():
    return render_template("home.html", contact = current_user.contact, email = current_user.email)