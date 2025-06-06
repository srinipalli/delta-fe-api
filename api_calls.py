import lancedb
import pandas as pd
import psycopg2
import os
from flask import Flask, jsonify, send_file




def get_top_user_stories(limit=10):
    db = lancedb.connect("my_lance_db")
    table = db.open_table("user_stories")
    df = table.to_pandas()
    df = df.sort_values(by="timestamp", ascending=False).head(limit)
    return df[["story_id", "file_name", "test_case_generated", "timestamp"]]
def get_postgres_data():
    conn = psycopg2.connect(
        host="localhost",
        dbname="testcases_db",
        user="your_user",
        password="your_password"
    )
    query = "SELECT story_id, story, testcases_generated, source, timestamp FROM test_cases_generated"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
def generate_excel(data: pd.DataFrame, story_id: str) -> str:
    file_path = f"downloads/{story_id}.xlsx"
    os.makedirs("downloads", exist_ok=True)
    data.to_excel(file_path, index=False)
    return file_path
