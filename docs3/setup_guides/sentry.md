# Sentry Setup Guide

## 1. Account Setup
```
1. Go to sentry.io
2. Sign up with GitHub
3. Create a new project
   - Platform: Next.js
   - Name: orbit-vi
```

## 2. Frontend Integration

### Install Sentry SDK
```bash
# In frontend2 directory
npm install --save @sentry/nextjs
```

### Initialize Sentry
Create `frontend2/sentry.client.config.ts`:
```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: "YOUR_DSN", // Get from Sentry dashboard
  tracesSampleRate: 1.0,
  replaysOnErrorSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
});
```

Create `frontend2/sentry.server.config.ts`:
```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: "YOUR_DSN",
  tracesSampleRate: 1.0,
});
```

### Update Next.js Config
Update `frontend2/next.config.mjs`:
```javascript
const nextConfig = {
  // ... other config
  sentry: {
    hideSourceMaps: true,
  },
};

export default withSentry(nextConfig);
```

## 3. Backend Integration

### Install Sentry SDK
```bash
# In backend directory
pip install --upgrade 'sentry-sdk[fastapi]'
```

### Initialize Sentry
Update `backend/app/main.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="YOUR_DSN",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    integrations=[FastApiIntegration()]
)
```

## 4. Configure Alerts

### Error Alerts
```
1. Go to Sentry > Settings > Alerts
2. Create new alert rule:
   - Condition: Error frequency
   - Threshold: > 0 errors in 5 minutes
   - Action: Email notification
```

### Performance Alerts
```
1. Create performance alert:
   - Condition: P95 transaction duration
   - Threshold: > 1000ms
   - Action: Email notification
```

## 5. Environment Variables

### Frontend (.env)
```
NEXT_PUBLIC_SENTRY_DSN=your_dsn
SENTRY_AUTH_TOKEN=your_auth_token
```

### Backend (.env)
```
SENTRY_DSN=your_dsn
SENTRY_ENVIRONMENT=production
```

## 6. Verify Installation

### Test Frontend Error Tracking
```typescript
// Add to any component to test
throw new Error("Test Sentry Error");
```

### Test Backend Error Tracking
```python
# Add to any endpoint to test
raise Exception("Test Sentry Error")
```

## 7. Additional Setup

### Source Maps
```
1. Enable source map uploads in Sentry
2. Add SENTRY_AUTH_TOKEN to Vercel
3. Configure build settings
```

### Performance Monitoring
```
1. Enable performance monitoring
2. Set up custom transactions
3. Configure sampling rates
```

### User Context
```
1. Set up user identification
2. Configure custom tags
3. Add release tracking
```

## 8. Monitoring Dashboard

### Key Metrics to Watch
```
1. Error frequency
2. Affected users
3. Performance metrics
4. Release health
```

### Alert Configuration
```
1. Set up Slack integration
2. Configure email notifications
3. Set up PagerDuty (optional)
``` 