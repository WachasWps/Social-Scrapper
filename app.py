from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import instaloader
import logging
import time
import random
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

# Get credentials from environment variables
INSTAGRAM_USER = os.getenv("INSTAGRAM_USER")
INSTAGRAM_PASS = os.getenv("INSTAGRAM_PASS")

class CustomInstaloader(instaloader.Instaloader):
    def __init__(self):
        super().__init__()
        self.context._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.request_timeout = 30
        self.context.sleep = True
        self.context.max_connection_attempts = 3

loader = CustomInstaloader()

def login_to_instagram():
    try:
        if not INSTAGRAM_USER or not INSTAGRAM_PASS:
            raise ValueError("Instagram credentials not set in environment variables")
            
        loader.load_session_from_file(INSTAGRAM_USER)
        if not loader.context.is_logged_in:
            loader.login(INSTAGRAM_USER, INSTAGRAM_PASS)
            loader.save_session_to_file()
    except FileNotFoundError:
        loader.login(INSTAGRAM_USER, INSTAGRAM_PASS)
        loader.save_session_to_file()

login_to_instagram()

def scrape_instagram_profile(username):
    try:
        time.sleep(random.uniform(1, 3))
        profile = instaloader.Profile.from_username(loader.context, username)
        
        # Your data collection logic here
        data = {
            "Username": profile.username,
            "Followers": profile.followers,
            "Following": profile.followees,
            "Posts": profile.mediacount
        }
        
        return {"status": "success", "data": data}

    except instaloader.exceptions.QueryReturnedBadRequestException as e:
        logger.error(f"Rate limited: {e}")
        time.sleep(60)
        return scrape_instagram_profile(username)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scrape/{username}")
async def scrape(username: str):
    return scrape_instagram_profile(username)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)