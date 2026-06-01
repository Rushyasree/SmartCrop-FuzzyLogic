# 🚀 CROP ZEN REACT FRONTEND - SETUP GUIDE

## Overview

This guide walks you through setting up the Crop Zen React Dashboard - a modern, feature-rich UI for the agricultural AI platform.

## Prerequisites

- Node.js 16+ (download from https://nodejs.org/)
- npm 8+ or yarn
- Backend API running at http://localhost:5000
- Git (optional, for version control)

## Quick Start (5 minutes)

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Create Environment File
```bash
cp .env.example .env
```

Edit `.env` if your backend is running on a different URL:
```env
VITE_API_URL=http://localhost:5000/api
VITE_APP_NAME=Crop Zen
```

### 4. Start Development Server
```bash
npm run dev
```

The app will open at **http://localhost:3000** with hot reload enabled.

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Auth/            # Login, Register forms
│   │   ├── Dashboard/       # Dashboard pages
│   │   ├── Farms/           # Farm management
│   │   ├── Predictions/     # Crop predictions
│   │   └── Common/          # Shared components
│   ├── pages/               # Page components
│   ├── services/            # API service layer
│   ├── redux/               # State management
│   ├── hooks/               # Custom React hooks
│   ├── App.jsx              # Main app component
│   ├── main.jsx             # React entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── package.json             # Dependencies
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # Tailwind CSS config
└── .env                     # Environment variables
```

## Available Scripts

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Format code
npm run format

# Run tests
npm run test

# Generate coverage report
npm run coverage
```

## Tech Stack

| Tool | Purpose | Version |
|------|---------|---------|
| **React** | UI framework | 18.2+ |
| **Vite** | Build tool | 4.4+ |
| **Redux Toolkit** | State management | 1.9+ |
| **Axios** | HTTP client | 1.5+ |
| **Tailwind CSS** | Styling | 3.3+ |
| **React Router** | Routing | 6.14+ |
| **Chart.js** | Charts & graphs | 4.4+ |

## Authentication Flow

### Login
```
1. User enters email & password
2. Frontend calls POST /api/auth/login
3. Backend returns access_token + refresh_token
4. Tokens stored in localStorage
5. User redirected to dashboard
```

### Protected Routes
```
1. User visits protected page
2. Axios interceptor adds Authorization header
3. Backend verifies token
4. Page renders if valid
5. Auto-logout if expired
```

### Token Refresh
```
1. API returns 401 (token expired)
2. Interceptor calls /api/auth/refresh-token
3. New access_token returned
4. Original request retried with new token
5. User stays logged in
```

## API Integration

All backend APIs are automatically integrated:

### Authentication
```javascript
POST   /auth/register         // Register new user
POST   /auth/login            // Login user
POST   /auth/refresh-token    // Refresh access token
GET    /auth/me               // Get current user (protected)
```

### Farm Management
```javascript
GET    /farms                 // List farms (protected)
POST   /farms                 // Create farm (protected)
GET    /farms/{id}            // Get farm (protected)
PUT    /farms/{id}            // Update farm (protected)
DELETE /farms/{id}            // Delete farm (protected)
```

### Predictions
```javascript
GET    /predictions           // List predictions (protected)
POST   /predictions           // Store prediction (protected)
```

## Styling with Tailwind CSS

We use Tailwind CSS for styling. Check the `tailwind.config.js` for custom colors:

```javascript
primary: '#2D5016'        // Dark green
secondary: '#6B8E23'      // Olive green
accent: '#FFA500'         // Orange
success: '#10B981'        // Green
danger: '#EF4444'         // Red
```

### Usage Examples
```jsx
// Button
<button className="bg-primary hover:bg-secondary text-white px-4 py-2 rounded">
  Click me
</button>

// Card
<div className="bg-white rounded-lg shadow p-6">
  Card content
</div>

// Responsive
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  Items
</div>
```

## Component Examples

### Login Form
```jsx
import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { login } from '../redux/slices/authSlice'

export default function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const dispatch = useDispatch()

  const handleSubmit = (e) => {
    e.preventDefault()
    dispatch(login({ email, password }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        className="w-full px-4 py-2 border rounded"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        className="w-full px-4 py-2 border rounded"
      />
      <button type="submit" className="w-full bg-primary text-white py-2 rounded">
        Login
      </button>
    </form>
  )
}
```

### Farm List
```jsx
import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchFarms } from '../redux/slices/farmsSlice'

export default function FarmList() {
  const dispatch = useDispatch()
  const { farms, loading } = useSelector((state) => state.farms)

  useEffect(() => {
    dispatch(fetchFarms())
  }, [dispatch])

  if (loading) return <div>Loading...</div>

  return (
    <div className="grid gap-4">
      {farms.map((farm) => (
        <div key={farm.id} className="border rounded p-4">
          <h3 className="text-lg font-semibold">{farm.name}</h3>
          <p className="text-gray-600">{farm.location}</p>
          <p className="text-sm">{farm.size_hectares} hectares</p>
        </div>
      ))}
    </div>
  )
}
```

## Common Issues & Solutions

### "Cannot find module" errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port 3000 already in use
```bash
# Change port in vite.config.js or use:
npm run dev -- --port 3001
```

### API calls failing (CORS)
- Ensure backend is running at http://localhost:5000
- Backend CORS is configured to allow http://localhost:3000
- Check Network tab in browser DevTools

### Token not persisting
- Check if localStorage is enabled in browser
- Look for errors in browser console
- Verify token format in Network tab

### Build fails
```bash
# Clear build cache
rm -rf dist
npm run build
```

## Development Tips

### Redux DevTools
Install Redux DevTools browser extension to debug state:
https://chrome.google.com/webstore/detail/redux-devtools/lmjabcaajmjhenlofebjdjnkabbnornj

### React Developer Tools
Install React Developer Tools:
https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi

### Tailwind CSS IntelliSense
For VS Code, install Tailwind CSS IntelliSense extension for autocomplete.

## Deployment

### Build for Production
```bash
npm run build
```

This creates a `dist/` folder with optimized files.

### Deploy to Vercel (Recommended)
```bash
npm install -g vercel
vercel
```

### Deploy to Netlify
Drag and drop the `dist/` folder to Netlify.

### Deploy to AWS S3
```bash
# Build
npm run build

# Sync to S3
aws s3 sync dist/ s3://your-bucket-name --delete
```

## Performance Optimization

- ✅ Code splitting with React.lazy()
- ✅ Image optimization
- ✅ Tree shaking with Vite
- ✅ Minification in production
- ✅ Gzip compression
- ✅ Caching strategy

## Security Best Practices

✅ **Do**
- Store tokens in localStorage (with HTTPS)
- Validate all user inputs
- Sanitize HTML content
- Use HTTPS in production
- Add CSRF tokens if needed

❌ **Don't**
- Store sensitive data in state
- Log tokens to console
- Expose API keys
- Trust user input
- Use outdated dependencies

## Monitoring & Logging

- Browser DevTools for debugging
- Redux DevTools for state inspection
- Network tab for API calls
- Console for errors
- Error boundaries for crash handling

## Contributing

1. Create a branch: `git checkout -b feature/new-feature`
2. Make changes and commit: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/new-feature`
4. Create a pull request

## Support

For issues or questions:
1. Check Network tab in DevTools
2. Review browser console for errors
3. Check backend logs
4. Review documentation
5. Check GitHub issues

## Roadmap

- ✅ Phase 1: Basic setup and components
- ✅ Phase 2: Authentication and CRUD
- ⏳ Phase 3: Analytics and charts
- ⏳ Phase 4: Mobile app (React Native)
- ⏳ Phase 5: Progressive Web App (PWA)

## License

MIT License - feel free to use this project

---

**Status**: 🟢 Frontend Ready for Development  
**Backend Required**: Yes (running at http://localhost:5000)  
**Documentation**: Complete  
**Last Updated**: May 2024
