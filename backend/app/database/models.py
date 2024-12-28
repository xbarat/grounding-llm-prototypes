"""
SQLAlchemy models for platform data caching and connections.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PlatformCache(Base):
    """Model for caching platform data."""
    __tablename__ = "platform_cache"
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)
    identifier = Column(String(100), nullable=False)
    data = Column(Text, nullable=False)  # JSON data stored as text
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    __table_args__ = (
        # Index for faster lookups
        {'sqlite_on_conflict': 'REPLACE'}
    )

class PlatformConnection(Base):
    """Model for tracking platform connections."""
    __tablename__ = "platform_connections"
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)
    identifier = Column(String(100), nullable=False)
    is_connected = Column(Boolean, nullable=False, default=False)
    last_sync = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (
        # Index for faster lookups
        {'sqlite_on_conflict': 'REPLACE'}
    ) 