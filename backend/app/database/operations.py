from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.typing_stats import TypingStats
from sqlalchemy.dialects.postgresql import insert

def save_typing_stats(db: Session, data: List[Dict], player_id: str) -> None:
    """Save typing stats to database using UPSERT to handle duplicates."""
    # Convert the data into a list of dictionaries for bulk upsert
    records = []
    for i, game in enumerate(data, start=1):
        record = {
            'player_id': player_id,
            'entry_number': i,
            'speed': game.get('wpm', 0),
            'accuracy': game.get('accuracy', 0),
            'pts': game.get('pts', 0),
            'time': game.get('t', 0),
            'rank': game.get('rank', 0),
            'game_entry': game.get('gn', 0),
            'text_id': game.get('tid', 0),
            'skill_level': game.get('sl', ''),
            'num_players': game.get('np', 0)
        }
        records.append(record)

    # Create the upsert statement
    stmt = insert(TypingStats).values(records)
    stmt = stmt.on_conflict_do_update(
        constraint='uix_player_entry',
        set_={
            'speed': stmt.excluded.speed,
            'accuracy': stmt.excluded.accuracy,
            'pts': stmt.excluded.pts,
            'time': stmt.excluded.time,
            'rank': stmt.excluded.rank,
            'game_entry': stmt.excluded.game_entry,
            'text_id': stmt.excluded.text_id,
            'skill_level': stmt.excluded.skill_level,
            'num_players': stmt.excluded.num_players
        }
    )
    
    try:
        db.execute(stmt)
        db.commit()
    except Exception as e:
        print(f"Error saving typing stats: {str(e)}")
        db.rollback()
        raise

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
