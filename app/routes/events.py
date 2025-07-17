from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Event, Club, EventRegistration, User
from app import db
from sqlalchemy import desc

bp = Blueprint('events', __name__)

def is_htmx_request():
    """Check if the request is from HTMX"""
    return request.headers.get('HX-Request') == 'true'

@bp.route('/<int:event_id>')
def detail(event_id):
    """Event detail page"""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is registered
    is_registered = False
    if current_user.is_authenticated:
        is_registered = event.is_user_registered(current_user.id)
    
    return render_template('events/detail.html', event=event, is_registered=is_registered)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new event (club managers only)"""
    if not current_user.is_club_manager():
        flash('Access denied. Club manager privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    club = current_user.club
    if not club:
        flash('No club assigned. Please contact admin.', 'error')
        return redirect(url_for('dashboard.club_manager'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date_time')
        location = request.form.get('location')
        registration_deadline_str = request.form.get('registration_deadline')
        max_participants = request.form.get('max_participants', 100, type=int)
        
        # Validation
        errors = []
        
        if not all([title, description, date_str, location, registration_deadline_str]):
            errors.append('Please fill in all required fields.')
        
        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            reg_deadline = datetime.strptime(registration_deadline_str, '%Y-%m-%dT%H:%M')
            
            if event_date <= datetime.utcnow():
                errors.append('Event date must be in the future.')
            
            if reg_deadline >= event_date:
                errors.append('Registration deadline must be before event date.')
                
            if reg_deadline <= datetime.utcnow():
                errors.append('Registration deadline must be in the future.')
                
        except ValueError:
            errors.append('Invalid date format.')
        
        if max_participants < 1:
            errors.append('Maximum participants must be at least 1.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('events/create.html', club=club)
        
        # Create event
        event = Event(
            title=title,
            description=description,
            date_time=event_date,
            location=location,
            registration_deadline=reg_deadline,
            max_participants=max_participants,
            club_id=club.id,
            created_by=current_user.id
        )
        
        try:
            db.session.add(event)
            db.session.commit()
            flash('Event created successfully! It will be visible after admin approval.', 'success')
            return redirect(url_for('dashboard.club_manager'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to create event. Please try again.', 'error')
    
    return render_template('events/create.html', club=club)

@bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    """Edit event (club managers and admin only)"""
    event = Event.query.get_or_404(event_id)
    
    if not (current_user.is_admin() or current_user.can_manage_club(event.club_id)):
        flash('Access denied.', 'error')
        return redirect(url_for('events.detail', event_id=event_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date_time')
        location = request.form.get('location')
        registration_deadline_str = request.form.get('registration_deadline')
        max_participants = request.form.get('max_participants', type=int)
        
        # Validation (similar to create)
        errors = []
        
        if not all([title, description, date_str, location, registration_deadline_str]):
            errors.append('Please fill in all required fields.')
        
        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            reg_deadline = datetime.strptime(registration_deadline_str, '%Y-%m-%dT%H:%M')
            
            if reg_deadline >= event_date:
                errors.append('Registration deadline must be before event date.')
                
        except ValueError:
            errors.append('Invalid date format.')
        
        if max_participants < event.registration_count:
            errors.append(f'Maximum participants cannot be less than current registrations ({event.registration_count}).')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('events/edit.html', event=event)
        
        # Update event
        event.title = title
        event.description = description
        event.date_time = event_date
        event.location = location
        event.registration_deadline = reg_deadline
        event.max_participants = max_participants
        
        # Reset approval if not admin
        if not current_user.is_admin():
            event.is_approved = False
        
        try:
            db.session.commit()
            message = 'Event updated successfully!'
            if not current_user.is_admin() and not event.is_approved:
                message += ' Changes require admin approval.'
            flash(message, 'success')
            return redirect(url_for('events.detail', event_id=event_id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update event. Please try again.', 'error')
    
    return render_template('events/edit.html', event=event)

@bp.route('/<int:event_id>/register', methods=['POST'])
@login_required
def register(event_id):
    """Register for event"""
    event = Event.query.get_or_404(event_id)
    
    # Check if registration is open
    if not event.is_registration_open:
        flash('Registration is not open for this event.', 'error')
        if is_htmx_request():
            is_registered = event.is_user_registered(current_user.id)
            return render_template('events/_registration_section.html', event=event, is_registered=is_registered)
        return redirect(url_for('events.detail', event_id=event_id))
    
    # Check if already registered
    if event.is_user_registered(current_user.id):
        flash('You are already registered for this event.', 'warning')
        if is_htmx_request():
            is_registered = True
            return render_template('events/_registration_section.html', event=event, is_registered=is_registered)
        return redirect(url_for('events.detail', event_id=event_id))
    
    # Check if event is full
    if event.seats_available <= 0:
        flash('This event is full.', 'error')
        if is_htmx_request():
            is_registered = False
            return render_template('events/_registration_section.html', event=event, is_registered=is_registered)
        return redirect(url_for('events.detail', event_id=event_id))
    
    # Create registration
    registration = EventRegistration(
        user_id=current_user.id,
        event_id=event_id
    )
    
    try:
        db.session.add(registration)
        db.session.commit()
        flash('Successfully registered for the event!', 'success')
        if is_htmx_request():
            # Refresh the event object to get updated registration count
            db.session.refresh(event)
            is_registered = True
            return render_template('events/_registration_section.html', event=event, is_registered=is_registered)
    except Exception as e:
        db.session.rollback()
        flash('Registration failed. Please try again.', 'error')
        if is_htmx_request():
            is_registered = False
            return render_template('events/_registration_section.html', event=event, is_registered=is_registered)
    
    return redirect(url_for('events.detail', event_id=event_id))

@bp.route('/<int:event_id>/unregister', methods=['POST'])
@login_required
def unregister(event_id):
    """Unregister from event"""
    event = Event.query.get_or_404(event_id)
    
    registration = EventRegistration.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if not registration:
        flash('You are not registered for this event.', 'warning')
        if is_htmx_request():
            is_registered = False
            return render_template('events/_registration_section.html', event=event, is_registered=is_registered)
        return redirect(url_for('events.detail', event_id=event_id))
    
    try:
        db.session.delete(registration)
        db.session.commit()
        flash('Successfully unregistered from the event.', 'success')
        if is_htmx_request():
            # Refresh the event object to get updated registration count
            db.session.refresh(event)
            is_registered = False
            return render_template('events/_registration_section.html', event=event, is_registered=is_registered)
    except Exception as e:
        db.session.rollback()
        flash('Unregistration failed. Please try again.', 'error')
        if is_htmx_request():
            is_registered = True
            return render_template('events/_registration_section.html', event=event, is_registered=is_registered)
    
    return redirect(url_for('events.detail', event_id=event_id))

@bp.route('/<int:event_id>/participants')
@login_required
def participants(event_id):
    """View event participants (club managers and admin only)"""
    event = Event.query.get_or_404(event_id)
    
    if not (current_user.is_admin() or current_user.can_manage_club(event.club_id)):
        flash('Access denied.', 'error')
        return redirect(url_for('events.detail', event_id=event_id))
    
    participants = db.session.query(User).join(EventRegistration).filter(
        EventRegistration.event_id == event_id
    ).order_by(User.full_name).all()
    
    return render_template('events/participants.html', event=event, participants=participants)

@bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete(event_id):
    """Delete event (club managers and admin only)"""
    event = Event.query.get_or_404(event_id)
    
    if not (current_user.is_admin() or current_user.can_manage_club(event.club_id)):
        flash('Access denied.', 'error')
        return redirect(url_for('events.detail', event_id=event_id))
    
    try:
        # Soft delete
        event.is_active = False
        db.session.commit()
        flash('Event deleted successfully.', 'success')
        
        if current_user.is_admin():
            return redirect(url_for('dashboard.manage_events'))
        else:
            return redirect(url_for('dashboard.club_manager'))
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete event. Please try again.', 'error')
        return redirect(url_for('events.detail', event_id=event_id))

@bp.route('/<int:event_id>/approve', methods=['POST'])
@login_required
def approve(event_id):
    """Approve event (admin only)"""
    if not current_user.is_admin():
        if is_htmx_request():
            return '<div class="alert alert-danger">Access denied</div>', 403
        return jsonify({'error': 'Access denied'}), 403
    
    event = Event.query.get_or_404(event_id)
    event.is_approved = True
    
    try:
        db.session.commit()
        if is_htmx_request():
            return '<div class="alert alert-success fade show"><i class="bi bi-check-circle"></i> Event approved successfully</div>'
        return jsonify({'success': True, 'message': 'Event approved successfully'})
    except Exception as e:
        db.session.rollback()
        if is_htmx_request():
            return '<div class="alert alert-danger fade show"><i class="bi bi-x-circle"></i> Failed to approve event</div>'
        return jsonify({'error': 'Failed to approve event'}), 500

@bp.route('/<int:event_id>/reject', methods=['POST'])
@login_required
def reject(event_id):
    """Reject event (admin only)"""
    if not current_user.is_admin():
        if is_htmx_request():
            return '<div class="alert alert-danger">Access denied</div>', 403
        return jsonify({'error': 'Access denied'}), 403
    
    event = Event.query.get_or_404(event_id)
    event.is_active = False
    
    try:
        db.session.commit()
        if is_htmx_request():
            return '<div class="alert alert-warning fade show"><i class="bi bi-x-circle"></i> Event rejected successfully</div>'
        return jsonify({'success': True, 'message': 'Event rejected successfully'})
    except Exception as e:
        db.session.rollback()
        if is_htmx_request():
            return '<div class="alert alert-danger fade show"><i class="bi bi-x-circle"></i> Failed to reject event</div>'
        return jsonify({'error': 'Failed to reject event'}), 500 