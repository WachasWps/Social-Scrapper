from fastapi import FastAPI, HTTPException
import instaloader
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define session file path
SESSION_FILE = Path(__file__).parent / "session-aayeri.ai"

# Validate session file
if not SESSION_FILE.exists():
    logger.error(f"Session file not found at {SESSION_FILE}")
    raise FileNotFoundError("Session file is missing")

app = FastAPI()
loader = instaloader.Instaloader()

def load_instagram_session():
    try:
        loader.load_session_from_file("aayeri.ai", filename=str(SESSION_FILE))
        
        if not loader.context.is_logged_in:
            raise ValueError("Session expired or invalid")
            
    except Exception as e:
        logger.error(f"Session loading failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize Instagram session: {str(e)}"
        )

# Initialize session
load_instagram_session()

@app.get("/scrape/{username}")
def scrape(username: str):
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        return {
            "username": profile.username,
            "followers": profile.followers,
            "posts": profile.mediacount
        }
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/debug/session")
def debug_session():
    return {
        "session_file_path": str(SESSION_FILE),
        "session_exists": SESSION_FILE.exists(),
        "file_size": SESSION_FILE.stat().st_size if SESSION_FILE.exists() else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)