# 🚀 Quick Render Deployment Guide

## 1. Prepare Repository
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin master
```

## 2. Render Setup
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your `Event-Management-System` repository

## 3. Configuration
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT run:app`

## 4. Environment Variables
| Variable | Value |
|----------|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `^PzTID\TW|\9{D?g}W"*XYlc%dd&#>iC` |
| `DATABASE_URL` | `sqlite:///instance/duet_events.db` |
| `SESSION_COOKIE_SECURE` | `True` |
| `ADMIN_EMAIL` | `admin@duet.ac.bd` |
| `ADMIN_PASSWORD` | `YourSecurePassword123!` |

## 5. After Deployment
- Test: `https://your-app.onrender.com`
- Health: `https://your-app.onrender.com/health`
- Admin login with your credentials

## 6. Important Notes
- ⚠️ **Change ADMIN_PASSWORD** from default
- ⚠️ **Use the SECRET_KEY** generated above
- ⚠️ **Keep credentials secure**
- 💤 Free tier apps sleep after 15 minutes
- ⏰ Wake-up time: 30-60 seconds

## Need Help?
- Check `RENDER_DEPLOYMENT.md` for detailed instructions
- View logs in Render dashboard
- Contact support through Render dashboard
