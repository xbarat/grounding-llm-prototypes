# User Management and History Feature Documentation

## Overview
This document details the implementation of user authentication, session management, and chat history features in the application.

## Architecture

### Key Components
1. **Backend Components** (`backend/app/`)
   - `auth/routes.py`: Authentication endpoints
   - `auth/utils.py`: Authentication utilities
   - `models/user.py`: User and QueryHistory models
   - `database.py`: Database configuration
   - `main.py`: Main FastAPI application

2. **Frontend Components** (`frontend2/`)
   - `components/sidebar.tsx`: User interface for auth and history
   - `next.config.mjs`: API proxy configuration
   - Local storage for token management

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE,
    email VARCHAR UNIQUE,
    hashed_password VARCHAR,
    created_at TIMESTAMP,
    last_login TIMESTAMP
);
```

### Query History Table
```sql
CREATE TABLE query_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    parent_id INTEGER REFERENCES query_history(id),
    query VARCHAR,
    result JSON,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## API Endpoints

### Authentication Endpoints
1. **Register User**
   - Path: `/auth/register`
   - Method: `POST`
   - Body:
     ```json
     {
       "username": "string",
       "password": "string",
       "email": "string | null"
     }
     ```
   - Response:
     ```json
     {
       "access_token": "string",
       "token_type": "bearer",
       "username": "string"
     }
     ```

2. **Login**
   - Path: `/auth/token`
   - Method: `POST`
   - Body (form-urlencoded):
     ```
     username=string&password=string
     ```
   - Response: Same as register

### History Endpoints
1. **Save Query History**
   - Path: `/api/v1/query_history`
   - Method: `POST`
   - Headers: `Authorization: Bearer <token>`
   - Body:
     ```json
     {
       "query": "string",
       "data": "object",
       "parent_id": "number | null"
     }
     ```

2. **Get Query History**
   - Path: `/api/v1/query_history`
   - Method: `GET`
   - Headers: `Authorization: Bearer <token>`
   - Response:
     ```json
     {
       "status": "success",
       "data": {
         "queries": [
           {
             "id": "string",
             "title": "string",
             "thread": [
               {
                 "id": "string",
                 "query": "string",
                 "result": "object",
                 "timestamp": "string"
               }
             ],
             "timestamp": "string"
           }
         ]
       }
     }
     ```

## Authentication Flow

1. **Registration**
   - User submits username/password
   - Backend hashes password
   - Creates user record
   - Returns JWT token

2. **Login**
   - User submits credentials
   - Backend verifies password
   - Updates last_login timestamp
   - Returns JWT token

3. **Session Management**
   - Frontend stores token in localStorage
   - Token included in Authorization header
   - Backend validates token for protected routes

## History Feature Implementation

### Storage
- Hierarchical structure using parent_id
- JSON storage for query results
- Timestamps for sorting and display

### Frontend Implementation
- Real-time history updates
- Threaded conversation view
- Automatic token management

## Security Measures

1. **Password Security**
   - Bcrypt hashing
   - Salt rounds configuration
   - No plain text storage

2. **Token Security**
   - JWT with expiration
   - Secure token storage
   - Authorization header usage

3. **API Security**
   - CORS configuration
   - Protected routes
   - Input validation

## Migration Guide: Moving to Auth0

### Required Changes

1. **Backend Changes**
   - Remove local JWT implementation
   - Add Auth0 middleware
   - Update user model
   - Modify authentication endpoints

2. **Frontend Changes**
   - Add Auth0 React SDK
   - Update login/register UI
   - Modify token management
   - Update API calls

### Migration Steps

1. **Auth0 Setup**
   ```typescript
   // Example Auth0 configuration
   const auth0Config = {
     domain: 'your-domain.auth0.com',
     clientId: 'your-client-id',
     audience: 'your-api-identifier'
   };
   ```

2. **Backend Integration**
   ```python
   # Example Auth0 middleware
   from fastapi_auth0 import Auth0
   auth = Auth0(
       domain='your-domain.auth0.com',
       api_audience='your-api-identifier'
   )
   ```

3. **Frontend Integration**
   ```typescript
   // Example Auth0 hook usage
   import { useAuth0 } from '@auth0/auth0-react';
   
   const { loginWithRedirect, logout, user } = useAuth0();
   ```

4. **Data Migration**
   - Map existing users to Auth0 users
   - Update database schema
   - Migrate existing tokens

### Auth0 Benefits
- Managed authentication
- Social login support
- Enhanced security features
- MFA support
- Compliance standards

## Development Notes

### Required Environment Variables
```env
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./sql_app.db
```

### Development Setup
1. Database initialization
2. Environment configuration
3. Backend server setup
4. Frontend proxy configuration

### Testing
- Authentication unit tests
- Token validation tests
- History feature integration tests

