# Free Hosting on Render - Deployment Guide

## Overview
This guide will help you deploy your Scientific Collaboration Network Analyzer to Render for free.

**What you get with Render's free tier:**
- 1 free web service per account (0.5 CPU, 512MB RAM)
- Services spin down after 15 minutes of inactivity
- Up to 750 free compute hours per month
- Perfect for development and testing

## Prerequisites
1. ✅ Project pushed to GitHub (already done!)
2. A Render account (free) - Sign up at https://render.com
3. Your Supabase PostgreSQL connection string (you already have this in .env)

## Important Notes about Free Tier

### Limitations
- **Services spin down after 15 minutes of inactivity** - First request after spindown takes 30-60 seconds
- **512MB RAM** - Enough for development, tight for production
- **Redis not included** - Free tier doesn't support Redis. We've configured the app to work without it for now
- **No persistent storage** - Uploaded files will be lost on redeployment. Consider using S3 later

### Workarounds Applied
- ✅ Using Supabase PostgreSQL (free tier available)
- ✅ Disabled Redis requirement for free tier
- ✅ Using in-memory caching instead of Redis

## Step 1: Prepare Environment Variables

Before deploying, gather these environment variables:

1. **Database** (Already configured in Supabase)
   - `DATABASE_URL` - Your Supabase PostgreSQL connection string

2. **Authentication**
   - `JWT_SECRET_KEY` - Already in your .env

3. **Email**
   - `SMTP_HOST` - smtp.gmail.com
   - `SMTP_PORT` - 587
   - `SMTP_USERNAME` - Your Gmail
   - `SMTP_PASSWORD` - Your app password (not Gmail password)
   - `SMTP_FROM_EMAIL` - Sender email

4. **API Keys**
   - `ANTHROPIC_API_KEY` - Chatbot AI
   - `GOOGLE_CLIENT_ID` - Google Sign-In
   - `RECAPTCHA_SITE_KEY` - Google reCAPTCHA
   - `RECAPTCHA_SECRET_KEY` - Google reCAPTCHA

## Step 2: Deploy to Render

### Option A: Using Render Dashboard (Easiest for Beginners)

1. Go to https://render.com and sign up/log in

2. Click "New +" → "Web Service"

3. Connect your GitHub repo:
   - Choose "Deploy an existing repository"
   - Connect your GitHub account
   - Select `springboardmentor28126j/Scientific-Collaboration-Network-Analyzer-Group-2`
   - Select branch: `Harikumar`

4. Configure Backend Service:
   - **Name**: `scientific-collab-backend`
   - **Environment**: `Python 3`
   - **Region**: `Oregon` (free tier available)
   - **Branch**: `Harikumar`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`
   - **Plan**: `Free`
   - **Add environment variables**: (See Step 1)
     - DATABASE_URL
     - JWT_SECRET_KEY
     - ANTHROPIC_API_KEY
     - GOOGLE_CLIENT_ID
     - RECAPTCHA_SITE_KEY
     - RECAPTCHA_SECRET_KEY
     - SMTP_HOST=smtp.gmail.com
     - SMTP_PORT=587
     - SMTP_USERNAME
     - SMTP_PASSWORD
     - SMTP_FROM_EMAIL
     - CORS_ORIGINS=["your-frontend-url:5000"]
     - ENVIRONMENT=production

5. Deploy! Click "Create Web Service"

6. Repeat steps 2-5 for Frontend Service:
   - **Name**: `scientific-collab-frontend`
   - **Build Command**: `cd frontend && pip install -r requirements.txt`
   - **Start Command**: `cd frontend && python app.py`
   - **Environment variables**:
     - FLASK_ENV=production
     - BACKEND_API_URL={your-backend-url}/api/v1
     - FLASK_SECRET_KEY={random-secure-string}
     - FLASK_APP=app.py

### Option B: Using Infrastructure as Code (Advanced)

We've created a `render.yaml` file in your repo. You can:

1. Go to https://render.com/dashboard
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect and deploy using `render.yaml`

## Step 3: Configure CORS and URLs

After deployment, you'll get URLs like:
- Backend: `https://scientific-collab-backend.onrender.com`
- Frontend: `https://scientific-collab-frontend.onrender.com`

Update environment variables:
1. Backend `CORS_ORIGINS`: Add frontend URL
   ```
   ["https://scientific-collab-frontend.onrender.com"]
   ```

2. Frontend `BACKEND_API_URL`: Set to backend URL
   ```
   https://scientific-collab-backend.onrender.com/api/v1
   ```

## Step 4: Database Setup

1. Render will run migrations automatically via `alembic upgrade head`
2. If migrations fail:
   - SSH into the backend service via Render dashboard
   - Manually run: `alembic upgrade head`
   - Check your Supabase connection string

## Step 5: Test Deployment

1. Visit your frontend URL: `https://scientific-collab-frontend.onrender.com`
2. Try logging in with your Google account
3. Test email verification (check your email)
4. Check server logs in Render dashboard if issues occur

## Troubleshooting

### Service won't start
- Check logs in Render dashboard: Services → [Your Service] → Logs
- Verify all environment variables are set
- Ensure DATABASE_URL is correct

### Database connection errors
- Verify Supabase connection string includes `postgresql+psycopg2://`
- Check Supabase account status and credits

### Services keep spinning down
- This is normal on free tier! First request takes 30-60 seconds
- Upgrade to paid plan ($7/month) to prevent spindowns

### Redis/Cache errors
- Free tier doesn't support Redis
- App should use in-memory caching (already configured)
- If you see Redis errors, check backend code for Redis-specific features

### File uploads not working
- Uploaded files are stored temporarily in the service
- On redeploy/restart, files are lost
- Solution: Upgrade to S3 storage (AWS, Supabase, etc.)

## Upgrading from Free Tier

When ready for production:

1. **Upgrade to Paid Services** (Render)
   - Starter plan: $7/month per service
   - Prevents spindowns
   - Increases resource limits

2. **Add Redis** (Optional)
   - Render Redis: $15/month
   - Or use Railway.app free credits

3. **Add File Storage** (Optional)
   - Configure AWS S3 or similar
   - Update backend config to use S3 backend

4. **Use Database Backups**
   - Supabase has backup features
   - Enable automated backups for production

## Monitoring

Monitor your deployment:
1. Check logs regularly in Render dashboard
2. Set up error notifications (Render Premium feature)
3. Monitor database usage on Supabase dashboard
4. Watch for spindowns in Render logs

## Security Notes

⚠️ **Important for Production**:
1. Never commit `.env` to GitHub
2. Use Render's built-in environment variable management
3. Rotate API keys regularly
4. Enable 2FA on Supabase and Render accounts
5. Use strong, unique Flask secret key
6. Keep dependencies updated (run `pip install --upgrade` regularly)

## Next Steps

After successful deployment:
1. Test all features thoroughly
2. Monitor logs for errors
3. Set up custom domain (Render supports this)
4. Plan migration to paid tier if needed
5. Configure automated backups

## Support

If you encounter issues:
- Check Render documentation: https://render.com/docs
- Check Supabase documentation: https://supabase.com/docs
- Review service logs in Render dashboard
- Common issues: Missing env vars, connection timeouts, spindowns
