import lancedb
import os
from dotenv import load_dotenv
import pyarrow as pa

load_dotenv()

def create_lance_db():
    lance_db_path = os.getenv('LANCE_DB_PATH')
    os.makedirs(lance_db_path, exist_ok=True)
    db = lancedb.connect(lance_db_path)


    schema = pa.schema([
        pa.field("story_id", pa.string()),
        pa.field("story_Description", pa.string()),
        pa.field("story_Description_vector", pa.list_(pa.float32(), 768)),  # Gemini embedding dimension
        pa.field("Processed_Flag", pa.bool_()),
        pa.field("time_stamp", pa.timestamp('us'))
    ])

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