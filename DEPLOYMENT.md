# SmartBot.uz - Render Deployment Guide

## Prerequisites
- Render.com account
- Environment variables configured

## Environment Variables Required

Set these environment variables in your Render dashboard:

### Required Variables:
- `FLASK_ENV=production`
- `SESSION_SECRET` - Random secret key for sessions
- `ADMIN_PASSWORD` - Admin panel password

### Optional Variables (for full functionality):
- `GEMINI_API_KEY` - Google Gemini AI API key
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `TELEGRAM_CHAT_ID` - Telegram chat ID for notifications
- `TELEGRAM_CHANNEL_ID` - Telegram channel ID
- `GA_MEASUREMENT_ID` - Google Analytics measurement ID
- `GOOGLE_VERIFICATION` - Google Search Console verification

## Deployment Steps

1. **Connect Repository**: Connect your GitHub repository to Render
2. **Service Configuration**: Use the provided `render.yaml` configuration
3. **Environment Variables**: Set all required environment variables in Render dashboard
4. **Deploy**: Deploy the service

## Features Ready for Production

✅ **Performance Optimized**
- Gunicorn with 4 workers
- WhiteNoise for static file serving
- Compressed assets with 1-year cache

✅ **Security Ready**
- Environment variable configuration
- Secure session handling
- Input validation and sanitization

✅ **AI Integration**
- Google Gemini 1.5 Flash API
- Error handling for missing API keys
- Graceful degradation

✅ **SEO Optimized**
- Meta tags and structured data
- Sitemap and robots.txt
- Open Graph and Twitter Card support

✅ **Mobile Responsive**
- Bootstrap 5 framework
- Mobile-optimized navigation
- Touch-friendly interface

## Health Check
The application includes a health check endpoint at `/` for Render monitoring.

## Automatic Setup
The deployment includes automatic setup of:
- Data directories
- Default JSON data files
- Upload directories

## Post-Deployment
After successful deployment:
1. Access admin panel at `/admin`
2. Configure services and portfolio items
3. Test AI functionality (if API keys provided)
4. Verify contact form and Telegram integration