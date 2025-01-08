# Production Deployment Guide

This guide outlines the successful deployment of the F1 Data Analysis System in production using Vercel for the frontend and Railway for the backend.

## Architecture Overview

The system is deployed with the following architecture:

- Frontend: Deployed on Vercel (Next.js application)
- Backend: Deployed on Railway (FastAPI application)
- Database: PostgreSQL hosted on Railway

## Frontend Deployment (Vercel)

### Current Deployment
- URL: `https://frontend2-fpi53khr2-barat-paims-projects.vercel.app`
- Repository: Connected to the main branch
- Framework: Next.js 14.2.16
- Environment Variables:
  - `NEXT_PUBLIC_API_URL`: Set to `https://orbit-vi-production.up.railway.app`

### API Routes
The frontend implements API routes that proxy requests to the backend:
- `/api/v1/process_query`: Processes natural language queries
- `/api/v1/fetch_data`: Fetches F1 data based on requirements
- `/api/v1/analyze_data`: Generates analysis and visualizations
- `/api/v1/query_history`: Manages user query history

### Deployment Steps
1. Push code to the main branch
2. Vercel automatically triggers deployment
3. Build process:
   - Installs dependencies
   - Builds Next.js application
   - Generates API routes
   - Deploys to production

## Backend Deployment (Railway)

### Current Deployment
- URL: `https://orbit-vi-production.up.railway.app`
- Services:
  - FastAPI application
  - PostgreSQL database

### Environment Variables
Required environment variables in Railway:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: API key for OpenAI services
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `JWT_ALGORITHM`: Algorithm for JWT (default: "HS256")
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Database
- Type: PostgreSQL
- Managed by: Railway
- Auto-backup: Enabled
- Migration: Automatic on deployment

## Monitoring and Maintenance

### Logs
- Frontend logs: Available in Vercel dashboard
- Backend logs: Available in Railway dashboard
- Database logs: Available in Railway dashboard

### Performance Monitoring
- Frontend: Vercel Analytics
- Backend: Railway Metrics
- Database: Railway PostgreSQL Metrics

### Error Tracking
- Frontend: Vercel Error Tracking
- Backend: Railway Logs
- API Routes: Vercel Function Logs

## Security

### Frontend
- CORS: Configured to allow specific origins
- Environment Variables: Securely stored in Vercel
- API Routes: Protected endpoints

### Backend
- JWT Authentication
- Database Connection: Secured by Railway
- API Keys: Stored securely in Railway environment

## Backup and Recovery

### Database Backups
- Automated backups by Railway
- Point-in-time recovery available
- Manual backup option available

### Code Backups
- GitHub repository
- Vercel deployment history
- Railway deployment history

## Troubleshooting

### Common Issues and Solutions

1. 405 Method Not Allowed
   - Check API route implementation
   - Verify HTTP method matches endpoint
   - Ensure CORS is properly configured

2. Database Connection Issues
   - Verify DATABASE_URL in Railway
   - Check database service status
   - Review connection pool settings

3. Authentication Errors
   - Verify JWT configuration
   - Check token expiration settings
   - Ensure proper token handling

## Scaling

### Frontend Scaling
- Automatic scaling by Vercel
- Edge Network deployment
- Serverless functions

### Backend Scaling
- Railway auto-scaling
- Database connection pooling
- Caching implementation

## Maintenance Procedures

### Regular Maintenance
1. Monitor error logs
2. Review performance metrics
3. Update dependencies
4. Backup verification

### Emergency Procedures
1. Rollback procedures
2. Database recovery steps
3. Incident response plan

## Future Improvements

1. Custom domain setup
2. CDN integration
3. Enhanced monitoring
4. Automated testing pipeline
5. Performance optimization 