## Maintenance and Monitoring

### Regular Tasks
1. Token cleanup
2. History cleanup
3. Database optimization
4. Security updates

### Monitoring Points
1. Failed login attempts
2. Token usage patterns
3. History storage metrics
4. API response times 

## Dependencies and Environment Setup

### Backend Dependencies
```requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.2
python-jose[cryptography]==3.3.0  # For JWT
passlib[bcrypt]==1.7.4  # For password hashing
python-multipart==0.0.6  # For form data parsing
python-dotenv==1.0.0
```

### Frontend Dependencies
```package.json
{
  "dependencies": {
    "@radix-ui/react-collapsible": "^1.1.2",
    "@radix-ui/react-dialog": "^1.1.4",
    "@radix-ui/react-label": "^2.1.1",
    "@radix-ui/react-slot": "^1.1.1",
    "lucide-react": "^0.468.0",
    "next": "14.2.16",
    "next-themes": "^0.4.4",
    "react": "^18",
    "react-dom": "^18"
  }
}
```

### Critical Environment Variables
```env
# Backend (.env)
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./sql_app.db
CORS_ORIGINS=http://localhost:3000

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Crisis Management Guide

### 1. Database Issues

#### SQLite Database Corruption
```bash
# Backup existing database
cp sql_app.db sql_app.backup.db

# Create new database
rm sql_app.db
cd backend
python -m app.db_migrations
```

#### Lost Database
1. Check for backups in `sql_app.backup.db`
2. If no backup:
   ```bash
   cd backend
   python -m app.db_migrations  # Recreates schema
   ```
3. Users will need to re-register

### 2. Authentication Failures

#### JWT Issues
1. Check SECRET_KEY in .env
2. Verify token expiration time
3. Clear frontend storage:
   ```javascript
   localStorage.clear()
   ```
4. Regenerate SECRET_KEY:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

#### Password Reset
1. Temporary admin access:
   ```python
   # backend/scripts/reset_password.py
   from app.database import SessionLocal
   from app.models.user import User
   from app.auth.utils import get_password_hash

   def reset_user_password(username: str, new_password: str):
       db = SessionLocal()
       user = db.query(User).filter(User.username == username).first()
       if user:
           user.hashed_password = get_password_hash(new_password)
           db.commit()
           print(f"Password reset for {username}")
   ```

### 3. Frontend Issues

#### Node Modules Problems
```bash
# Clean install
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# If still failing
npm install --legacy-peer-deps
```

#### Build Issues
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

### 4. API Connection Issues

#### CORS Errors
1. Verify CORS settings in `main.py`
2. Check frontend API URL configuration
3. Verify proxy settings in `next.config.mjs`

#### Proxy Issues
1. Check backend server is running
2. Verify ports (8000 for backend, 3000 for frontend)
3. Check `next.config.mjs`:
   ```javascript
   async rewrites() {
     return [
       {
         source: '/auth/:path*',
         destination: 'http://localhost:8000/auth/:path*'
       }
     ]
   }
   ```

### 5. Version Control Recovery

#### Missing Dependencies
1. Backend:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

2. Frontend:
   ```bash
   npm install
   # If using specific version:
   npm install --legacy-peer-deps
   ```

#### Environment Setup
1. Create `.env` files from templates:
   ```bash
   cp .env.example .env  # Backend
   cp .env.local.example .env.local  # Frontend
   ```

2. Generate new secrets:
   ```python
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### 6. Emergency Contacts

```yaml
Technical Leads:
  Backend:
    - Name: [Lead Backend Developer]
    - Contact: [Contact Info]
  Frontend:
    - Name: [Lead Frontend Developer]
    - Contact: [Contact Info]
  DevOps:
    - Name: [DevOps Lead]
    - Contact: [Contact Info]
```

### 7. Recovery Checklist

1. **Environment**
   - [ ] Check all .env files
   - [ ] Verify database connection
   - [ ] Confirm API endpoints

2. **Dependencies**
   - [ ] Verify Python virtual environment
   - [ ] Check node_modules
   - [ ] Confirm package versions

3. **Database**
   - [ ] Check schema version
   - [ ] Verify data integrity
   - [ ] Test user authentication

4. **Services**
   - [ ] Confirm backend running
   - [ ] Verify frontend build
   - [ ] Test API connectivity

### 8. Backup Procedures

1. **Database Backups**
   ```bash
   # Daily backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d)
   cp sql_app.db backups/sql_app_$DATE.db
   ```

2. **Environment Backups**
   ```bash
   # Save all env files (encrypted)
   tar -czf env_backup.tar.gz .env* && gpg -c env_backup.tar.gz
   ```

3. **Regular Maintenance**
   - Weekly database optimization
   - Monthly token cleanup
   - Quarterly dependency updates 