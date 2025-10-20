# Vercel Deployment Guide

## 🚀 Deploy Visual Agent to Vercel

This guide shows how to deploy the Visual Agent web interface to Vercel so users can access it via a public URL.

## 📁 Files for Vercel Deployment

### Required Files:

- `api/index.py` - Vercel-compatible Flask API
- `vercel.json` - Vercel configuration
- `visual_agent.py` - Core Visual Agent class
- `requirements.txt` - Python dependencies
- `index.html` - Web interface

### Optional Files:

- `examples/` - Sample text files
- `README.md` - Documentation

## 🛠️ Deployment Steps

### 1. Prepare Your Repository

Make sure these files are in your repository root:

```
visual-agent/
├── api/
│   └── index.py
├── vercel.json
├── visual_agent.py
├── requirements.txt
├── index.html
└── examples/
```

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from your project directory
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? (your account)
# - Link to existing project? No
# - What's your project's name? visual-agent
# - In which directory is your code located? ./
```

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Sign in with your Git provider (GitHub, GitLab, etc.)
3. Click "New Project"
4. Import your repository
5. Vercel will auto-detect the Python configuration
6. Click "Deploy"

### 3. Configure Environment (if needed)

If you need environment variables:

1. Go to your project dashboard on Vercel
2. Go to Settings → Environment Variables
3. Add any required variables

### 4. Access Your Deployed App

After deployment, you'll get a URL like:

- `https://visual-agent-xyz.vercel.app`

## 🔧 Configuration Details

### vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

### API Endpoints

- `GET /` - Serves the web interface
- `POST /generate` - Generates visuals from text
- `GET /health` - Health check

## 🧪 Testing Your Deployment

### 1. Test the Web Interface

Visit your Vercel URL and test the web interface:

- Enter some text
- Select a visual type
- Click "Generate Visual"

### 2. Test the API Directly

```bash
curl -X POST https://your-app.vercel.app/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Start -> Process -> End", "type": "flowchart"}'
```

## 🚨 Important Notes

### Limitations

- **Cold starts**: First request may be slower due to serverless cold start
- **Timeout**: Functions have a 30-second timeout (configurable)
- **File system**: Only `/tmp` directory is writable
- **Memory**: Limited to 1024MB per function

### Best Practices

- Keep your code lightweight
- Use caching for frequently accessed data
- Handle cold starts gracefully
- Test thoroughly before going live

## 🔄 Updates and Redeployment

### Automatic Updates

If you connected to Git:

- Push changes to your main branch
- Vercel automatically redeploys

### Manual Updates

```bash
# Redeploy from CLI
vercel --prod

# Or trigger from Vercel dashboard
```

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**: Make sure all files are in the correct locations
2. **Timeout errors**: Increase `maxDuration` in vercel.json
3. **Memory errors**: Optimize your code or use external storage
4. **CORS errors**: Check your API headers

### Debugging

1. Check Vercel function logs in the dashboard
2. Use `console.log()` for debugging
3. Test locally with `vercel dev`

## 📊 Monitoring

### Vercel Analytics

- View request metrics in your dashboard
- Monitor performance and errors
- Set up alerts for failures

### Custom Monitoring

- Add health check endpoints
- Log important events
- Monitor response times

## 🎉 Success!

Once deployed, your Visual Agent will be accessible at:
`https://your-app-name.vercel.app`

Users can:

- Access the web interface
- Generate flowcharts, diagrams, and charts
- Use the API for integration
- View examples and documentation

---

**Ready to deploy?** Follow the steps above and your Visual Agent will be live on Vercel! 🚀
