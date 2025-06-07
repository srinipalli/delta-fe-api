import psycopg2
import lancedb
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class DatabaseOperations:
    def __init__(self):
        """Initialize database connections"""
        # PostgreSQL connection
        self.pg_conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT')
        )
        
        # LanceDB connection
        self.lance_db = lancedb.connect(os.getenv('LANCE_DB_PATH'))
        self.stories_table = self.lance_db.open_table('user_stories')
    
    def add_user_story(self, title: str, description: str, vector: list, filename: str):
        """Add a new user story to both databases"""
        # Add to PostgreSQL
        with self.pg_conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_stories (title, description)
                VALUES (%s, %s)
                RETURNING id
            """, (title, description))
            story_id = cur.fetchone()[0]
            self.pg_conn.commit()
        
        # Add to LanceDB
        self.stories_table.add([{
            "story_id": str(story_id),
            "vector": vector,
            "filename": filename,
            "test_case_generated": False,
            "time_stamp": datetime.now()
        }])
        
        return story_id
    
    def add_test_cases(self, story_id: int, test_cases: dict):
        """Add test cases for a story"""
        with self.pg_conn.cursor() as cur:
            cur.execute("""
                INSERT INTO test_cases_generated (story_id, test_cases)
                VALUES (%s, %s)
            """, (story_id, json.dumps(test_cases)))
            self.pg_conn.commit()
        
        # Update LanceDB
        self.stories_table.update(
            where=f"story_id = '{story_id}'",
            values={"test_case_generated": True}
        )
    
    def get_story(self, story_id: int):
        """Get a story with its test cases"""
        with self.pg_conn.cursor() as cur:
            # Get story
            cur.execute("""
                SELECT id, title, description, created_at
                FROM user_stories
                WHERE id = %s
            """, (story_id,))
            story = cur.fetchone()
            
            if not story:
                return None
            
            # Get test cases
            cur.execute("""
                SELECT test_cases
                FROM test_cases_generated
                WHERE story_id = %s
            """, (story_id,))
            test_cases = cur.fetchone()
            
            return {
                'id': story[0],
                'title': story[1],
                'description': story[2],
                'created_at': story[3].isoformat(),
                'test_cases': json.loads(test_cases[0]) if test_cases else None
            }
    
    def get_recent_stories(self, limit: int = 10):
        """Get recent stories with their test case status"""
        with self.pg_conn.cursor() as cur:
            cur.execute("""
                SELECT s.id, s.title, s.description, s.created_at,
                       CASE WHEN t.id IS NOT NULL THEN true ELSE false END as test_case_generated
                FROM user_stories s
                LEFT JOIN test_cases_generated t ON s.id = t.story_id
                ORDER BY s.created_at DESC
                LIMIT %s
            """, (limit,))
            stories = []
            for row in cur.fetchall():
                stories.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'created_at': row[3].isoformat(),
                    'test_case_generated': row[4]
                })
            return stories
    
    def close(self):
        """Close database connections"""
        self.pg_conn.close()

if __name__ == "__main__":
    # Example usage
    db = DatabaseOperations()
    
    # Add a test story
    story_id = db.add_user_story(
        title="Test Story",
        description="This is a test story",
        vector=[0.1] * 768,  # Example vector
        filename="test.txt"
    )
    
    # Add test cases
    test_cases = {
        "test_cases": [
            {
                "id": "TC1",
                "title": "Test Case 1",
                "description": "Test Description",
                "steps": [
                    {
                        "step": 1,
                        "action": "Test Action",
                        "expected_result": "Expected Result"
                    }
                ]
            }
        ]
    }
    db.add_test_cases(story_id, test_cases)
    
    # Get story
    story = db.get_story(story_id)
    print("Story:", story)
    
    # Get recent stories
    stories = db.get_recent_stories()
    print("Recent stories:", stories)
    
    db.close() 