# Event Management System

A production-ready Flask application for managing university club events: create, approve, browse, and register for events with role-based dashboards (Admin, Club Manager, Student).

## Live Demo

- Deployed on Render: `https://duet-ems.onrender.com/`  
  Use the demo credentials below to explore.

## Demo Credentials

- Username or Email: `admin`  
- Password: `admin123`

## Highlights

- Role-based access (Admin, Club Manager, Student)
- Event lifecycle: creation → admin approval → registration
- Clean Bootstrap 5 UI, mobile-friendly
- SQLite by default; can switch to Postgres/MySQL in production

## Tech Stack

- Flask, Flask-Login, Flask-WTF, Flask SQLAlchemy
- Bootstrap 5
- Gunicorn (production)

## Getting Started (Local)

1. Python 3.10+ recommended
2. Create a virtualenv and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python run.py
   # open http://localhost:5000
   ```

4. Sign in using the demo credentials above.

## Configuration

- `.env` (optional):
  - `SECRET_KEY`
  - `DATABASE_URL` (defaults to SQLite)
  - `FLASK_ENV=production` for production

## Screenshots

Add screenshots or a short GIF here to showcase the UI.

## License

MIT
