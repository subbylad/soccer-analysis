# Soccer Scout AI - Deployment FAQ

## 🔑 OpenAI API Key Questions

### Q: When deployed, would I need to add my OpenAI key again?

**A: Yes, you'll need to set your OpenAI API key in the production environment.** Here's why and how:

#### Why you need to set it again:
- **Security**: Environment variables are not transferred from local to production
- **Separation**: Local `.env` files are not deployed (they're in `.gitignore`)
- **Platform-specific**: Each deployment platform has its own environment management

#### How to set it for each platform:

**🚄 Railway (Backend)**
```bash
# Method 1: Using Railway CLI
railway variables set OPENAI_API_KEY="sk-your-key-here"

# Method 2: Railway Dashboard
# 1. Go to your project dashboard
# 2. Click "Variables" tab
# 3. Add OPENAI_API_KEY with your key value
```

**▲ Vercel (Frontend - if needed)**
```bash
# Method 1: Using Vercel CLI
vercel env add NEXT_PUBLIC_API_URL

# Method 2: Vercel Dashboard
# 1. Go to Project Settings
# 2. Click "Environment Variables"
# 3. Add your variables
```

**🎨 Render**
```bash
# Render Dashboard only:
# 1. Go to your service dashboard
# 2. Click "Environment" tab
# 3. Add OPENAI_API_KEY with your key value
```

**🐳 Docker**
```bash
# Method 1: Environment file
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Method 2: Docker run command
docker run -e OPENAI_API_KEY="sk-your-key-here" soccer-scout-api

# Method 3: Docker Compose
# Already configured in docker-compose.yml to read from .env
```

### Q: Do I need to set the API key on both frontend and backend?

**A: Only the backend needs the OpenAI API key.**

- **Backend** (Flask API): Needs `OPENAI_API_KEY` to communicate with OpenAI
- **Frontend** (Next.js): Only needs `NEXT_PUBLIC_API_URL` to connect to your backend

### Q: Is my OpenAI key secure when deployed?

**A: Yes, when properly configured:**

✅ **Secure practices:**
- Stored as environment variables (encrypted at rest)
- Never exposed in client-side code
- Not visible in logs or error messages
- Platform-managed secret storage

❌ **Avoid these:**
- Never commit API keys to Git
- Don't put keys in frontend environment variables
- Don't hardcode keys in source code

## 🚀 Deployment Process Questions

### Q: What's the deployment order?

**A: Deploy backend first, then frontend:**

1. **Deploy Backend** (Railway/Render/Docker)
   - Set `OPENAI_API_KEY` environment variable
   - Note the deployed backend URL
   
2. **Deploy Frontend** (Vercel/Render)
   - Set `NEXT_PUBLIC_API_URL` to your backend URL
   - Update CORS settings on backend if needed

### Q: How long does deployment take?

**A: Typical deployment times:**

- **Railway**: 2-5 minutes
- **Vercel**: 1-3 minutes  
- **Render**: 5-10 minutes
- **Docker**: 1-2 minutes (local)

### Q: What if deployment fails?

**A: Common issues and solutions:**

1. **Missing API Key**
   ```bash
   # Error: OpenAI API key not found
   # Solution: Set OPENAI_API_KEY environment variable
   railway variables set OPENAI_API_KEY="sk-..."
   ```

2. **Build Failures**
   ```bash
   # Error: Build failed
   # Solution: Check Node.js/Python versions match requirements
   ```

3. **CORS Errors**
   ```bash
   # Error: CORS policy error
   # Solution: Update CORS_ORIGINS on backend
   railway variables set CORS_ORIGINS="https://your-frontend.vercel.app"
   ```

## 🔧 Environment Configuration

### Q: What environment variables do I need to set?

**Backend (Required):**
```bash
OPENAI_API_KEY=sk-your-key-here          # Required for GPT-4
FLASK_ENV=production                      # Production mode
NODE_ENV=production                       # Production mode
CORS_ORIGINS=https://your-frontend.com   # Frontend URL
```

**Frontend (Required):**
```bash
NEXT_PUBLIC_API_URL=https://your-backend.com  # Backend URL
NODE_ENV=production                            # Production mode
```

### Q: How do I update environment variables after deployment?

**Railway:**
```bash
railway variables set VARIABLE_NAME="new-value"
railway restart  # Restart to apply changes
```

**Vercel:**
```bash
vercel env add VARIABLE_NAME
vercel --prod  # Redeploy with new variables
```

**Render:**
- Use dashboard to update variables
- Service will automatically restart

## 🌐 Domain and SSL Questions

### Q: Will my deployed app have HTTPS?

**A: Yes, all platforms provide free SSL certificates:**

- **Vercel**: Automatic HTTPS with custom domains
- **Railway**: Free SSL on *.railway.app domains  
- **Render**: Free SSL on *.onrender.com domains

### Q: Can I use my own domain?

**A: Yes, all platforms support custom domains:**

**Vercel:**
```bash
vercel domains add yourdomain.com
# Then configure DNS to point to Vercel
```

**Railway:**
```bash
railway domain add yourdomain.com
# Then configure DNS with provided values
```

**Render:**
- Add custom domain in dashboard
- Configure DNS as instructed

## 💰 Cost Questions

### Q: What are the costs for deployment?

**A: Platform costs:**

**Free Tiers:**
- **Vercel**: 100GB bandwidth, hobby projects
- **Railway**: $5 credit monthly, then pay-per-use
- **Render**: 750 hours/month free (sleeps after 15min)

**Paid Plans:**
- **Vercel Pro**: $20/month per member
- **Railway**: Pay-per-use ($0.000463/GB-hour RAM)
- **Render**: $7/month for always-on service

**OpenAI Costs:**
- GPT-4: ~$0.03 per 1K tokens
- Typical query: $0.01-0.05 per complex tactical analysis

### Q: How can I control OpenAI costs?

**A: Cost control strategies:**

1. **Set Usage Limits** in OpenAI dashboard
2. **Monitor Usage** regularly
3. **Implement Caching** (already built-in)
4. **Rate Limiting** prevents abuse
5. **Query Optimization** for efficient prompts

## 🐛 Troubleshooting

### Q: My app is deployed but GPT-4 features don't work. What's wrong?

**A: Check these in order:**

1. **Verify API key is set:**
   ```bash
   railway variables  # Should show OPENAI_API_KEY
   ```

2. **Check API key format:**
   ```bash
   # Should start with sk- and be 51 characters
   echo $OPENAI_API_KEY | wc -c
   ```

3. **Test backend health:**
   ```bash
   curl https://your-backend.com/api/health
   ```

4. **Check logs:**
   ```bash
   railway logs  # or platform-specific log command
   ```

### Q: The frontend loads but can't connect to the backend?

**A: CORS configuration issue:**

1. **Check frontend API URL:**
   ```bash
   # Should match your deployed backend
   echo $NEXT_PUBLIC_API_URL
   ```

2. **Update backend CORS:**
   ```bash
   railway variables set CORS_ORIGINS="https://your-frontend.vercel.app"
   ```

3. **Restart backend:**
   ```bash
   railway restart
   ```

## 📊 Monitoring

### Q: How do I monitor my deployed application?

**A: Built-in monitoring:**

1. **Health Checks:**
   ```bash
   curl https://your-backend.com/api/health
   curl https://your-frontend.com/health
   ```

2. **Platform Dashboards:**
   - **Railway**: Metrics, logs, and usage
   - **Vercel**: Analytics and performance
   - **Render**: Logs and metrics

3. **Logs:**
   ```bash
   railway logs       # Railway
   vercel logs        # Vercel  
   # Render: View in dashboard
   ```

## 🔄 Updates and Maintenance

### Q: How do I update my deployed application?

**A: Simple redeployment:**

1. **Update your code locally**
2. **Push to Git repository**
3. **Platforms auto-deploy** from Git pushes
4. **Or manually redeploy:**
   ```bash
   railway up         # Railway
   vercel --prod      # Vercel
   ```

### Q: How often should I update dependencies?

**A: Recommended schedule:**

- **Security updates**: Immediately
- **Minor updates**: Monthly
- **Major updates**: Quarterly with testing
- **OpenAI models**: When new versions available

---

## 📞 Getting Help

### Q: Where can I get support?

**A: Support channels:**

1. **Platform Support:**
   - Railway: Discord community
   - Vercel: GitHub discussions
   - Render: Support tickets

2. **OpenAI Support:**
   - OpenAI community forum
   - OpenAI help center

3. **Project Support:**
   - GitHub issues for bugs
   - Documentation in this repository

### Q: What information should I include when asking for help?

**A: Always include:**

1. **Platform used** (Railway, Vercel, etc.)
2. **Error messages** (full text)
3. **Steps to reproduce** the issue
4. **Environment details** (Node.js version, etc.)
5. **Logs** from the platform dashboard

---

**💡 Pro Tip**: Keep your OpenAI API key secure and monitor usage regularly to avoid unexpected costs!