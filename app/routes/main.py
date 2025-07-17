from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from app.models import Event, Club
from app import db
from sqlalchemy import desc

bp = Blueprint('main', __name__)

def is_htmx_request():
    """Check if the request is from HTMX"""
    return request.headers.get('HX-Request') == 'true'

@bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

@bp.route('/')
def index():
    """Landing page showing upcoming approved events"""
    # Get search parameters
    search = request.args.get('search', '')
    club_filter = request.args.get('club', '')
    
    # Base query for approved upcoming events
    query = Event.query.filter(
        Event.is_approved == True,
        Event.date_time > datetime.utcnow(),
        Event.is_active == True
    )
    
    # Apply search filter
    if search:
        query = query.filter(Event.title.contains(search))
    
    # Apply club filter
    if club_filter:
        query = query.filter(Event.club_id == club_filter)
    
    # Get events ordered by date
    events = query.order_by(Event.date_time).limit(12).all()
    
    # Get all clubs for filter dropdown
    clubs = Club.query.filter_by(is_active=True).all()
    
    # Get featured clubs (first 3)
    featured_clubs = clubs[:3]
    
    return render_template('landing.html', 
                         events=events, 
                         clubs=clubs, 
                         featured_clubs=featured_clubs,
                         search=search,
                         club_filter=club_filter)

@bp.route('/about')
def about():
    """About DUET page"""
    clubs = Club.query.filter_by(is_active=True).all()
    return render_template('about.html', clubs=clubs)

@bp.route('/events')
def events():
    """All events page with filtering and search"""
    # Get search parameters
    search = request.args.get('search', '')
    club_filter = request.args.get('club', '')
    status_filter = request.args.get('status', 'upcoming')  # upcoming, past, all
    
    # Base query for approved events
    query = Event.query.filter(
        Event.is_approved == True,
        Event.is_active == True
    )
    
    # Apply status filter
    if status_filter == 'upcoming':
        query = query.filter(Event.date_time > datetime.utcnow())
    elif status_filter == 'past':
        query = query.filter(Event.date_time <= datetime.utcnow())
    
    # Apply search filter
    if search:
        query = query.filter(Event.title.contains(search))
    
    # Apply club filter
    if club_filter:
        query = query.filter(Event.club_id == club_filter)
    
    # Order events
    if status_filter == 'past':
        events = query.order_by(desc(Event.date_time)).all()
    else:
        events = query.order_by(Event.date_time).all()
    
    # Get all clubs for filter dropdown
    clubs = Club.query.filter_by(is_active=True).all()
    
    # Return partial template for HTMX requests
    if is_htmx_request():
        return render_template('events/_events_grid.html', 
                             events=events, 
                             clubs=clubs,
                             search=search,
                             club_filter=club_filter,
                             status_filter=status_filter)
    
    return render_template('events.html', 
                         events=events, 
                         clubs=clubs,
                         search=search,
                         club_filter=club_filter,
                         status_filter=status_filter)