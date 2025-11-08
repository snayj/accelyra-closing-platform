# Deploy Backend to Railway

This guide will help you deploy the Accelyra backend to Railway with full PDF generation and OCR capabilities.

## Prerequisites

- GitHub account (to connect Railway)
- Supabase database (already set up)

## Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click **"Login"** → Sign in with GitHub
3. Authorize Railway to access your GitHub account

## Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose: `your-username/accelyra-closing-platform`
4. Railway will detect the `railway.json` config automatically

## Step 3: Set Environment Variables

Railway will start building immediately, but you need to add environment variables:

1. Click on your project
2. Click **"Variables"** tab in the left sidebar
3. Click **"Add Variable"** and add these THREE variables:

### Variable 1: DATABASE_URL
```
DATABASE_URL
```
**Value:**
```
postgresql://postgres:%3FHZbqbNv4zm%2Ai%40T@db.zukwdzenqrxoazbtozjm.supabase.co:5432/postgres
```
*(This is your Supabase connection string with URL-encoded password)*

### Variable 2: NODE_ENV
```
NODE_ENV
```
**Value:**
```
production
```

### Variable 3: PORT
```
PORT
```
**Value:**
```
3001
```

## Step 4: Redeploy

After adding variables:
1. Go to **"Deployments"** tab
2. Click the **three dots (...)** on the latest deployment
3. Click **"Redeploy"**

Railway will rebuild with the correct configuration.

## Step 5: Get Your Backend URL

Once deployed successfully:
1. Go to **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. You'll get a URL like: `https://accelyra-backend-production.up.railway.app`

**Copy this URL** - you'll need it for the frontend!

## Step 6: Update Frontend to Use Railway Backend

You'll need to update the frontend to point to your Railway backend URL instead of localhost.

In the Vercel dashboard for your frontend:
1. Go to **Settings** → **Environment Variables**
2. Add:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://your-backend.up.railway.app/api/v1`
3. **Redeploy** the frontend

## What Gets Deployed

Your Railway backend includes:
- ✅ PDF Generation (Puppeteer with beautiful templates)
- ✅ OCR Processing (pdf-parse)
- ✅ Validation Engine
- ✅ All API Endpoints
- ✅ Database Connection (Supabase)
- ✅ Automatic Prisma Migrations

## Monitoring & Logs

To view logs:
1. Click on your project in Railway
2. Click **"Deployments"** tab
3. Click on the running deployment
4. View real-time logs

## Testing Your Backend

Once deployed, test the health endpoint:
```
https://your-backend.up.railway.app/health
```

You should see:
```json
{
  "status": "ok",
  "timestamp": "2025-01-06T12:00:00.000Z"
}
```

## Troubleshooting

### Build Fails
- Check that all environment variables are set
- View logs for specific error messages
- Ensure Supabase database is accessible

### Migrations Fail
- Check DATABASE_URL is correct
- Ensure password is URL-encoded
- Verify Supabase database is running

### Timeout Issues
- Railway free tier has no timeout limits (unlike Vercel)
- PDF generation should complete in 3-5 seconds

## Cost

Railway free tier includes:
- 500 hours of usage per month
- $5 free credit
- Perfect for demos and MVPs

## Next Steps

After deployment:
1. Update frontend VITE_API_URL in Vercel
2. Test document generation at `/simulator`
3. Verify OCR and validation workflows

## Support

If you encounter issues:
- Check Railway logs for errors
- Verify environment variables are set correctly
- Ensure Supabase connection string is properly URL-encoded
