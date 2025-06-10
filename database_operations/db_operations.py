import psycopg2
import lancedb
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import numpy as np
from typing import Dict, Any, List, Optional

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
        self._init_lance_tables()
    
    def _init_lance_tables(self):
        """Initialize LanceDB tables if they don't exist"""
        try:
            # Create test_cases table if it doesn't exist
            if "test_cases" not in self.lance_db.table_names():
                schema = {
                    "story_id": "int64",
                    "test_case_id": "string",
                    "title": "string",
                    "description": "string",
                    "steps": "string",
                    "preconditions": "string",
                    "priority": "string",
                    "type": "string",
                    "embedding": "float32[384]",  # Assuming 384-dimensional embeddings
                    "created_at": "timestamp"
                }
                self.lance_db.create_table("test_cases", schema=schema)
        except Exception as e:
            print(f"Error initializing LanceDB tables: {str(e)}")
    
    def add_user_story(self, title: str, description: str) -> int:
        """Add a new user story to PostgreSQL"""
        with self.pg_conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_stories (title, description)
                VALUES (%s, %s)
                RETURNING id
            """, (title, description))
            story_id = cur.fetchone()[0]
            self.pg_conn.commit()
        return story_id
    
    def add_test_cases(self, story_id: int, test_cases: List[Dict[str, Any]]):
        """Add test cases to LanceDB"""
        try:
            test_cases_table = self.lance_db.open_table("test_cases")
            
            # Prepare test cases for LanceDB
            lance_test_cases = []
            for tc in test_cases:
                # Generate embedding for the test case (you should implement this)
                embedding = self._get_embedding(f"{tc['title']} {tc['description']}")
                
                lance_test_cases.append({
                    "story_id": story_id,
                    "test_case_id": tc['id'],
                    "title": tc['title'],
                    "description": tc['description'],
                    "steps": json.dumps(tc['steps']),
                    "preconditions": json.dumps(tc.get('preconditions', [])),
                    "priority": tc.get('priority', 'Medium'),
                    "type": tc.get('type', 'Functional'),
                    "embedding": embedding,
                    "created_at": datetime.now()
                })
            
            # Add test cases to LanceDB
            test_cases_table.add(lance_test_cases)
            return True
        except Exception as e:
            print(f"Error adding test cases: {str(e)}")
            return False
    
    def get_story(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Get a story with its test cases"""
        try:
            # Get story from PostgreSQL
            with self.pg_conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, description, created_at
                    FROM user_stories
                    WHERE id = %s
                """, (story_id,))
                story = cur.fetchone()
                
                if not story:
                    return None
            
            # Get test cases from LanceDB
            test_cases_table = self.lance_db.open_table("test_cases")
            test_cases = test_cases_table.to_pandas()
            story_test_cases = test_cases[test_cases['story_id'] == story_id]
            
            # Format test cases
            formatted_test_cases = []
            for _, tc in story_test_cases.iterrows():
                formatted_test_cases.append({
                    'id': tc['test_case_id'],
                    'title': tc['title'],
                    'description': tc['description'],
                    'steps': json.loads(tc['steps']),
                    'preconditions': json.loads(tc['preconditions']),
                    'priority': tc['priority'],
                    'type': tc['type']
                })
            
            return {
                'id': story[0],
                'title': story[1],
                'description': story[2],
                'created_at': story[3].isoformat(),
                'test_cases': formatted_test_cases
            }
        except Exception as e:
            print(f"Error getting story: {str(e)}")
            return None
    
    def get_recent_stories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent stories with their test case status"""
        try:
            with self.pg_conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, description, created_at
                    FROM user_stories
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))
                
                stories = []
                for row in cur.fetchall():
                    # Check if story has test cases in LanceDB
                    test_cases_table = self.lance_db.open_table("test_cases")
                    test_cases = test_cases_table.to_pandas()
                    has_test_cases = not test_cases[test_cases['story_id'] == row[0]].empty
                    
                    stories.append({
                        'id': row[0],
                        'title': row[1],
                        'description': row[2],
                        'created_at': row[3].isoformat(),
                        'has_test_cases': has_test_cases
                    })
                return stories
        except Exception as e:
            print(f"Error getting recent stories: {str(e)}")
            return []
    
    def search_similar_test_cases(self, query: str, story_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar test cases using LanceDB vector search"""
        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)
            
            # Search in LanceDB
            test_cases_table = self.lance_db.open_table("test_cases")
            results = test_cases_table.search(query_embedding).metric("cosine").limit(limit).to_pandas()
            
            # Filter results for the specific story
            story_results = results[results['story_id'] == story_id]
            
            # Format results
            similar_test_cases = []
            for _, tc in story_results.iterrows():
                similar_test_cases.append({
                    'id': tc['test_case_id'],
                    'title': tc['title'],
                    'description': tc['description'],
                    'similarity_score': float(tc['_distance']),
                    'steps': json.loads(tc['steps']),
                    'preconditions': json.loads(tc['preconditions']),
                    'priority': tc['priority'],
                    'type': tc['type']
                })
            
            return similar_test_cases
        except Exception as e:
            print(f"Error searching similar test cases: {str(e)}")
            return []
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text (placeholder - implement with your preferred embedding model)"""
        # This is a placeholder - you should implement this using your preferred embedding model
        # For example, you could use sentence-transformers, OpenAI embeddings, etc.
        return np.random.rand(384).tolist()  # Placeholder: random 384-dimensional vector
    
    def close(self):
        """Close database connections"""
        self.pg_conn.close()

if __name__ == "__main__":
    # Example usage
    db = DatabaseOperations()
    
    # Add a test story
    story_id = db.add_user_story(
        title="Test Story",
        description="This is a test story"
    )
    
    # Add test cases
    test_cases = [
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
            ],
            "preconditions": ["Precondition 1"],
            "priority": "High",
            "type": "Functional"
        }
    ]
    db.add_test_cases(story_id, test_cases)
    
    # Get story
    story = db.get_story(story_id)
    print("Story:", story)
    
    # Get recent stories
    stories = db.get_recent_stories()
    print("Recent stories:", stories)
    
    # Search similar test cases
    similar_cases = db.search_similar_test_cases("test action", story_id)
    print("Similar test cases:", similar_cases)
    
    db.close() 