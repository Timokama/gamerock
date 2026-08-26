from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.minutes import bp
from app import db
from app.user import User
from app.level import AccessLevel
from app.models.minutes import Minutes

def can_manage_minutes():
    return current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN', 'SECRETARY']

def is_admin_or_dev():
    return current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN']

@bp.route('/')
@login_required
def index():
    if not can_manage_minutes():
        flash('You do not have permission to view minutes.', 'danger')
        return redirect(url_for('home.home'))
    
    search = request.args.get('search', '')
    meeting_type = request.args.get('meeting_type', '')
    status = request.args.get('status', '')
    
    query = Minutes.query
    
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Minutes.title.ilike(like),
                Minutes.agenda.ilike(like),
                Minutes.decisions.ilike(like)
            )
        )
    
    if meeting_type:
        query = query.filter(Minutes.meeting_type == meeting_type)
    
    if status:
        query = query.filter(Minutes.status == status)
    
    minutes_list = query.order_by(Minutes.meeting_date.desc()).all()
    return render_template('minutes/index.html', minutes_list=minutes_list, search=search, meeting_type=meeting_type, status=status)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not can_manage_minutes():
        flash('You do not have permission to create minutes.', 'danger')
        return redirect(url_for('minutes.index'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        meeting_type = request.form.get('meeting_type', 'General').strip()
        meeting_date_str = request.form.get('meeting_date', '')
        location = request.form.get('location', '').strip()
        agenda = request.form.get('agenda', '').strip()
        discussion = request.form.get('discussion', '').strip()
        decisions = request.form.get('decisions', '').strip()
        action_items = request.form.get('action_items', '').strip()
        next_meeting_date_str = request.form.get('next_meeting_date', '')
        attendees = request.form.get('attendees', '').strip()
        
        if not title or not meeting_date_str:
            flash('Title and meeting date are required.', 'danger')
            return redirect(url_for('minutes.create'))
        
        try:
            meeting_date = datetime.strptime(meeting_date_str, '%Y-%m-%d').date()
            next_meeting_date = datetime.strptime(next_meeting_date_str, '%Y-%m-%d').date() if next_meeting_date_str else None
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('minutes.create'))
        
        minutes_entry = Minutes(
            title=title,
            meeting_type=meeting_type,
            meeting_date=meeting_date,
            location=location,
            agenda=agenda,
            discussion=discussion,
            decisions=decisions,
            action_items=action_items,
            next_meeting_date=next_meeting_date,
            attendees=attendees,
            created_by=current_user.id
        )
        db.session.add(minutes_entry)
        db.session.commit()
        flash('Minutes created successfully.', 'success')
        return redirect(url_for('minutes.index'))
    
    return render_template('minutes/create.html')


@bp.route('/<int:minutes_id>')
@login_required
def view(minutes_id):
    if not can_manage_minutes():
        flash('You do not have permission to view minutes.', 'danger')
        return redirect(url_for('minutes.index'))
    
    minutes_entry = Minutes.query.get_or_404(minutes_id)
    return render_template('minutes/view.html', minutes_entry=minutes_entry)


@bp.route('/<int:minutes_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(minutes_id):
    if not can_manage_minutes():
        flash('You do not have permission to edit minutes.', 'danger')
        return redirect(url_for('minutes.index'))
    
    minutes_entry = Minutes.query.get_or_404(minutes_id)
    
    if request.method == 'POST':
        minutes_entry.title = request.form.get('title', '').strip()
        minutes_entry.meeting_type = request.form.get('meeting_type', 'General').strip()
        meeting_date_str = request.form.get('meeting_date', '')
        minutes_entry.location = request.form.get('location', '').strip()
        minutes_entry.agenda = request.form.get('agenda', '').strip()
        minutes_entry.discussion = request.form.get('discussion', '').strip()
        minutes_entry.decisions = request.form.get('decisions', '').strip()
        minutes_entry.action_items = request.form.get('action_items', '').strip()
        next_meeting_date_str = request.form.get('next_meeting_date', '')
        minutes_entry.attendees = request.form.get('attendees', '').strip()
        minutes_entry.status = request.form.get('status', 'Draft')
        
        if request.form.get('status') == 'Approved' and not minutes_entry.approved_by:
            minutes_entry.approved_by = current_user.id
            minutes_entry.approved_at = datetime.utcnow()
        
        try:
            minutes_entry.meeting_date = datetime.strptime(meeting_date_str, '%Y-%m-%d').date()
            if next_meeting_date_str:
                minutes_entry.next_meeting_date = datetime.strptime(next_meeting_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('minutes.edit', minutes_id=minutes_id))
        
        db.session.commit()
        flash('Minutes updated successfully.', 'success')
        return redirect(url_for('minutes.view', minutes_id=minutes_entry.id))
    
    return render_template('minutes/edit.html', minutes_entry=minutes_entry)


@bp.route('/<int:minutes_id>/delete', methods=['POST'])
@login_required
def delete(minutes_id):
    if not is_admin_or_dev():
        flash('You do not have permission to delete minutes.', 'danger')
        return redirect(url_for('minutes.index'))
    
    minutes_entry = Minutes.query.get_or_404(minutes_id)
    db.session.delete(minutes_entry)
    db.session.commit()
    flash('Minutes deleted successfully.', 'success')
    return redirect(url_for('minutes.index'))
