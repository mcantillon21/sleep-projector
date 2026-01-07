#!/usr/bin/env python3
"""
Whoop OAuth Token Getter
This script helps you get fresh access_token and refresh_token from Whoop
"""

import requests
import webbrowser
import secrets
from urllib.parse import urlencode, urlparse, parse_qs

# Your Whoop App Credentials
CLIENT_ID = 'b3e7f107-34b0-412f-83c3-b542c871d618'
CLIENT_SECRET = '314450a6e83b283cfc5df2402f6296ad01988671b082baa4f8db1e1685299a32'
REDIRECT_URI = 'http://localhost:8000/callback'  # Must match Whoop OAuth app settings

# Whoop OAuth endpoints
AUTH_URL = 'https://api.prod.whoop.com/oauth/oauth2/auth'
TOKEN_URL = 'https://api.prod.whoop.com/oauth/oauth2/token'

def get_authorization_url():
    """Generate the authorization URL"""
    # Generate a random state parameter for CSRF protection (min 8 characters)
    state = secrets.token_urlsafe(16)

    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'read:recovery read:sleep read:workout read:cycles read:body_measurement offline',
        'state': state,
    }
    url = f"{AUTH_URL}?{urlencode(params)}"
    return url, state

def exchange_code_for_tokens(authorization_code):
    """Exchange authorization code for access_token and refresh_token"""
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(TOKEN_URL, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🏃 Whoop OAuth Token Getter")
    print("=" * 50)
    print()

    # Step 1: Get authorization URL
    auth_url, state = get_authorization_url()
    print("📱 Step 1: Authorize the app")
    print("Opening browser to Whoop authorization page...")
    print()
    print("If browser doesn't open, copy this URL:")
    print(auth_url)
    print()

    # Open browser
    webbrowser.open(auth_url)

    # Step 2: Get authorization code from user
    print("=" * 50)
    print("📋 Step 2: Get authorization code")
    print()
    print("After authorizing, you'll be redirected to:")
    print(f"{REDIRECT_URI}?code=AUTHORIZATION_CODE")
    print()
    print("You can paste either:")
    print("  - Just the code value, OR")
    print("  - The entire callback URL")
    print()

    user_input = input("Paste here: ").strip()

    if not user_input:
        print("❌ No input provided. Exiting.")
        return

    # Try to parse as URL first, otherwise treat as raw code
    authorization_code = user_input
    if user_input.startswith('http'):
        try:
            parsed_url = urlparse(user_input)
            params = parse_qs(parsed_url.query)
            if 'code' in params:
                authorization_code = params['code'][0]
                print(f"✓ Extracted code from URL")
            else:
                print("❌ No 'code' parameter found in URL. Exiting.")
                return
        except Exception as e:
            print(f"❌ Error parsing URL: {e}")
            return

    # Step 3: Exchange code for tokens
    print()
    print("🔄 Step 3: Exchanging code for tokens...")
    tokens = exchange_code_for_tokens(authorization_code)

    if tokens:
        print()
        print("✅ Success! Here are your tokens:")
        print("=" * 50)
        print()
        print("ACCESS_TOKEN:")
        print(tokens.get('access_token'))
        print()
        print("REFRESH_TOKEN:")
        print(tokens.get('refresh_token'))
        print()
        print("EXPIRES_IN:", tokens.get('expires_in'), "seconds")
        print()
        print("=" * 50)
        print()
        print("💾 Now update webhook_server.py with these values:")
        print(f"   ACCESS_TOKEN = '{tokens.get('access_token')}'")
        print(f"   REFRESH_TOKEN = '{tokens.get('refresh_token')}'")
        print()
    else:
        print("❌ Failed to get tokens")

if __name__ == '__main__':
    main()
