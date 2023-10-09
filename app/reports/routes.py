from flask import render_template, url_for
from app.reports import bp
from flask_login import login_required, current_user
from app.user import User
from app import db
# from app.models.deposit import Deposit
from app.models.contribute import Contribution


@bp.route('/')
@login_required
def index():
    user = User.query.get_or_404(current_user.id)
    contribute = user.contribution
    # deposit = Deposit.query.get_or_404(user)
    total = 0
    count = 0
    for money in contribute:
        for amount in money.deposit:
            total += amount.amount
            count += 1
    
    return render_template("reports/index.html", total = total, members = count, user = user)

@bp.route('/<int:depo_id>/reports')
def reports(depo_id):
    # user = User.query.get_or_404(current_user.id)
    contribute = Contribution.query.get_or_404(depo_id)
    # deposit = Deposit.query.get_or_404(user)
    total = 0
    count = 0
    for money in contribute.deposit:
        total += money.amount
        count += 1
    
    return render_template("reports/reports.html",contribute = contribute, total = total, members = count)