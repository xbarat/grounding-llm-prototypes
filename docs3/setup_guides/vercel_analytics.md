# Vercel Analytics Setup Guide

## 1. Enable Analytics

### In Vercel Dashboard
```
1. Go to your project in Vercel
2. Navigate to Settings > Analytics
3. Enable Analytics
4. Choose Speed Insights plan (Free)
```

## 2. Frontend Integration

### Install Dependencies
```bash
# In frontend2 directory
npm install @vercel/analytics
```

### Add Analytics Provider
Update `frontend2/app/layout.tsx`:
```typescript
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

## 3. Configure Web Vitals

### Enable Web Vitals Reporting
Update `frontend2/app/layout.tsx`:
```typescript
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
```

## 4. Custom Events

### Track API Performance
```typescript
// In your API routes
import { track } from '@vercel/analytics';

track('api_call', {
  endpoint: '/api/v1/process_query',
  duration: responseTime,
  status: response.status
});
```

### Track User Interactions
```typescript
// In your components
import { track } from '@vercel/analytics';

track('query_submitted', {
  queryType: 'analysis',
  responseTime: duration
});
```

## 5. Dashboard Configuration

### Key Metrics to Monitor
```
1. Core Web Vitals
   - LCP (Largest Contentful Paint)
   - FID (First Input Delay)
   - CLS (Cumulative Layout Shift)

2. API Performance
   - Response times
   - Error rates
   - Usage patterns

3. User Behavior
   - Popular queries
   - Session duration
   - Navigation paths
```

### Set Up Alerts
```
1. Configure email alerts for:
   - Performance degradation
   - Error rate spikes
   - Usage thresholds
```

## 6. Integration with Other Tools

### Sentry Integration
```
1. Link Vercel project with Sentry
2. Enable error tracking
3. Correlate performance data
```

### Status Page Integration
```
1. Connect metrics to status page
2. Set up automated incident creation
3. Configure status updates
```

## 7. Custom Dashboards

### Create Views
```
1. API Performance Dashboard
   - Endpoint response times
   - Error rates by endpoint
   - Usage patterns

2. User Experience Dashboard
   - Core Web Vitals
   - User flows
   - Error impacts

3. Business Metrics Dashboard
   - Query success rates
   - User engagement
   - Feature usage
```

## 8. Monitoring Strategy

### Daily Checks
```
1. Review Core Web Vitals
2. Check API performance
3. Monitor error rates
4. Review user patterns
```

### Weekly Analysis
```
1. Performance trends
2. Usage patterns
3. Error patterns
4. User behavior
```

### Monthly Review
```
1. Performance optimization opportunities
2. Resource utilization
3. Cost analysis
4. User experience improvements
``` 