# Deploy Accelyra Frontend to Vercel

This guide will help you deploy the Accelyra Closing Platform frontend to Vercel to preview the aesthetic and functionality before setting up the backend database.

## Prerequisites

- A GitHub account (your code is already on GitHub)
- A Vercel account (free tier is perfect for this)

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Easiest)

1. **Go to Vercel**
   - Visit [vercel.com](https://vercel.com)
   - Click "Sign Up" or "Login" (use your GitHub account)

2. **Import Your Repository**
   - Click "Add New..." → "Project"
   - Import `snayj/accelyra-closing-platform`
   - Vercel will detect it's a monorepo

3. **Configure the Project**
   - **Framework Preset**: Vite
   - **Root Directory**: `packages/frontend`
   - **Build Command**: `pnpm build`
   - **Output Directory**: `dist`
   - **Install Command**: `pnpm install`
   - **Node Version**: 20.x

4. **Environment Variables** (Optional - not needed for demo)
   - The app works standalone with mock data
   - Later you can add `VITE_API_URL` when backend is ready

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for build
   - You'll get a live URL like `accelyra-closing-platform.vercel.app`

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI globally
npm i -g vercel

# Navigate to frontend directory
cd packages/frontend

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts:
# - Link to existing project? No
# - Project name: accelyra-closing-platform
# - Directory: ./ (you're already in frontend)
# - Override settings? Yes
#   - Build Command: pnpm build
#   - Output Directory: dist
#   - Install Command: pnpm install

# For production deployment
vercel --prod
```

### Option 3: Deploy from Root with vercel.json

If deploying from the root directory:

```bash
# From project root
vercel

# Use these settings:
# - Root Directory: packages/frontend
# - Build Command: cd ../.. && pnpm install && pnpm build:frontend
# - Output Directory: packages/frontend/dist
```

## Post-Deployment

### Your Live URLs

After deployment, you'll get:
- **Preview URL** (for each commit): `accelyra-xxxxx.vercel.app`
- **Production URL**: `accelyra-closing-platform.vercel.app`

### What You Can Test

The deployed frontend includes:

✅ **Welcome Page**
- Hero section with Accelyra branding
- 70% faster closing time stats
- 7-stage process overview
- Quick start guide

✅ **Transaction Simulator** (Core Demo)
- 6 realistic scenarios (perfect, insufficient funds, title issues, etc.)
- Stage-by-stage progression through all 7 stages
- Document validation with OCR simulation
- Real-time activity logging
- Pass/fail validation with detailed reasons

✅ **Transaction History**
- List of past transactions
- Status indicators
- Mock data for demonstration

✅ **About Page**
- Company information
- Technology stack

### Automatic Deployments

Vercel will automatically deploy:
- **Every push to your branch** → Preview deployment
- **Merges to main** → Production deployment

### Custom Domain (Optional)

You can add your own domain:
1. Go to Project Settings → Domains
2. Add your domain (e.g., `demo.accelyra.com`)
3. Update DNS records as instructed

## Testing the Deployment

Once deployed, test all features:

1. **Navigation**: All 4 pages should load instantly
2. **Simulator**:
   - Start a new transaction
   - Try different scenarios
   - Advance through stages
   - Watch activity log update
3. **Responsive Design**: Test on mobile/tablet
4. **Performance**: Should load in < 1 second

## Current Limitations

Since the backend isn't connected yet:
- All data is mock/simulated
- No real API calls
- No database persistence
- OCR and validation are simulated

Once you set up PostgreSQL and deploy the backend, you can:
1. Add `VITE_API_URL` environment variable in Vercel
2. Point it to your backend API (e.g., Railway, Render, or Vercel Serverless)
3. Enable real transaction processing

## Troubleshooting

### Build Fails

If the build fails:
- Check Node version is 20.x
- Ensure pnpm is enabled (Vercel auto-detects from `pnpm-lock.yaml`)
- Verify Root Directory is `packages/frontend`

### 404 on Page Refresh

The `vercel.json` rewrites should handle this. If not:
- Check `vercel.json` exists in `packages/frontend`
- Ensure the rewrite rule is present

### Slow Build Times

First build may take 3-5 minutes. Subsequent builds with cache:
- Preview deployments: ~30 seconds
- Production deployments: ~1 minute

## Next Steps

After viewing the aesthetic on Vercel:

1. **Set up PostgreSQL** (Railway, Supabase, or Neon)
2. **Deploy Backend** (Vercel Serverless Functions or Railway)
3. **Connect Frontend to Backend** (add `VITE_API_URL` env var)
4. **Enable Real Transactions** (Prisma migrations + seed data)

## Cost

- **Vercel Free Tier**: Perfect for this demo
  - 100 GB bandwidth/month
  - Unlimited deployments
  - Automatic HTTPS
  - Global CDN

## Support

If you encounter issues:
- Check [Vercel Documentation](https://vercel.com/docs)
- Vercel build logs show detailed error messages
- The frontend builds successfully locally (confirmed in TEST_RESULTS.md)
