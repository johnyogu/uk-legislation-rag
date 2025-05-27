from typing import Dict, List
import psycopg2
from psycopg2.extras import DictCursor

def get_db_connection(db_config: Dict[str, str]):
    """Get a database connection"""
    return psycopg2.connect(**db_config)

def get_legislation_chunks(db_config: Dict[str, str], limit: int = None) -> List[Dict[str, str]]:
    """Retrieve legislation chunks from database"""
    query = """
        SELECT c.id, c.legislation_id, c.chunk_number, c.text, 
               l.title, l.year, l.number, l.source_url
        FROM legislation_chunks c
        JOIN legislation l ON c.legislation_id = l.id
    """
    
    if limit:
        query += f" LIMIT {limit}"
        
    with get_db_connection(db_config) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]