from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import instaloader
import logging

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing; restrict in production
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers to the client
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def scrape_instagram_profile(username):
    L = instaloader.Instaloader()
    try:
        # Scrape Instagram profile data
        profile = instaloader.Profile.from_username(L.context, username)

        # Collect profile data
        data = {
            "Username": profile.username,
            "Full Name": profile.full_name,
            "Bio": profile.biography,
            "Followers": profile.followers,
            "Following": profile.followees,
            "Profile Pic URL": profile.profile_pic_url,
            "Posts Count": profile.mediacount,
            "Is Private": profile.is_private,
            "Is Verified": profile.is_verified,
            "External URL": profile.external_url if profile.external_url else "None",
        }

        # Collect recent posts
        posts = []
        for post in profile.get_posts():
            if len(posts) >= 5:  # Limit to the latest 5 posts
                break
            posts.append({
                "Caption": post.caption[:100] if post.caption else "No Caption",
                "Likes": post.likes,
                "Comments": post.comments,
                "Post URL": post.url,
                "Hashtags": list(post.caption_hashtags) if post.caption_hashtags else [],
                "Mentions": list(post.caption_mentions) if post.caption_mentions else [],
                "Post Date": post.date.strftime('%Y-%m-%d'),
                "Is Video": post.is_video,
                "Video Views": post.video_view_count if post.is_video else "N/A",
            })

        # Add engagement rate
        total_likes = sum(post["Likes"] for post in posts)
        total_comments = sum(post["Comments"] for post in posts)
        engagement_rate = round(((total_likes + total_comments) / profile.followers) * 100, 2)

        data["Engagement Rate (%)"] = engagement_rate
        data["Recent Posts"] = posts

        return {"status": "success", "data": data}

    except instaloader.exceptions.ProfileNotExistsException as e:
        logger.error(f"Profile {username} does not exist or is private: {e}")
        raise HTTPException(status_code=404, detail="Profile does not exist or is private")
    except Exception as e:
        logger.error(f"An error occurred while scraping {username}: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Define the endpoint
@app.get("/scrape/{username}")
async def scrape(username: str):
    return scrape_instagram_profile(username)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)