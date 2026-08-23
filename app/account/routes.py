from flask import render_template, request, redirect, url_for, flash
from app.account import bp
from flask_login import login_required, current_user
from app import db
from app.user import User
from app.models.contribute import Contribution

@bp.route('/')
@login_required
def index():
    user = User.query.get_or_404(current_user.id)
    member = user.member_profile
    if not member:
        flash("No member profile found for your account.")
        return redirect(url_for('main.index'))
    return render_template("contribute/index.html", user = user, member = member)

@bp.route('/create_account/', methods=('GET', 'POST'))
def cont():
    user = User.query.get_or_404(current_user.id)
    if request.method == 'POST':
        cont = Contribution(name=request.form['name'], user=user)

        db.session.add(cont)
        db.session.commit()
        return redirect(url_for('register.index'))

    return render_template('contribute/post.html', user = user)


@bp.route('/contribute/<path:tag_name>/')
def contribute(tag_name):
    user = User.query.get_or_404(current_user.id)
    register = user.family
    
    contribute = Contribution.query.filter_by(name=tag_name).order_by(Contribution.id.desc()).first_or_404()

    return render_template('contribute/tag.html', contribute = contribute, user = user, register = register)


@bp.post('/<int:depo_id>/delete')
def delete(depo_id):
    user = User.query.get_or_404(current_user.id)
    contribute = Contribution.query.get_or_404(depo_id)
    for cont in contribute.deposit:
        db.session.delete(cont)
    db.session.delete(contribute)
    db.session.commit()
    return redirect(url_for('account.index'))