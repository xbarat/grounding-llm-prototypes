# GIRAFFE Project Setup Guide

## Overview
GIRAFFE is a full-stack application featuring user authentication, persistent chat sessions, and a modern React frontend. This guide will help you set up the development environment and get the application running.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Additional Documentation](#additional-documentation)

## Prerequisites

### Required Software
- Python 3.8 or higher
- Node.js 16.x or higher
- npm 8.x or higher
- Git

### System Requirements
- At least 2GB of free disk space
- 4GB RAM recommended
- Internet connection for package installation

## Project Structure
```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── auth/           # Authentication logic
│   │   ├── models/         # Database models
│   │   ├── main.py         # Main application file
│   │   └── database.py     # Database configuration
│   ├── scripts/            # Utility scripts
│   └── requirements.txt    # Python dependencies
├── frontend2/              # Next.js frontend
│   ├── components/         # React components
│   ├── app/                # Next.js pages
│   └── package.json        # Node.js dependencies
└── docs2/                  # Project documentation
```

## Quick Start

```bash
# Clone repository
git clone <repository-url>
cd GIRAFFE

# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
cd backend
pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(32))"  # Generate SECRET_KEY
python -m app.db_setup    # Initialize database

# Frontend setup
cd ../frontend2
npm install
cp .env.example .env.local

# Start services
# Terminal 1 (Backend):
cd backend
uvicorn app.main:app --reload

# Terminal 2 (Frontend):
cd frontend2
npm run dev
```

## Detailed Setup

### 1. Backend Setup

#### Environment Setup
```bash
cd backend
cp .env.example .env
```

Edit `.env` with appropriate values:
```env
# Database Configuration
DATABASE_URL=sqlite:///./sql_app.db

# JWT Authentication
SECRET_KEY=<generated-secret-key>  # Replace with output from secrets.token_urlsafe(32)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=http://localhost:3000

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

#### Database Initialization
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m app.db_setup

# Verify database setup
python scripts/view_db.py
```

### 2. Frontend Setup

#### Environment Setup
```bash
cd frontend2
cp .env.example .env.local
```

Edit `.env.local`:
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Development Settings
NODE_ENV=development
```

#### Dependencies Installation
```bash
npm install
```

## Development

### Starting the Services

#### Backend Server
```bash
cd backend
source venv/bin/activate  # Windows: .\venv\Scripts\activate
uvicorn app.main:app --reload
```
The backend will be available at `http://localhost:8000`

#### Frontend Development Server
```bash
cd frontend2
npm run dev
```
The frontend will be available at `http://localhost:3000`

### Creating First User
You can create a user through:
1. Web Interface: Visit `http://localhost:3000` and use the registration form
2. API Request:
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"your_password","email":"admin@example.com"}'
```

## Troubleshooting

### Common Issues

#### Database Issues
```bash
# Reset database
cd backend
rm sql_app.db
python -m app.db_setup
```

#### Authentication Issues
1. Clear browser storage
2. Regenerate SECRET_KEY in `.env`
3. Restart both servers

#### Frontend Build Issues
```bash
cd frontend2
rm -rf .next
rm -rf node_modules
npm install
npm run dev
```

#### CORS Issues
1. Verify backend is running on port 8000
2. Check CORS_ORIGINS in backend `.env`
3. Verify API URL in frontend `.env.local`

## Additional Documentation

- [User Management Documentation](docs2/user-management.md)
- [API Documentation](http://localhost:8000/docs) (available when backend is running)
- [Frontend Components](frontend2/README.md)

## Security Notes

1. **Environment Variables**
   - Never commit `.env` files
   - Use strong, unique SECRET_KEY
   - Keep production credentials secure

2. **Database**
   - Regular backups recommended
   - Use SQLite for development only
   - Consider PostgreSQL for production

3. **Authentication**
   - Default token expiry is 30 minutes
   - Implement password policies
   - Enable HTTPS in production

## Production Deployment

For production deployment, additional steps are required:

1. **Environment Updates**
   - Set `DEBUG=False`
   - Configure proper CORS origins
   - Use production-grade database
   - Set appropriate token expiration

2. **Security Measures**
   - Enable HTTPS
   - Set secure cookie policies
   - Configure rate limiting
   - Implement monitoring

3. **Performance**
   - Configure proper database indices
   - Enable frontend optimization
   - Setup proper logging

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

[Add License Information] 