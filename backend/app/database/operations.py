from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.typing_stats import TypingStats

def save_typing_stats(db: Session, data: List[Dict[str, Any]], player_id: str) -> None:
    """Save typing statistics to PostgreSQL database"""
    try:
        # Sort data by game number
        sorted_data = sorted(data, key=lambda x: x['gn'])
        
        # Prepare records for bulk insert
        records = []
        for i, entry in enumerate(sorted_data, start=1):
            record = TypingStats(
                player_id=player_id,
                entry_number=i,
                speed=entry['wpm'],
                accuracy=entry['ac'],
                pts=entry.get('pts'),
                time=entry['t'],
                rank=entry.get('r'),
                game_entry=entry['gn'],
                text_id=entry.get('tid'),
                skill_level=entry.get('sl'),
                num_players=entry.get('np')
            )
            records.append(record)
        
        # Bulk insert records
        db.bulk_save_objects(records)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e

def load_typing_stats(db: Session, player_id: str = None) -> List[Dict[str, Any]]:
    """Load typing statistics from database"""
    try:
        query = db.query(TypingStats)
        if player_id:
            query = query.filter(TypingStats.player_id == player_id)
        
        records = query.all()
        return [
            {
                "id": record.id,
                "player_id": record.player_id,
                "entry_number": record.entry_number,
                "speed": record.speed,
                "accuracy": record.accuracy,
                "pts": record.pts,
                "time": record.time,
                "rank": record.rank,
                "game_entry": record.game_entry,
                "text_id": record.text_id,
                "skill_level": record.skill_level,
                "num_players": record.num_players
            }
            for record in records
        ]
    except Exception as e:
        raise e
