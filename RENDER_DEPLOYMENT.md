# Render Deployment Guide for DUET Event Management System

## Prerequisites

1. **GitHub Account**: Your code should be pushed to a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com) (free tier available)
3. **Code Ready**: Ensure all files are committed and pushed to GitHub

## Step-by-Step Deployment Instructions

### Step 1: Prepare Your Repository

1. **Commit all changes to GitHub:**
```bash
cd "/home/mehrab/Event Management System"
git add .
git commit -m "Prepare for Render deployment"
git push origin master
```

### Step 2: Create a Render Account

1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with your GitHub account (recommended)
4. Authorize Render to access your repositories

### Step 3: Create a New Web Service

1. **Dashboard**: Once logged in, click "New +" → "Web Service"
2. **Connect Repository**: 
   - Select "Connect account" if not already connected
   - Find your `Event-Management-System` repository
   - Click "Connect"

### Step 4: Configure the Web Service

Fill in the following configuration:

#### Basic Settings
- **Name**: `duet-events` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `master`
- **Root Directory**: Leave empty (use root)

#### Build & Deploy Settings
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT run:app`

#### Environment Variables
Click "Advanced" → "Add Environment Variable" and add these:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `your-super-secret-key-here-generate-a-strong-one` |
| `DATABASE_URL` | `sqlite:///instance/duet_events.db` |
| `SESSION_COOKIE_SECURE` | `True` |
| `ADMIN_EMAIL` | `admin@duet.ac.bd` |
| `ADMIN_PASSWORD` | `NewSecurePassword123!` |

**Important**: 
- Generate a strong SECRET_KEY (32+ random characters)
- Change the ADMIN_PASSWORD from default
- Keep these values secure!

### Step 5: Deploy

1. **Review Settings**: Double-check all configurations
2. **Create Web Service**: Click "Create Web Service"
3. **Wait for Deployment**: This takes 5-15 minutes
4. **Monitor Logs**: Watch the build logs for any errors

### Step 6: Verify Deployment

Once deployment is complete:

1. **Access Application**: Click the URL provided by Render (e.g., `https://duet-events.onrender.com`)
2. **Test Health Check**: Visit `https://your-app.onrender.com/health`
3. **Login as Admin**: Use the credentials you set in environment variables
4. **Test Features**: Create a club, add an event, register as a student

## Render Configuration Details

### Free Tier Limitations
- **Sleep Mode**: Apps sleep after 15 minutes of inactivity
- **Monthly Hours**: 750 hours/month (sufficient for most use cases)
- **Wake-up Time**: 30-60 seconds from sleep
- **Storage**: 1GB persistent disk

### Paid Tier Benefits ($7/month)
- **Always On**: No sleep mode
- **Better Performance**: Faster startup and response
- **More Storage**: Additional disk space
- **Custom Domains**: Use your own domain

## Environment Variables Explained

```bash
# Application Settings
FLASK_ENV=production                    # Sets Flask to production mode
SECRET_KEY=your-secret-key-here        # Session encryption key
DATABASE_URL=sqlite:///instance/duet_events.db  # Database location

# Security Settings
SESSION_COOKIE_SECURE=True             # HTTPS-only cookies
SESSION_COOKIE_HTTPONLY=True           # Prevent XSS

# Admin Account
ADMIN_EMAIL=admin@duet.ac.bd          # Admin login email
ADMIN_PASSWORD=your-secure-password    # Admin login password

# Optional: Email Configuration (if you want email features)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Database Considerations

### SQLite (Default - Recommended for Start)
- **Pros**: Simple, no setup required, good for small-medium apps
- **Cons**: Not suitable for high-traffic apps
- **Storage**: Data persists across deployments

### PostgreSQL (For Scaling)
If you expect high traffic, consider upgrading to PostgreSQL:

1. **Add PostgreSQL**: In Render dashboard, create a PostgreSQL database
2. **Update DATABASE_URL**: Use the connection string provided by Render
3. **Update requirements.txt**: Ensure `psycopg2-binary` is included

## Custom Domain Setup (Optional)

1. **Purchase Domain**: From any domain registrar
2. **Add Custom Domain**: In Render dashboard → Settings → Custom Domains
3. **Configure DNS**: Point your domain to Render's servers
4. **SSL Certificate**: Render provides free SSL automatically

## Monitoring and Maintenance

### Check Application Health
- **URL**: `https://your-app.onrender.com/health`
- **Expected Response**: `{"status": "healthy", "timestamp": "...", "database": "connected"}`

### View Logs
1. **Render Dashboard**: Go to your service
2. **Logs Tab**: View real-time application logs
3. **Monitor Errors**: Watch for any application errors

### Update Application
```bash
# Make changes locally
git add .
git commit -m "Your update message"
git push origin master

# Render will automatically redeploy
```

## Troubleshooting Common Issues

### 1. Build Fails
- **Check logs** in Render dashboard
- **Verify requirements.txt** includes all dependencies
- **Check Python version** compatibility

### 2. Application Won't Start
- **Check Start Command**: Should be `gunicorn --bind 0.0.0.0:$PORT run:app`
- **Verify run.py** exists in root directory
- **Check environment variables** are set correctly

### 3. Database Errors
- **Check DATABASE_URL** format
- **Verify database** initialization in build process
- **Check file permissions** for SQLite

### 4. 404 Errors
- **Check routes** in your Flask application
- **Verify static files** are properly configured
- **Check base URL** in templates

## Security Best Practices

1. **Strong SECRET_KEY**: Use a random 32+ character string
2. **Secure Admin Password**: Use a strong, unique password
3. **Environment Variables**: Never commit secrets to GitHub
4. **HTTPS Only**: Render provides HTTPS by default
5. **Regular Updates**: Keep dependencies updated

## Performance Optimization

1. **Gunicorn Workers**: For paid plans, you can increase workers:
   ```
   Start Command: gunicorn --bind 0.0.0.0:$PORT --workers 2 run:app
   ```

2. **Static Files**: Consider using a CDN for static assets

3. **Database**: Upgrade to PostgreSQL for better performance

## Getting Help

1. **Render Documentation**: [docs.render.com](https://docs.render.com)
2. **Render Support**: Available through dashboard
3. **Application Logs**: Check Render dashboard logs
4. **GitHub Issues**: For application-specific problems

---

## Quick Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service configured
- [ ] Environment variables set
- [ ] SECRET_KEY generated and set
- [ ] Admin password changed
- [ ] Application deployed successfully
- [ ] Health check responds correctly
- [ ] Admin login works
- [ ] Basic functionality tested

**Your DUET Event Management System should now be live on Render!** 🚀

Access it at: `https://your-service-name.onrender.com`
