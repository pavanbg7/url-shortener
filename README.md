# URL Shortener API

A REST API built with FastAPI that converts long URLs into short, shareable codes — with click tracking, stats, and full test coverage.

> This project was originally built with Flask as a simple HTML-form app. It has since been rewritten as a proper JSON REST API using FastAPI, with typed validation, structured error handling, and an automated test suite. See commit history for the full progression.

## Features

- Shorten any valid URL into a short code
- Redirect from short code to original URL
- Track click counts per short code
- View stats (creation time, click count) for any short code
- Delete short codes
- Automatic input validation — invalid URLs are rejected before they reach the database
- Interactive API documentation (Swagger UI) generated automatically
- Full test suite covering both success and failure cases

## Tech Stack

- **FastAPI** — web framework
- **Pydantic** — request/response validation and typing
- **SQLite** — database
- **Uvicorn** — ASGI server
- **Pytest** — testing

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/pavanbg7/url-shortener.git
cd url-shortener
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the server**
```bash
uvicorn main:app --reload
```

The API will be running at `http://127.0.0.1:8000`

## Usage

### Interactive Docs
Once the server is running, open `http://127.0.0.1:8000/docs` for a full interactive interface to test every endpoint directly in your browser.

### Endpoints

**Shorten a URL**
```
POST /shorten
Content-Type: application/json

{
  "url": "https://example.com"
}
```
Response:
```json
{
  "short_code": "h7j8m",
  "short_url": "http://127.0.0.1:8000/h7j8m",
  "long_url": "https://example.com/"
}
```

**Visit a short URL (redirects to original)**
```
GET /{code}
```

**Get stats for a short code**
```
GET /stats/{code}
```
Response:
```json
{
  "short_code": "h7j8m",
  "long_url": "https://example.com/",
  "created_at": "2026-08-29 12:27:17",
  "click_count": 2
}
```

**Delete a short code**
```
DELETE /{code}
```
**Root**
```
GET /
Returns a simple message pointing to `/docs` — useful as a quick health check or entry point.
```

### Error Handling

| Scenario | Response |
|---|---|
| Invalid or missing URL in request | `422 Unprocessable Entity` with details on what failed |
| Requesting a short code that doesn't exist | `404 Not Found` |
| Deleting a short code that doesn't exist | `404 Not Found` |

## Running Tests

```bash
pytest -v
```

Tests run against a separate `test_database.db`, so your real data is never touched. The suite covers:
- Successful shortening, redirecting, and click tracking
- Validation failures (missing fields, wrong types, invalid URLs)
- Not-found cases across all endpoints

## Project Structure

```
url-shortener/
├── main.py           # API routes
├── database.py        # Database connection and setup
├── models.py          # Pydantic request/response models
├── test_main.py        # Test suite
├── requirements.txt
└── README.md
```

## Live Demo

https://url-shortener-7yvj.onrender.com/