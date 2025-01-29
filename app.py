from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import instaloader
import logging
import time
import random

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instagram credentials (use environment variables in production)
INSTAGRAM_USER = "aayeri.ai"
INSTAGRAM_PASS = "Wachas WP"

# Configure Instaloader with proper headers and delays
class CustomInstaloader(instaloader.Instaloader):
    def __init__(self):
        super().__init__()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        })
        self.request_timeout = 25
        self._context._sleep = True
        self._context._max_connection_attempts = 3

# Global loader instance with session persistence
loader = CustomInstaloader()

def login_to_instagram():
    try:
        loader.load_session_from_file(INSTAGRAM_USER)
    except FileNotFoundError:
        loader.login(INSTAGRAM_USER, INSTAGRAM_PASS)
        loader.save_session_to_file()

# Perform initial login
login_to_instagram()

def scrape_instagram_profile(username):
    try:
        # Random delay to avoid detection
        time.sleep(random.uniform(1, 3))
        
        profile = instaloader.Profile.from_username(loader.context, username)
        
        # Implement rate limiting handling
        if loader.context.is_logged_in and loader.context.last_response_ts:
            current_time = time.time()
            time_since_last = current_time - loader.context.last_response_ts
            if time_since_last < 2.0:  # Maintain 2s between requests
                time.sleep(2.0 - time_since_last)

        # Your existing data collection logic here
        data = {
            "Username": profile.username,
            "Followers": profile.followers,
            # ... rest of your data collection
        }
        
        return {"status": "success", "data": data}

    except instaloader.exceptions.QueryReturnedBadRequestException as e:
        logger.error(f"Rate limited: {e}")
        # Implement rotating proxy or wait longer
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