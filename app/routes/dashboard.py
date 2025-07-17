from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.models import User, Club, Event, EventRegistration
from app import db
from sqlalchemy import desc

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def index():
    """Redirect to appropriate dashboard based on user role"""
    if current_user.is_admin():
        return redirect(url_for('dashboard.admin'))
    elif current_user.is_club_manager():
        return redirect(url_for('dashboard.club_manager'))
    else:
        return redirect(url_for('dashboard.student'))

@bp.route('/admin')
@login_required
def admin():
    """Admin dashboard"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get statistics
    total_users = User.query.count()
    total_clubs = Club.query.filter_by(is_active=True).count()
    total_events = Event.query.filter_by(is_active=True).count()
    pending_events = Event.query.filter_by(is_approved=False, is_active=True).count()
    
    # Get recent events pending approval
    pending_events_list = Event.query.filter_by(
        is_approved=False, 
        is_active=True
    ).order_by(desc(Event.created_at)).limit(5).all()
    
    # Get recent users
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    
    return render_template('dashboard/admin.html',
                         total_users=total_users,
                         total_clubs=total_clubs,
                         total_events=total_events,
                         pending_events=pending_events,
                         pending_events_list=pending_events_list,
                         recent_users=recent_users)

@bp.route('/club-manager')
@login_required
def club_manager():
    """Club manager dashboard"""
    if not current_user.is_club_manager():
        flash('Access denied. Club manager privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get club manager's club
    club = current_user.club
    if not club:
        flash('No club assigned. Please contact admin.', 'error')
        return redirect(url_for('main.index'))
    
    # Get club events
    upcoming_events = Event.query.filter(
        Event.club_id == club.id,
        Event.date_time > datetime.utcnow(),
        Event.is_active == True
    ).order_by(Event.date_time).all()
    
    past_events = Event.query.filter(
        Event.club_id == club.id,
        Event.date_time <= datetime.utcnow(),
        Event.is_active == True
    ).order_by(desc(Event.date_time)).limit(5).all()
    
    pending_events = Event.query.filter(
        Event.club_id == club.id,
        Event.is_approved == False,
        Event.is_active == True
    ).order_by(desc(Event.created_at)).all()
    
    # Get total registrations for club events
    total_registrations = db.session.query(EventRegistration).join(Event).filter(
        Event.club_id == club.id
    ).count()
    
    return render_template('dashboard/club_manager.html',
                         club=club,
                         upcoming_events=upcoming_events,
                         past_events=past_events,
                         pending_events=pending_events,
                         total_registrations=total_registrations)

@bp.route('/student')
@login_required
def student():
    """Student dashboard"""
    # Get user's registered events
    registered_events = db.session.query(Event).join(EventRegistration).filter(
        EventRegistration.user_id == current_user.id,
        Event.is_active == True
    ).order_by(Event.date_time).all()
    
    # Separate upcoming and past events
    upcoming_registered = [e for e in registered_events if e.is_upcoming]
    past_registered = [e for e in registered_events if not e.is_upcoming]
    
    # Get upcoming events not registered for
    registered_event_ids = [e.id for e in registered_events]
    available_events = Event.query.filter(
        Event.is_approved == True,
        Event.date_time > datetime.utcnow(),
        Event.is_active == True,
        ~Event.id.in_(registered_event_ids) if registered_event_ids else True
    ).order_by(Event.date_time).limit(6).all()
    
    return render_template('dashboard/student.html',
                         upcoming_registered=upcoming_registered,
                         past_registered=past_registered,
                         available_events=available_events)

@bp.route('/manage-users')
@login_required
def manage_users():
    """Admin page to manage users"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.full_name.contains(search)) |
            (User.email.contains(search))
        )
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    users = query.order_by(User.created_at.desc()).all()
    clubs = Club.query.filter_by(is_active=True).all()
    
    return render_template('dashboard/manage_users.html',
                         users=users,
                         clubs=clubs,
                         search=search,
                         role_filter=role_filter)

