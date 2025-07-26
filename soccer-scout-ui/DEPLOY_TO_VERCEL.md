# Deploy Soccer Scout UI to Vercel

## Option 1: Vercel Web Dashboard (Recommended)

1. **Push to GitHub** (if not already done):
   ```bash
   git push origin main
   ```

2. **Go to Vercel Dashboard**:
   - Visit: https://vercel.com/dashboard
   - Click "Add New..." → "Project"

3. **Import from GitHub**:
   - Select your GitHub repository: `socceranalysis`
   - Choose the `soccer-scout-ui` folder as the root directory

4. **Configure Build Settings**:
   - Framework Preset: Next.js
   - Root Directory: `soccer-scout-ui`
   - Build Command: `npm run build`
   - Output Directory: `.next`

5. **Environment Variables**:
   - Add: `NEXT_PUBLIC_API_URL` = `https://soccer-scout-ai-production.up.railway.app`
   - Add: `NODE_ENV` = `production`

6. **Deploy**:
   - Click "Deploy" and wait for build completion

## Option 2: Vercel CLI (After Authentication)

1. **Login to Vercel**:
   ```bash
   cd soccer-scout-ui
   npx vercel login
   ```

2. **Deploy to Production**:
   ```bash
   npx vercel --prod
   ```

## Built-in Configuration

The project includes:
- ✅ `vercel.json` with production settings
- ✅ Next.js optimization for Vercel
- ✅ Environment variables configured
- ✅ API routes for health checks
- ✅ Professional UI with chat interface

## Expected Result

After deployment, you'll get a URL like:
`https://soccer-scout-ui-[random].vercel.app`

The application will:
- ✅ Show modern chat interface
- ✅ Connect to Railway backend
- ✅ Handle player queries with GPT-4
- ✅ Display professional scout reports