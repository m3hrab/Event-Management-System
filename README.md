# DUET Event Management System

A comprehensive web application for managing events at Dhaka University of Engineering & Technology (DUET). This system allows clubs to create events, students to register for events, and administrators to manage the entire ecosystem.

## Features

### 🔐 User Authentication & Authorization
- User registration and login with password hashing
- Role-based access control (Admin, Club Manager, Student)
- Session management with Flask-Login
- Secure password validation

### 👥 User Roles

#### Admin
- Manage all users and assign roles
- Approve/reject events from clubs
- Create and manage clubs
- Assign club managers
- System-wide statistics and overview

#### Club Manager
- Create and manage events for their assigned club
- View event registrations and participants
- Edit event details (requires re-approval if modified)
- Club-specific dashboard with analytics

#### Student
- Browse and search for events
- Register/unregister for events
- Personal dashboard with registered events
- View upcoming and past events

### 🎯 Event Management
- Create events with detailed information (title, description, date, location, capacity)
- Event approval workflow (admin approval required)
- Registration deadlines and capacity limits
- Event search and filtering by club, date, status
- Registration management with duplicate prevention

### 🏛️ Club Management
- Multiple clubs support (DUETCS, DRC, DELC, and more)
- Club profiles with descriptions
- Manager assignment system
- Club-specific event listing

### 🎨 Modern UI/UX
- Responsive design with Bootstrap 5
- Beautiful landing page with hero section
- Role-based navigation and dashboards
- Clean, professional interface
- Mobile-friendly design

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Icons**: Bootstrap Icons

## Project Structure

```
project/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes
│   │   ├── main.py              # Main/landing routes
│   │   ├── events.py            # Event management routes
│   │   ├── clubs.py             # Club management routes
│   │   └── dashboard.py         # Dashboard routes
│   ├── templates/
│   │   ├── base.html            # Base template
│   │   ├── landing.html         # Landing page
│   │   ├── about.html           # About page
│   │   ├── events.html          # Events listing
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── signup.html
│   │   ├── dashboard/
│   │   │   ├── admin.html
│   │   │   ├── club_manager.html
│   │   │   ├── student.html
│   │   │   ├── manage_users.html
│   │   │   └── manage_events.html
│   │   └── events/
│   │       ├── detail.html
│   │       ├── create.html
│   │       └── edit.html
│   └── static/
├── config.py                    # Configuration settings
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Event\ Management\ System
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Demo Credentials

### Admin Account
- **Email**: `admin@duet.ac.bd`
- **Password**: `admin123`
- **Role**: Administrator with full system access

### Creating Additional Users
1. Register as a new user (defaults to Student role)
2. Login as admin to promote users to Club Manager or Admin roles
3. Assign club managers to specific clubs

## Default Clubs

The system comes pre-configured with these DUET clubs:
- **DUETCS** - DUET Computer Society
- **DRC** - DUET Robotics Club  
- **DELC** - DUET English Language Club

Admins can create additional clubs as needed.

## Key Features in Detail

### Event Workflow
1. **Creation**: Club managers create events
2. **Approval**: Events require admin approval before going live
3. **Registration**: Students can register for approved events
4. **Management**: Track registrations, view participants

### Search & Discovery
- Search events by title
- Filter by club, date range, status
- Separate views for upcoming vs past events
- Registration status indicators

### Security Features
- Password hashing with Werkzeug
- Session management
- Role-based route protection
- CSRF protection with Flask-WTF
- Input validation and sanitization

### Responsive Design
- Mobile-first design approach
- Bootstrap 5 components
- Professional color scheme
- Intuitive navigation
- Hover effects and animations

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/signup` - User registration
- `GET /auth/logout` - User logout

### Events
- `GET /events/<id>` - Event details
- `POST /events/create` - Create event (Club Manager)
- `POST /events/<id>/register` - Register for event
- `POST /events/<id>/approve` - Approve event (Admin)

