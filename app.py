from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import instaloader
import logging
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use pre-authenticated session
loader = instaloader.Instaloader(
    max_connection_attempts=3,
    request_timeout=30
)

# Load session from file included in deployment
try:
    loader.load_session_from_file("aayeri.ai")
except Exception as e:
    logger.error(f"Failed to load session: {e}")
    raise HTTPException(
        status_code=500,
        detail="Failed to initialize Instagram session"
    )

def scrape_profile(username):
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        return {
            "username": profile.username,
            "followers": profile.followers,
            "following": profile.followees,
            "posts": profile.mediacount
        }
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/scrape/{username}")
async def scrape(username: str):
    return scrape_profile(username)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)