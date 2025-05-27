from typing import List, Dict
import psycopg2
from psycopg2 import sql
import logging

logger = logging.getLogger(__name__)

class DatabaseLoader:
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.conn = None
        
    def __enter__(self):
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def connect(self):
        """Connect to PostgreSQL database"""
        self.conn = psycopg2.connect(**self.db_config)
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def initialize_database(self):
        """Create required tables"""
        with self.conn.cursor() as cursor:
            # Legislation metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS legislation (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    year TEXT,
                    number TEXT,
                    type TEXT,
                    date TEXT,
                    source_url TEXT UNIQUE,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Legislation chunks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS legislation_chunks (
                    id SERIAL PRIMARY KEY,
                    legislation_id INTEGER REFERENCES legislation(id),
                    chunk_number INTEGER,
                    text TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            
    def save_legislation(self, legislation: Dict) -> int:
        """Save legislation metadata and return ID"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO legislation (title, year, number, type, date, source_url)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_url) DO UPDATE SET
                    title = EXCLUDED.title,
                    year = EXCLUDED.year,
                    number = EXCLUDED.number,
                    type = EXCLUDED.type,
                    date = EXCLUDED.date,
                    processed_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (
                legislation['metadata']['title'],
                legislation['metadata']['year'],
                legislation['metadata']['number'],
                legislation['metadata'].get('type', ''),
                legislation['metadata'].get('date', ''),
                legislation['metadata']['source_url']
            ))
            
            result = cursor.fetchone()
            self.conn.commit()
            return result[0] if result else None
            
    def save_chunks(self, legislation_id: int, chunks: List[Dict]):
        """Save legislation text chunks"""
        with self.conn.cursor() as cursor:
            for chunk in chunks:
                cursor.execute("""
                    INSERT INTO legislation_chunks (legislation_id, chunk_number, text)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (legislation_id, chunk_number) DO UPDATE SET
                        text = EXCLUDED.text,
                        processed_at = CURRENT_TIMESTAMP
                """, (legislation_id, chunk['chunk_number'], chunk['text']))
                
            self.conn.commit()