@bp.route('/manage-events')
@login_required
def manage_events():
    """Admin page to manage events"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get all events with filters
    status_filter = request.args.get('status', '')
    club_filter = request.args.get('club', '')
    search = request.args.get('search', '')
    
    query = Event.query
    
    if status_filter:
        if status_filter == 'approved':
            query = query.filter_by(is_approved=True)
        elif status_filter == 'pending':
            query = query.filter_by(is_approved=False)
    
    if club_filter:
        query = query.filter_by(club_id=club_filter)
    
    if search:
        query = query.filter(Event.title.contains(search))
    
    events = query.order_by(desc(Event.created_at)).all()
    clubs = Club.query.filter_by(is_active=True).all()
    
    return render_template('dashboard/manage_events.html',
                         events=events,
                         clubs=clubs,
                         status_filter=status_filter,
                         club_filter=club_filter,
                         search=search)

@bp.route('/manage-clubs')
@login_required
def manage_clubs():
    """Admin page to manage clubs"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get search and filter parameters
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'active')
    
    # Build query
    query = Club.query
    
    if search:
        query = query.filter(
            (Club.name.contains(search)) |
            (Club.acronym.contains(search))
        )
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    # 'all' shows both active and inactive
    
    clubs = query.order_by(Club.created_at.desc()).all()
    
    # Get statistics
    total_clubs = Club.query.count()
    active_clubs = Club.query.filter_by(is_active=True).count()
    clubs_with_managers = Club.query.join(User, Club.id == User.club_id).filter(User.role == 'club_manager').count()
    clubs_without_managers = active_clubs - clubs_with_managers
    
    stats = {
        'total_clubs': total_clubs,
        'active_clubs': active_clubs,
        'inactive_clubs': total_clubs - active_clubs,
        'clubs_with_managers': clubs_with_managers,
        'clubs_without_managers': clubs_without_managers
    }
    
    return render_template('dashboard/manage_clubs.html',
                         clubs=clubs,
                         stats=stats,
                         search=search,
                         status_filter=status_filter)

@bp.route('/club-actions/<int:club_id>', methods=['POST'])
@login_required
def club_actions(club_id):
    """Handle club actions via HTMX (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    action = request.json.get('action')
    club = Club.query.get_or_404(club_id)
    
    try:
        if action == 'toggle_status':
            club.is_active = not club.is_active
            status = 'activated' if club.is_active else 'deactivated'
            
            # If deactivating, remove manager
            if not club.is_active:
                manager = club.get_manager()
                if manager:
                    manager.role = 'student'
                    manager.club_id = None
            
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'Club {status} successfully',
                'new_status': club.is_active
            })
            
        elif action == 'remove_manager':
            manager = club.get_manager()
            if manager:
                manager.role = 'student'
                manager.club_id = None
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': 'Manager removed successfully'
                })
            else:
                return jsonify({'error': 'No manager assigned'}), 400
                
        else:
            return jsonify({'error': 'Invalid action'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Action failed'}), 500

@bp.route('/update-user-role', methods=['POST'])
@login_required
def update_user_role():
    """Update user role (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    user_id = request.json.get('user_id')
    new_role = request.json.get('role')
    club_id = request.json.get('club_id')
    
    if not all([user_id, new_role]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from changing their own role
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot change your own role'}), 400
    
    # Validate role
    if new_role not in ['admin', 'club_manager', 'student']:
        return jsonify({'error': 'Invalid role'}), 400
    
    # If assigning club manager role, ensure club is provided and available
    if new_role == 'club_manager':
        if not club_id:
            return jsonify({'error': 'Club is required for club manager role'}), 400
        
        club = Club.query.get_or_404(club_id)
        existing_manager = club.get_manager()
        
        if existing_manager and existing_manager.id != user.id:
            return jsonify({'error': f'Club already has a manager: {existing_manager.full_name}'}), 400
        
        user.club_id = club_id
    else:
        # If removing club manager role, clear club assignment
        if user.role == 'club_manager':
            user.club_id = None
    
    user.role = new_role
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': f'User role updated to {new_role}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user role'}), 500 