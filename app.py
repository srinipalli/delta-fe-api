from flask import Flask,send_file,request
import lancedb
import pandas as pd
import psycopg2
import os
from api_calls import get_top_user_stories, get_postgres_data, generate_excel
from flask import jsonify
 
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"


@app.route("/latest-stories", methods=["GET"])
def latest_stories():
    user_df = get_top_user_stories()
    testcase_df = get_postgres_data()
    
    merged_df = pd.merge(user_df, testcase_df, on="story_id", how="left")

    response_data = []
    for _, row in merged_df.iterrows():
        response_data.append({
            "story_id": row["story_id"],
            "description": row.get("story", ""),
            "testcases_generated": row.get("testcases_generated", ""),
            "source": row.get("source", ""),
            "timestamp": row["timestamp"],
            "download_link": f"/download-excel/{row['story_id']}"
        })
    return jsonify(response_data)


@app.route("/download-excel/<story_id>", methods=["GET"])
def download_excel(story_id):
    user_df = get_top_user_stories()
    testcase_df = get_postgres_data()

    # Filter for the specific story_id
    user_row = user_df[user_df["story_id"] == story_id]
    test_row = testcase_df[testcase_df["story_id"] == story_id]

    if user_row.empty or test_row.empty:
        return jsonify({"error": "Story not found"}), 404

    combined_df = pd.merge(user_row, test_row, on="story_id")
    file_path = generate_excel(combined_df, story_id)
    return send_file(file_path, as_attachment=True)
@app.route("/search-story", methods=["GET"])
def search_story():
    story_id = request.args.get("story_id")
    if not story_id:
        return jsonify({"error": "Please provide story_id as a query parameter"}), 400

    user_df = get_top_user_stories(limit=1000)  # or read all if needed
    testcase_df = get_postgres_data()

    user_row = user_df[user_df["story_id"] == story_id]
    test_row = testcase_df[testcase_df["story_id"] == story_id]

    if user_row.empty:
        return jsonify({"error": f"Story ID '{story_id}' not found in LanceDB"}), 404

    merged_df = pd.merge(user_row, test_row, on="story_id", how="left")

    row = merged_df.iloc[0]  # Get the first row safely
    data = {
        "story_id": row["story_id"],
        "description": row.get("story", ""),
        "testcases_generated": row.get("testcases_generated", ""),
        "source": row.get("source", ""),
        "timestamp": row["timestamp"],
        "download_link": f"/download-excel/{row['story_id']}"
    }

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)