from pydantic import BaseModel, HttpUrl
from datetime import datetime

# ---- Request models (what the client sends us) ----


class ShortenRequest(BaseModel):
    url: HttpUrl  # must be a valid URL, e.g. "https://example.com" — anything else gets auto-rejected


# ---- Response models (what we send back) ----


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: str


class StatsResponse(BaseModel):
    short_code: str
    long_url: str
    created_at: str
    click_count: int


class DeleteResponse(BaseModel):
    detail: str
