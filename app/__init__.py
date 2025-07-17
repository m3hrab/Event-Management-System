import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Setup logging for production
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/duet_events.log', maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('DUET Events startup')
    
    # Create upload directory
    upload_dir = os.path.join(app.instance_path, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create static directory
    static_dir = os.path.join(app.root_path, 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # Add custom Jinja2 filters
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks"""
        if text:
            return text.replace('\n', '<br>')
        return text
    
    # Register blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.events import bp as events_bp
    app.register_blueprint(events_bp, url_prefix='/events')
    
    from app.routes.clubs import bp as clubs_bp
    app.register_blueprint(clubs_bp, url_prefix='/clubs')
    
    from app.routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    # Create database tables
    with app.app_context():
        try:
            # Ensure the database directory exists
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            if db_url.startswith('sqlite:///'):
                db_path = db_url.replace('sqlite:///', '')
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
            
            db.create_all()
            
            # Create default admin user and clubs if they don't exist
            from app.models import User, Club
            
            # Create admin user
            admin = User.query.filter_by(email='admin@duet.ac.bd').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@duet.ac.bd',
                    full_name='DUET Admin',
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
            
            # Create default clubs
            clubs_data = [
                {'name': 'DUET Computer Society', 'acronym': 'DUETCS', 'description': 'The premier technology and programming club of DUET'},
                {'name': 'DUET Robotics Club', 'acronym': 'DRC', 'description': 'Advancing robotics and automation at DUET'},
                {'name': 'DUET English Language Club', 'acronym': 'DELC', 'description': 'Promoting English language and literature at DUET'}
            ]
            
            for club_data in clubs_data:
                existing_club = Club.query.filter_by(acronym=club_data['acronym']).first()
                if not existing_club:
                    club = Club(**club_data)
                    db.session.add(club)
            
            db.session.commit()
            
        except Exception as e:
            app.logger.error(f"Database initialization error: {e}")
            # Don't fail the app startup, just log the error
    
    return app 