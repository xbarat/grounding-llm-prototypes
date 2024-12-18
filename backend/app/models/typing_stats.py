from sqlalchemy import Column, Integer, Float, String, UniqueConstraint
from app.database.config import Base

class TypingStats(Base):
    __tablename__ = "typing_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, nullable=False)
    entry_number = Column(Integer, nullable=False)
    speed = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)
    pts = Column(Float)
    time = Column(Float, nullable=False)
    rank = Column(Integer)
    game_entry = Column(Integer, nullable=False)
    text_id = Column(Integer)
    skill_level = Column(String)
    num_players = Column(Integer)

    __table_args__ = (
        UniqueConstraint('player_id', 'entry_number', name='uix_player_entry'),
    )
