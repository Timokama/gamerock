from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import db

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('home.html', name = current_user.name, contact = current_user.contact, email = current_user.email)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name = current_user.name, contact = current_user.contact, email = current_user.email)
