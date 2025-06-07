import lancedb
import os
from dotenv import load_dotenv
import pyarrow as pa

load_dotenv()

def create_lance_db():
    """Create LanceDB database and table"""
    # Get LanceDB path from environment
    lance_db_path = os.getenv('LANCE_DB_PATH')
    
    # Create directory if it doesn't exist
    os.makedirs(lance_db_path, exist_ok=True)
    
    # Connect to LanceDB
    db = lancedb.connect(lance_db_path)
    
    # Create table schema using PyArrow
    schema = pa.schema([
        pa.field("story_id", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), 768)),  # Gemini embedding dimension
        pa.field("filename", pa.string()),
        pa.field("test_case_generated", pa.bool_()),
        pa.field("time_stamp", pa.timestamp('us'))
    ])
    
    # Create table if it doesn't exist
    try:
        table = db.create_table("user_stories", schema=schema)
        print("LanceDB table created successfully!")
    except Exception as e:
        if "already exists" in str(e):
            print("LanceDB table already exists!")
        else:
            raise e

if __name__ == "__main__":
    create_lance_db() 