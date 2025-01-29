from instaloader import Instaloader
import time

L = Instaloader()

# Configure mobile user agent
L.context._session.headers.update({
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1'
})

try:
    L.login("aayeri.ai", "Wachas WP")
except Exception as e:
    if "Checkpoint required" in str(e):
        print(f"\n⚠️ Complete verification first! Visit: https://instagram.com{str(e).split()[-3]}")
        input("Press ENTER after completing verification in browser...")
        time.sleep(5)
        L.load_session_from_file("aayeri.ai")
    else:
        raise

# Save session for future use
L.save_session_to_file()