### Dashboard
- `GET /dashboard/` - Role-based dashboard redirect
- `GET /dashboard/admin` - Admin dashboard
- `GET /dashboard/club-manager` - Club manager dashboard
- `GET /dashboard/student` - Student dashboard

## Configuration

### Environment Variables
- `SECRET_KEY` - Flask secret key for sessions
- `DATABASE_URL` - Database connection string
- `MAIL_SERVER` - Email server (for future notifications)

### Default Configuration
The app uses SQLite by default for easy setup. For production:
1. Set `DATABASE_URL` to PostgreSQL connection string
2. Set a strong `SECRET_KEY`
3. Configure email settings for notifications

## Development

### Adding New Features
1. Create models in `models.py`
2. Add routes in appropriate blueprint
3. Create templates in `templates/`
4. Update navigation in `base.html`

### Database Migrations
The app automatically creates tables on first run. For schema changes:
1. Modify models in `models.py`
2. Delete the database file to recreate
3. Restart the application

## Future Enhancements

- [ ] Email notifications for event approvals/registrations
- [ ] Event categories and tags
- [ ] Calendar integration
- [ ] Event photos/file uploads
- [ ] Event feedback and ratings
- [ ] Attendance tracking with QR codes
- [ ] Club analytics and reporting
- [ ] Social features (event sharing, comments)
- [ ] Mobile app support
- [ ] Advanced search with location-based filtering

## Deployment

### Local Development
The application is configured for immediate local development with SQLite.

### Production Deployment

This application is production-ready with comprehensive deployment configurations.

#### Quick Production Setup

```bash
# Clone the repository
git clone <repository-url>
cd Event-Management-System

# Run the automated deployment script
sudo ./deploy.sh
```

#### Production Features

- **Environment-based configuration** with development, testing, and production configs
- **Docker support** with multi-stage builds and optimized containers
- **Nginx configuration** with SSL, security headers, and performance optimization
- **Systemd service** for reliable application management
- **Comprehensive monitoring** with health checks and automated alerts
- **Security hardening** with fail2ban, firewall configuration, and security headers
- **Automated backups** with rotation and retention policies
- **Production logging** with log rotation and centralized monitoring

#### Deployment Options

1. **Traditional Server Deployment**: Full server setup with nginx, gunicorn, and systemd
2. **Docker Deployment**: Containerized deployment with Docker Compose
3. **Cloud Deployment**: Ready for AWS, GCP, Azure, and other cloud platforms

#### Production Documentation

- [Complete Deployment Guide](DEPLOYMENT.md) - Step-by-step production deployment
- [Production Checklist](PRODUCTION_CHECKLIST.md) - Pre and post-deployment verification
- [Security Setup](security-setup.sh) - Automated security hardening
- [Monitoring Scripts](monitor.sh) - Health monitoring and alerting

#### Environment Configuration

The application supports multiple environments through configuration classes:

- **Development**: Debug enabled, SQLite database, relaxed security
- **Production**: Debug disabled, PostgreSQL/MySQL support, enhanced security
- **Testing**: In-memory database, optimized for testing

#### Security Features (Production)

- SSL/TLS encryption with automatic certificate management
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- Rate limiting and DDoS protection
- Fail2ban integration for intrusion prevention
- Automated security updates
- Comprehensive logging and monitoring
- Database connection pooling and optimization

#### Performance Optimizations

- **Gunicorn WSGI server** with configurable worker processes
- **Nginx reverse proxy** with caching and compression
- **Static file optimization** with proper caching headers
- **Database connection pooling** for improved performance
- **Log rotation** to prevent disk space issues

#### Monitoring and Maintenance

- **Health check endpoint** (`/health`) for load balancer integration
- **Automated monitoring scripts** for system health
- **Log aggregation** and error tracking
- **Backup automation** with configurable retention
- **Performance metrics** and alerting

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation for common solutions

---

**Built with ❤️ for DUET Community**