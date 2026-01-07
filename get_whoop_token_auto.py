#!/usr/bin/env python3
"""
Whoop OAuth Token Getter with Automatic Callback
This script automatically handles the OAuth callback
"""

import requests
import webbrowser
import secrets
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Your Whoop App Credentials
CLIENT_ID = 'b3e7f107-34b0-412f-83c3-b542c871d618'
CLIENT_SECRET = '314450a6e83b283cfc5df2402f6296ad01988671b082baa4f8db1e1685299a32'
REDIRECT_URI = 'http://localhost:8000/callback'

# Whoop OAuth endpoints
AUTH_URL = 'https://api.prod.whoop.com/oauth/oauth2/auth'
TOKEN_URL = 'https://api.prod.whoop.com/oauth/oauth2/token'

# Global variable to store authorization code
authorization_code = None
server_running = True

class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback"""

    def log_message(self, format, *args):
        # Enable logging for debugging
        print(f"[SERVER] {format % args}")

    def do_GET(self):
        global authorization_code, server_running

        print(f"[DEBUG] Received request: {self.path}")

        # Parse query parameters
        query = urlparse(self.path).query
        params = parse_qs(query)

        print(f"[DEBUG] Query params: {params}")

        if 'code' in params:
            authorization_code = params['code'][0]
            print(f"[DEBUG] Authorization code captured: {authorization_code[:20]}...")

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            success_html = """
            <!DOCTYPE html>
            <html>
            <head><title>Success</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: green;">✅ Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())

            # Signal to stop server
            server_running = False
        else:
            # Send error response
            print(f"[DEBUG] No code in params - authorization failed")
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Error</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: red;">❌ Authorization Failed</h1>
                <p>No authorization code received.</p>
                <p style="font-size: 12px; color: gray;">Path: {self.path}</p>
                <p style="font-size: 12px; color: gray;">Params: {params}</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())


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
    return url

def exchange_code_for_tokens(auth_code):
    """Exchange authorization code for access_token and refresh_token"""
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
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

def run_callback_server():
    """Run a temporary HTTP server to catch the OAuth callback"""
    global server_running

    server = HTTPServer(('localhost', 8000), CallbackHandler)

    while server_running:
        server.handle_request()

    server.server_close()

def main():
    global authorization_code

    print("🏃 Whoop OAuth Token Getter")
    print("=" * 50)
    print()

    # Start callback server in background
    print("🌐 Starting local callback server on port 8000...")
    server_thread = threading.Thread(target=run_callback_server, daemon=True)
    server_thread.start()
    print("✅ Server ready")
    print()

    # Get authorization URL
    auth_url = get_authorization_url()
    print("📱 Opening browser for Whoop authorization...")
    print()
    print("If browser doesn't open, copy this URL:")
    print(auth_url)
    print()

    # Open browser
    webbrowser.open(auth_url)

    print("⏳ Waiting for authorization...")
    print("   (Authorize the app in your browser)")
    print()

    # Wait for authorization code
    server_thread.join(timeout=120)  # Wait up to 2 minutes

    if not authorization_code:
        print("❌ Timeout or authorization failed")
        return

    print("✅ Authorization code received!")
    print()

    # Exchange code for tokens
    print("🔄 Exchanging code for tokens...")
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
        print("📝 Copy these values - I'll update your webhook_server.py next!")
        print()
    else:
        print("❌ Failed to get tokens")

if __name__ == '__main__':
    main()
