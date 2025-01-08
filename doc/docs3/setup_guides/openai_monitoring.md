# OpenAI Usage Monitoring Guide

## 1. OpenAI Dashboard Setup

### Access Usage Dashboard
```
1. Go to platform.openai.com
2. Navigate to Usage section
3. View current usage and limits
```

### Set Up Hard Limits
```
1. Go to Settings > Billing
2. Set monthly spending cap
3. Configure usage alerts
4. Set up billing notifications
```

## 2. Backend Integration

### Add Usage Tracking
Update `backend/app/main.py`:
```python
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OpenAIUsageTracker:
    def __init__(self):
        self.daily_usage = {}
        self.monthly_usage = {}
        
    def track_request(self, model: str, tokens: int, cost: float):
        date = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        # Track daily usage
        if date not in self.daily_usage:
            self.daily_usage[date] = {'requests': 0, 'tokens': 0, 'cost': 0.0}
        self.daily_usage[date]['requests'] += 1
        self.daily_usage[date]['tokens'] += tokens
        self.daily_usage[date]['cost'] += cost
        
        # Track monthly usage
        if month not in self.monthly_usage:
            self.monthly_usage[month] = {'requests': 0, 'tokens': 0, 'cost': 0.0}
        self.monthly_usage[month]['requests'] += 1
        self.monthly_usage[month]['tokens'] += tokens
        self.monthly_usage[month]['cost'] += cost
        
        # Log usage
        logger.info(f"OpenAI API Usage - Model: {model}, Tokens: {tokens}, Cost: ${cost:.4f}")
        
        # Check limits
        if self.monthly_usage[month]['cost'] > 50:  # Example limit
            logger.warning(f"Monthly OpenAI cost exceeded $50: ${self.monthly_usage[month]['cost']:.2f}")

usage_tracker = OpenAIUsageTracker()
```

### Implement Cost Calculation
```python
def calculate_cost(model: str, tokens: int) -> float:
    # Current pricing as of 2024
    pricing = {
        'gpt-4': 0.03,  # $0.03 per 1K tokens
        'gpt-3.5-turbo': 0.002  # $0.002 per 1K tokens
    }
    return (tokens / 1000) * pricing.get(model, 0.03)
```

### Track API Calls
```python
@app.post("/api/v1/analyze_data")
async def analyze_data(request: Request):
    try:
        # Your existing code...
        response = await openai.ChatCompletion.create(
            model="gpt-4",
            messages=[...]
        )
        
        # Track usage
        tokens = response.usage.total_tokens
        cost = calculate_cost("gpt-4", tokens)
        usage_tracker.track_request("gpt-4", tokens, cost)
        
        # Continue with your code...
    except Exception as e:
        logger.exception("Error in analyze_data")
        raise
```

## 3. Monitoring Endpoints

### Add Usage Endpoints
```python
@app.get("/api/v1/usage/daily")
async def get_daily_usage():
    return {
        "status": "success",
        "data": usage_tracker.daily_usage
    }

@app.get("/api/v1/usage/monthly")
async def get_monthly_usage():
    return {
        "status": "success",
        "data": usage_tracker.monthly_usage
    }
```

## 4. Alert Configuration

### Email Alerts
```python
async def send_usage_alert(subject: str, message: str):
    # Configure with your email service
    pass

async def check_usage_limits():
    month = datetime.now().strftime('%Y-%m')
    usage = usage_tracker.monthly_usage.get(month, {'cost': 0})
    
    if usage['cost'] > 100:  # Critical limit
        await send_usage_alert(
            "Critical: OpenAI Usage Alert",
            f"Monthly usage has exceeded $100: ${usage['cost']:.2f}"
        )
    elif usage['cost'] > 50:  # Warning limit
        await send_usage_alert(
            "Warning: OpenAI Usage Alert",
            f"Monthly usage has exceeded $50: ${usage['cost']:.2f}"
        )
```

## 5. Usage Dashboard

### Create Monitoring Dashboard
```python
@app.get("/api/v1/usage/dashboard")
async def get_usage_dashboard():
    month = datetime.now().strftime('%Y-%m')
    date = datetime.now().strftime('%Y-%m-%d')
    
    return {
        "status": "success",
        "data": {
            "current_month": {
                "usage": usage_tracker.monthly_usage.get(month, {}),
                "limit": 100,
                "remaining": 100 - usage_tracker.monthly_usage.get(month, {'cost': 0})['cost']
            },
            "current_day": {
                "usage": usage_tracker.daily_usage.get(date, {}),
                "limit": 10,
                "remaining": 10 - usage_tracker.daily_usage.get(date, {'cost': 0})['cost']
            },
            "history": {
                "daily": usage_tracker.daily_usage,
                "monthly": usage_tracker.monthly_usage
            }
        }
    }
```

## 6. Cost Control Measures

### Implement Rate Limiting
```python
from fastapi import HTTPException
from datetime import datetime, timedelta

async def check_rate_limits(user_id: str) -> bool:
    # Example: 10 requests per minute per user
    minute = datetime.now().strftime('%Y-%m-%d-%H-%M')
    user_key = f"rate_limit:{user_id}:{minute}"
    
    # Implement with Redis or similar
    current_usage = cache.get(user_key, 0)
    if current_usage >= 10:
        return False
    
    cache.incr(user_key)
    cache.expire(user_key, 60)  # Expire after 1 minute
    return True
```

### Implement Usage Quotas
```python
async def check_user_quota(user_id: str) -> bool:
    month = datetime.now().strftime('%Y-%m')
    user_usage = get_user_monthly_usage(user_id, month)
    
    # Example: $10 monthly limit per user
    if user_usage > 10:
        return False
    return True
```

## 7. Monitoring Strategy

### Daily Checks
```
1. Review total usage
2. Check per-user usage
3. Monitor error rates
4. Review cost trends
```

### Weekly Analysis
```
1. Usage patterns
2. Cost optimization
3. User quotas
4. Performance impact
```

### Monthly Review
```
1. Cost analysis
2. Usage optimization
3. Quota adjustments
4. Budget planning
```

## 8. Emergency Procedures

### Cost Spike Response
```
1. Identify source
2. Implement immediate limits
3. Notify stakeholders
4. Adjust quotas
```

### Service Degradation
```
1. Switch to backup model
2. Reduce token limits
3. Increase caching
4. Notify users
``` 