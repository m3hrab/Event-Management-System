from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import Club, User
from app import db

bp = Blueprint('clubs', __name__)

@bp.route('/')
def index():
    """List all clubs"""
    clubs = Club.query.filter_by(is_active=True).all()
    return render_template('clubs/index.html', clubs=clubs)

@bp.route('/<int:club_id>')
def detail(club_id):
    """Club detail page"""
    club = Club.query.get_or_404(club_id)
    upcoming_events = club.get_upcoming_events()
    manager = club.get_manager()
    return render_template('clubs/detail.html', club=club, events=upcoming_events, manager=manager)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new club (admin only)"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('clubs.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        acronym = request.form.get('acronym')
        description = request.form.get('description')
        
        # Validation
        errors = []
        
        if not all([name, acronym]):
            errors.append('Please fill in all required fields.')
        
        if Club.query.filter_by(acronym=acronym).first():
            errors.append('Club acronym already exists.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('clubs/create.html')
        
        # Create club
        club = Club(
            name=name,
            acronym=acronym,
            description=description
        )
        
        try:
            db.session.add(club)
            db.session.commit()
            flash('Club created successfully!', 'success')
            return redirect(url_for('clubs.detail', club_id=club.id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to create club. Please try again.', 'error')
    
    return render_template('clubs/create.html')

@bp.route('/<int:club_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(club_id):
    """Edit club (admin only)"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('clubs.detail', club_id=club_id))
    
    club = Club.query.get_or_404(club_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        acronym = request.form.get('acronym')
        description = request.form.get('description')
        
        # Validation
        errors = []
        
        if not all([name, acronym]):
            errors.append('Please fill in all required fields.')
        
        existing_club = Club.query.filter_by(acronym=acronym).first()
        if existing_club and existing_club.id != club.id:
            errors.append('Club acronym already exists.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('clubs/edit.html', club=club)
        
        # Update club
        club.name = name
        club.acronym = acronym
        club.description = description
        
        try:
            db.session.commit()
            flash('Club updated successfully!', 'success')
            return redirect(url_for('clubs.detail', club_id=club_id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update club. Please try again.', 'error')
    
    return render_template('clubs/edit.html', club=club)

@bp.route('/<int:club_id>/manage', methods=['GET', 'POST'])
@login_required
def manage(club_id):
    """Manage club members and assign manager (admin only)"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('clubs.detail', club_id=club_id))
    
    club = Club.query.get_or_404(club_id)
    current_manager = club.get_manager()
    
    # Get potential managers (students without club assignments or current manager)
    query = User.query.filter_by(role='student', is_active=True)
    
    if current_manager:
        # Include current manager and users without club assignments
        potential_managers = query.filter(
            (User.club_id.is_(None)) | (User.id == current_manager.id)
        ).all()
    else:
        # Only users without club assignments
        potential_managers = query.filter(User.club_id.is_(None)).all()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'assign_manager':
            user_id = request.form.get('user_id', type=int)
            
            if not user_id:
                flash('Please select a user.', 'error')
                return render_template('clubs/manage.html', club=club, 
                                     current_manager=current_manager, 
                                     potential_managers=potential_managers)
            
            user = User.query.get_or_404(user_id)
            
            # Remove current manager role
            if current_manager:
                current_manager.role = 'student'
                current_manager.club_id = None
            
            # Assign new manager
            user.role = 'club_manager'
            user.club_id = club.id
            
            try:
                db.session.commit()
                flash(f'{user.full_name} has been assigned as club manager.', 'success')
                return redirect(url_for('clubs.manage', club_id=club_id))
            except Exception as e:
                db.session.rollback()
                flash('Failed to assign manager. Please try again.', 'error')
        
        elif action == 'remove_manager':
            if current_manager:
                current_manager.role = 'student'
                current_manager.club_id = None
                
                try:
                    db.session.commit()
                    flash('Club manager removed.', 'success')
                    return redirect(url_for('clubs.manage', club_id=club_id))
                except Exception as e:
                    db.session.rollback()
                    flash('Failed to remove manager. Please try again.', 'error')
    
    return render_template('clubs/manage.html', club=club, 
                         current_manager=current_manager, 
                         potential_managers=potential_managers)

@bp.route('/<int:club_id>/delete', methods=['POST'])
@login_required
def delete(club_id):
    """Delete club (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    club = Club.query.get_or_404(club_id)
    
    # Check if club has events
    if club.events.filter_by(is_active=True).count() > 0:
        return jsonify({'error': 'Cannot delete club with active events'}), 400
    
    try:
        # Soft delete
        club.is_active = False
        
        # Remove manager assignment
        manager = club.get_manager()
        if manager:
            manager.role = 'student'
            manager.club_id = None
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Club deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete club'}), 500 