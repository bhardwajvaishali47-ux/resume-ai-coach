import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_google_auth_url() -> str:
    """
    Generates the Google OAuth authorization URL.
    User is redirected to this URL to login with Google.
    
    The URL contains:
    - client_id: identifies your app to Google
    - redirect_uri: where Google sends the user after login
    - scope: what information we want (email and profile)
    - response_type: we want an authorization code
    """
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account"
    }

    param_string = "&".join(
        f"{key}={value}" for key, value in params.items()
    )
    return f"{GOOGLE_AUTH_URL}?{param_string}"


async def exchange_code_for_token(code: str) -> dict:
    """
    Exchanges the authorization code for user information.
    
    After user logs in with Google:
    1. Google sends a code to our redirect URI
    2. We exchange that code for an access token
    3. We use the access token to get user's email and name
    
    Input:  authorization code from Google
    Output: dict with email, name, google_id, picture
    """
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        userinfo = userinfo_response.json()

        return {
            "email": userinfo.get("email"),
            "full_name": userinfo.get("name"),
            "google_id": userinfo.get("id"),
            "profile_picture": userinfo.get("picture")
        }