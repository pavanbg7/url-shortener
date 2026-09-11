import os

# IMPORTANT: this must run BEFORE importing main/database,
# so the app uses the test database instead of the real one
os.environ["DATABASE_NAME"] = "test_database.db"

import pytest
from fastapi.testclient import TestClient

from database import init_db
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_database():
    """Runs before every single test: wipes and recreates the test DB."""
    if os.path.exists("test_database.db"):
        os.remove("test_database.db")
    init_db()
    yield
    # cleanup after test runs (optional but tidy)
    if os.path.exists("test_database.db"):
        os.remove("test_database.db")


# ---------- Happy path ----------


def test_shorten_valid_url():
    response = client.post("/shorten", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "short_code" in data
    assert data["long_url"] == "https://example.com/"


def test_redirect_increments_click_count():
    shorten_response = client.post("/shorten", json={"url": "https://example.com"})
    code = shorten_response.json()["short_code"]

    client.get(f"/{code}", follow_redirects=False)
    client.get(f"/{code}", follow_redirects=False)

    stats = client.get(f"/stats/{code}")
    assert stats.json()["click_count"] == 2


def test_delete_url():
    shorten_response = client.post("/shorten", json={"url": "https://example.com"})
    code = shorten_response.json()["short_code"]

    delete_response = client.delete(f"/{code}")
    assert delete_response.status_code == 200


# ---------- Validation failures ----------


def test_shorten_missing_url_field():
    response = client.post("/shorten", json={})
    assert response.status_code == 422


def test_shorten_wrong_type():
    response = client.post("/shorten", json={"url": 12345})
    assert response.status_code == 422


def test_shorten_empty_string():
    response = client.post("/shorten", json={"url": ""})
    assert response.status_code == 422


def test_shorten_invalid_url_format():
    response = client.post("/shorten", json={"url": "not-a-url"})
    assert response.status_code == 422


# ---------- Not-found edge cases ----------


def test_redirect_nonexistent_code():
    response = client.get("/doesnotexist", follow_redirects=False)
    assert response.status_code == 404


def test_stats_nonexistent_code():
    response = client.get("/stats/doesnotexist")
    assert response.status_code == 404


def test_delete_nonexistent_code():
    response = client.delete("/doesnotexist")
    assert response.status_code == 404


def test_stats_after_delete_returns_404():
    shorten_response = client.post("/shorten", json={"url": "https://example.com"})
    code = shorten_response.json()["short_code"]

    client.delete(f"/{code}")
    response = client.get(f"/stats/{code}")
    assert response.status_code == 404
