"""
SQLAlchemy models for F1 data storage.
These models represent various aspects of Formula 1 data including races,
drivers, constructors, and their relationships.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from app.database.config import Base
from datetime import datetime

class F1Driver(Base):
    __tablename__ = "f1_drivers"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(String, unique=True, nullable=False)
    code = Column(String(3))  # Driver's three-letter code
    number = Column(Integer)
    given_name = Column(String)
    family_name = Column(String)
    nationality = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    results = relationship("F1RaceResult", back_populates="driver")
    qualifying_results = relationship("F1QualifyingResult", back_populates="driver")

class F1Constructor(Base):
    __tablename__ = "f1_constructors"

    id = Column(Integer, primary_key=True, index=True)
    constructor_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    nationality = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    results = relationship("F1RaceResult", back_populates="constructor")
    qualifying_results = relationship("F1QualifyingResult", back_populates="constructor")

class F1Circuit(Base):
    __tablename__ = "f1_circuits"

    id = Column(Integer, primary_key=True, index=True)
    circuit_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    location = Column(String)
    country = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    races = relationship("F1Race", back_populates="circuit")

class F1Race(Base):
    __tablename__ = "f1_races"

    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(String, unique=True, nullable=False)
    season = Column(Integer, nullable=False)
    round = Column(Integer, nullable=False)
    circuit_id = Column(String, ForeignKey("f1_circuits.circuit_id"))
    name = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    time = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    circuit = relationship("F1Circuit", back_populates="races")
    results = relationship("F1RaceResult", back_populates="race")
    qualifying_results = relationship("F1QualifyingResult", back_populates="race")

    __table_args__ = (
        UniqueConstraint('season', 'round', name='uix_season_round'),
    )

class F1RaceResult(Base):
    __tablename__ = "f1_race_results"

    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(String, ForeignKey("f1_races.race_id"), nullable=False)
    driver_id = Column(String, ForeignKey("f1_drivers.driver_id"), nullable=False)
    constructor_id = Column(String, ForeignKey("f1_constructors.constructor_id"), nullable=False)
    grid = Column(Integer)
    position = Column(Integer)
    position_text = Column(String)  # For cases like "R" for retired
    position_order = Column(Integer)
    points = Column(Float, nullable=False)
    laps = Column(Integer)
    time = Column(String)  # Race duration
    milliseconds = Column(Integer)  # Race duration in milliseconds
    fastest_lap = Column(String)
    fastest_lap_time = Column(String)
    status = Column(String)  # Finished, Retired, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    race = relationship("F1Race", back_populates="results")
    driver = relationship("F1Driver", back_populates="results")
    constructor = relationship("F1Constructor", back_populates="results")

    __table_args__ = (
        UniqueConstraint('race_id', 'driver_id', name='uix_race_driver'),
    )

class F1QualifyingResult(Base):
    __tablename__ = "f1_qualifying_results"

    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(String, ForeignKey("f1_races.race_id"), nullable=False)
    driver_id = Column(String, ForeignKey("f1_drivers.driver_id"), nullable=False)
    constructor_id = Column(String, ForeignKey("f1_constructors.constructor_id"), nullable=False)
    position = Column(Integer)
    q1 = Column(String)  # Q1 time
    q2 = Column(String)  # Q2 time
    q3 = Column(String)  # Q3 time
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    race = relationship("F1Race", back_populates="qualifying_results")
    driver = relationship("F1Driver", back_populates="qualifying_results")
    constructor = relationship("F1Constructor", back_populates="qualifying_results")

    __table_args__ = (
        UniqueConstraint('race_id', 'driver_id', name='uix_qualifying_driver'),
    )

class F1DriverStanding(Base):
    __tablename__ = "f1_driver_standings"

    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(String, ForeignKey("f1_races.race_id"), nullable=False)
    driver_id = Column(String, ForeignKey("f1_drivers.driver_id"), nullable=False)
    points = Column(Float, nullable=False)
    position = Column(Integer, nullable=False)
    wins = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('race_id', 'driver_id', name='uix_standing_driver'),
    )

class F1ConstructorStanding(Base):
    __tablename__ = "f1_constructor_standings"

    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(String, ForeignKey("f1_races.race_id"), nullable=False)
    constructor_id = Column(String, ForeignKey("f1_constructors.constructor_id"), nullable=False)
    points = Column(Float, nullable=False)
    position = Column(Integer, nullable=False)
    wins = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('race_id', 'constructor_id', name='uix_standing_constructor'),
    ) 