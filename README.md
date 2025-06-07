# Test Case Viewer API

A Flask-based REST API for viewing user stories and their associated test cases.

## Features

- View user stories
- View test cases for stories
- Download test cases as Excel files

## API Endpoints

### User Stories

1. **Get Recent Stories**
   ```
   GET /api/stories/
   ```
   Returns a list of the 10 most recent user stories.

2. **Get Story by ID**
   ```
   GET /api/stories/<story_id>
   ```
   Returns detailed information about a specific user story.

### Test Cases

1. **Get Test Cases**
   ```
   GET /api/testcases/<story_id>
   ```
   Returns all test cases associated with a specific story.

2. **Download Test Cases**
   ```
   GET /api/testcases/<story_id>/download
   ```
   Downloads test cases for a story as an Excel file.

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   POSTGRES_DB=your_db_name
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_password
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```
4. Run the application:
   ```bash
   python run.py
   ```

## Dependencies

- Flask 3.0.2
- Flask-CORS 4.0.0
- python-dotenv 1.0.1
- psycopg2-binary 2.9.9
- lancedb 0.4.3
- pandas 2.2.1
- openpyxl 3.1.2

## Project Structure

```
fe-api/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── routes/
│   │   ├── stories.py
│   │   └── testcases.py
│   ├── services/
│   │   └── db_service.py
│   └── utils/
│       └── excel_util.py
├── requirements.txt
├── run.py
└── README.md
```

## Database Schema

### User Stories Table
```sql
CREATE TABLE user_stories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Test Cases Table
```sql
CREATE TABLE test_cases_generated (
    id SERIAL PRIMARY KEY,
    story_id INTEGER REFERENCES user_stories(id),
    test_cases JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Response Formats

### Success Response
```json
{
    "id": "integer",
    "title": "string",
    "description": "string",
    "created_at": "ISO timestamp"
}
```

### Error Response
```json
{
    "error": "error message"
}
```

## Error Codes

- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 






fe-api/
├── app/
│   ├── __init__.py          # App initialization
│   ├── config.py            # Configuration
│   ├── routes/
│   │   ├── stories.py       # Story viewing endpoints
│   │   └── testcases.py     # Test case viewing endpoints
│   ├── services/
│   │   └── db_service.py    # Database operations
│   └── utils/
│       └── excel_util.py    # Excel export functionality
├── requirements.txt         # Dependencies
├── run.py                  # App entry point
├── README.md              # Documentation
└── .gitignore             # Git ignore file