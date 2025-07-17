#!/usr/bin/env python3

# Database initialization script for Render deployment
import os
import sys

def init_database():
    """Initialize the database with proper error handling"""
    try:
        # Set production environment
        os.environ['FLASK_ENV'] = 'production'
        
        # Import after setting environment
        from app import create_app, db
        
        print("Creating Flask app...")
        app = create_app('production')
        
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            
            # Import models after database creation
            from app.models import User, Club
            
            # Create admin user if not exists
            admin = User.query.filter_by(email='admin@duet.ac.bd').first()
            if not admin:
                print("Creating admin user...")
                admin = User(
                    username='admin',
                    email='admin@duet.ac.bd',
                    full_name='DUET Admin',
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
            
            # Create default clubs if they don't exist
            clubs_data = [
                {'name': 'DUET Computer Society', 'acronym': 'DUETCS', 'description': 'The premier technology and programming club of DUET'},
                {'name': 'DUET Robotics Club', 'acronym': 'DRC', 'description': 'Advancing robotics and automation at DUET'},
                {'name': 'DUET English Language Club', 'acronym': 'DELC', 'description': 'Promoting English language and literature at DUET'}
            ]
            
            for club_data in clubs_data:
                existing_club = Club.query.filter_by(acronym=club_data['acronym']).first()
                if not existing_club:
                    print(f"Creating club: {club_data['name']}")
                    club = Club(**club_data)
                    db.session.add(club)
            
            db.session.commit()
            print("Database initialization completed successfully!")
            return True
            
    except Exception as e:
        print(f"Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
