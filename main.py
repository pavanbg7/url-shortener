import random
import string
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from database import init_db, get_connection
from models import ShortenRequest, ShortenResponse, StatsResponse, DeleteResponse

app = FastAPI(title="URL Shortener API")


def generate_code(length: int = 5) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(payload: ShortenRequest):
    long_url = str(payload.url)

    conn = get_connection()
    cur = conn.cursor()

    # try generating a unique code, retry on the rare collision
    code = generate_code()
    while True:
        cur.execute("SELECT 1 FROM urls WHERE short_code = ?", (code,))
        if cur.fetchone() is None:
            break
        code = generate_code()

    cur.execute(
        "INSERT INTO urls (long_url, short_code) VALUES (?, ?)", (long_url, code)
    )
    conn.commit()
    conn.close()

    return ShortenResponse(
        short_code=code, short_url=f"http://127.0.0.1:8000/{code}", long_url=long_url
    )


@app.get("/stats/{code}", response_model=StatsResponse)
def get_stats(code: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM urls WHERE short_code = ?", (code,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Short code not found")

    return StatsResponse(
        short_code=row["short_code"],
        long_url=row["long_url"],
        created_at=row["created_at"],
        click_count=row["click_count"],
    )


@app.delete("/{code}", response_model=DeleteResponse)
def delete_url(code: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM urls WHERE short_code = ?", (code,))
    row = cur.fetchone()

    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Short code not found")

    cur.execute("DELETE FROM urls WHERE short_code = ?", (code,))
    conn.commit()
    conn.close()

    return DeleteResponse(detail=f"Short code '{code}' deleted")


@app.get("/{code}")
def redirect_to_long_url(code: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT long_url FROM urls WHERE short_code = ?", (code,))
    row = cur.fetchone()

    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Short code not found")

    cur.execute(
        "UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?", (code,)
    )
    conn.commit()
    conn.close()

    return RedirectResponse(url=row["long_url"])
