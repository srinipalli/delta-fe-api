import psycopg2
import lancedb
import json
from typing import Dict, Any, List, Optional

class DatabaseService:
    def __init__(self, postgres_config: Dict[str, Any], lance_db_path: str):
        """Initialize database connections"""
        self.postgres_config = postgres_config
        self.lance_db_path = lance_db_path
        self.lance_db = lancedb.connect(lance_db_path)
        
    def get_recent_stories(self) -> List[Dict[str, Any]]:
        """Get recent stories from PostgreSQL"""
        with psycopg2.connect(**self.postgres_config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, description, created_at
                    FROM user_stories
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
                stories = []
                for row in cur.fetchall():
                    stories.append({
                        'id': row[0],
                        'title': row[1],
                        'description': row[2],
                        'created_at': row[3].isoformat()
                    })
                return stories
    
    def get_story(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific story by ID"""
        with psycopg2.connect(**self.postgres_config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, description, created_at
                    FROM user_stories
                    WHERE id = %s
                """, (story_id,))
                row = cur.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'title': row[1],
                        'description': row[2],
                        'created_at': row[3].isoformat()
                    }
                return None
    
    def get_test_cases(self, story_id: int) -> Dict[str, Any]:
        """Get test cases for a story"""
        with psycopg2.connect(**self.postgres_config) as conn:
            with conn.cursor() as cur:
                # Get story details
                cur.execute("""
                    SELECT id, title, description
                    FROM user_stories
                    WHERE id = %s
                """, (story_id,))
                story_row = cur.fetchone()
                if not story_row:
                    return {'error': 'Story not found'}
                
                # Get test cases
                cur.execute("""
                    SELECT test_cases
                    FROM test_cases_generated
                    WHERE story_id = %s
                """, (story_id,))
                test_cases_row = cur.fetchone()
                
                if not test_cases_row:
                    return {
                        'story': {
                            'id': story_row[0],
                            'title': story_row[1],
                            'description': story_row[2]
                        },
                        'test_cases': []
                    }
                
                return {
                    'story': {
                        'id': story_row[0],
                        'title': story_row[1],
                        'description': story_row[2]
                    },
                    'test_cases': test_cases_row[0]
                } 