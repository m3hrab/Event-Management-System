from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, club_manager, student
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    club = db.relationship('Club', backref='managers')
    events_created = db.relationship('Event', backref='creator', lazy='dynamic')
    registrations = db.relationship('EventRegistration', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_club_manager(self):
        return self.role == 'club_manager'
    
    def is_student(self):
        return self.role == 'student'
    
    def can_manage_club(self, club_id):
        return self.is_admin() or (self.is_club_manager() and self.club_id == club_id)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    acronym = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    events = db.relationship('Event', backref='club', lazy='dynamic')
    
    def get_manager(self):
        return User.query.filter_by(club_id=self.id, role='club_manager').first()
    
    def get_upcoming_events(self):
        return self.events.filter(Event.date_time > datetime.utcnow(), Event.is_approved == True).all()
    
    def __repr__(self):
        return f'<Club {self.acronym}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(300), nullable=False)
    poster_url = db.Column(db.String(255))
    registration_deadline = db.Column(db.DateTime, nullable=False)
    max_participants = db.Column(db.Integer, default=100)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    registrations = db.relationship('EventRegistration', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def is_registration_open(self):
        return datetime.utcnow() < self.registration_deadline and self.is_approved
    
    @property
    def is_upcoming(self):
        return datetime.utcnow() < self.date_time
    
    @property
    def registration_count(self):
        return self.registrations.count()
    
    @property
    def seats_available(self):
        return max(0, self.max_participants - self.registration_count)
    
    def is_user_registered(self, user_id):
        return self.registrations.filter_by(user_id=user_id).first() is not None
    
    def __repr__(self):
        return f'<Event {self.title}>'

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate registrations
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event'),)
    
    def __repr__(self):
        return f'<EventRegistration {self.user_id}-{self.event_id}>' 