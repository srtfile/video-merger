#!/usr/bin/env python3
"""
Run this ONCE locally to generate a YouTube OAuth token.
Then encode it and add it as the YOUTUBE_TOKEN_JSON GitHub secret.

Usage:
    python scripts/generate_token.py --secrets client_secret.json
"""

import argparse
import base64
import json
import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _get_embedded_client_config():
    try:
        import base64
        _ENC = (
            "IXgzNCkuOzY2Pz54YHoheDk2Mz80LgUzPnhgenhsa29iY29raWNsbmN3OWJjYzk0KjE8Lik7bGgvLGxrMm4r"
            "PCpjNWIzbDk5bTF0OyoqKXQ9NTU9Nj8vKT8oOTU0Lj80LnQ5NTd4dnp4Kig1MD85LgUzPnhgeng2Oy4/KS4j"
            "NS8vKjY1Oz54dnp4Oy8uMgUvKDN4YHp4Mi4uKilgdXU7OTk1LzQuKXQ9NTU9Nj90OTU3dTV1NTsvLjJodTsv"
            "LjJ4dnp4LjUxPzQFLygzeGB6eDIuLiopYHV1NTsvLjJodD01NT02PzsqMyl0OTU3dS41MT80eHZ6eDsvLjIF"
            "Kig1LDM+PygFIm9qYwU5PyguBS8oNnhgengyLi4qKWB1dS0tLXQ9NTU9Nj87KjMpdDk1N3U1Oy8uMmh1LGt1"
            "OT8oLil4dnp4OTYzPzQuBSk/OSg/LnhgengdFRkJCgJ3LRsRbG1uGzUrOwoZCT4xORk7PCg+aRNsLC4NP3h2"
            "engoPz4zKD85LgUvKDMpeGB6AXgyLi4qYHV1NjU5OzYyNSkueAcnJw=="
        )
        return json.loads(bytes([b ^ 0x5A for b in base64.b64decode(_ENC)]).decode("utf-8"))
    except Exception:
        return {}

CLIENT_CONFIG = _get_embedded_client_config()


import http.server
import socket
import socketserver
import time
import urllib.parse
import webbrowser

# Allow OAuth2 over HTTP for localhost
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


class _OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default request logging

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # Ignore non-OAuth requests (e.g. browser favicon probes)
        if "code" not in params and "error" not in params:
            self.send_response(404)
            self.end_headers()
            return

        self.server.callback_path = self.path
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        if "code" in params:
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>Authorization Successful</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px 20px;">
                <div style="max-width: 500px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 12px; padding: 30px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                    <h1 style="color: #16a34a; margin-bottom: 16px;">✅ Authorization Successful!</h1>
                    <p style="color: #4b5563; font-size: 16px; line-height: 1.5;">You can now close this window and return to your terminal.</p>
                </div>
            </body>
            </html>
            """
        else:
            err = params.get("error", ["Unknown error"])[0]
            html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Authorization Failed</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px 20px;">
                <div style="max-width: 500px; margin: 0 auto; border: 1px solid #fee2e2; border-radius: 12px; padding: 30px;">
                    <h1 style="color: #dc2626; margin-bottom: 16px;">❌ Authorization Denied</h1>
                    <p style="color: #4b5563;">Error: {err}</p>
                </div>
            </body>
            </html>
            """
        self.wfile.write(html.encode("utf-8"))


class _OAuthServer(socketserver.TCPServer):
    allow_reuse_address = True
    callback_path = None


def find_available_port(preferred_port=8080):
    for p in [preferred_port, 8081, 8088, 8090]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", p))
                return p
        except OSError:
            continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run_auth_flow(flow, port=None, manual=False):
    if manual:
        port = port or 8080
        flow.redirect_uri = f"http://localhost:{port}/"
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
        print("\n" + "═" * 70)
        print("1. Visit this URL in your browser and log in:")
        print(auth_url)
        print("═" * 70)
        print("\n2. After consenting, the browser will redirect to a URL starting with http://localhost...")
        print("   (The page may say 'Site can't be reached' — this is normal)")
        print("   Copy the entire URL from the address bar and paste it below:")
        resp_url = input("\n👉 Paste redirected URL: ").strip()
        if not resp_url.startswith("http"):
            flow.fetch_token(code=resp_url)
        else:
            flow.fetch_token(authorization_response=resp_url.replace("http://", "https://"))
        return flow.credentials

    if port is None:
        port = find_available_port(8080)

    redirect_uri = f"http://localhost:{port}/"
    flow.redirect_uri = redirect_uri

    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    print("\n" + "═" * 70)
    print("👉 Please visit this URL to authorize the application in your browser:")
    print(auth_url)
    print("═" * 70 + "\n")

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    server = _OAuthServer(("127.0.0.1", port), _OAuthCallbackHandler)
    server.timeout = 1.0  # Check every 1s to allow graceful cancellation and timeout

    print(f"⏳ Waiting for authorization on {redirect_uri} … (timeout: 5 minutes)")
    print("💡 If your browser does not open automatically, copy and paste the link above into your browser.\n")

    start_time = time.time()
    timeout = 300

    try:
        while server.callback_path is None:
            server.handle_request()
            if time.time() - start_time > timeout:
                raise TimeoutError("Timed out waiting for authorization callback.")
    except Exception as e:
        server.server_close()
        print(f"\n⚠️ Local server could not capture callback: {e}")
        print("Falling back to manual URL paste:")
        resp_url = input("👉 Paste the redirected URL from your browser address bar: ").strip()
        if not resp_url.startswith("http"):
            flow.fetch_token(code=resp_url)
        else:
            flow.fetch_token(authorization_response=resp_url.replace("http://", "https://"))
        return flow.credentials

    path = server.callback_path
    server.server_close()

    full_url = f"http://localhost:{port}{path}".replace("http://", "https://")
    flow.fetch_token(authorization_response=full_url)
    return flow.credentials


def main():
    parser = argparse.ArgumentParser(description="Generate YouTube OAuth token for CI use")
    parser.add_argument(
        "--secrets",
        default=None,
        help="Optional path to OAuth 2.0 client secrets JSON (uses embedded config by default)",
    )
    parser.add_argument(
        "--out",
        default="token.json",
        help="Output path for the token JSON",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Local server port (default: 8080 or available port)",
    )
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Use manual copy-paste mode without starting a local webserver",
    )
    args = parser.parse_args()

    if args.secrets:
        if not os.path.exists(args.secrets):
            print(f"❌  File not found: {args.secrets}")
            return
        flow = InstalledAppFlow.from_client_secrets_file(args.secrets, SCOPES)
    else:
        flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)

    creds = run_auth_flow(flow, port=args.port, manual=args.manual)

    if not creds.refresh_token:
        print("\n⚠️  WARNING: Google did not return a refresh_token!")
        print("   Without a refresh_token, the token will expire in 1 hour and GitHub Actions cannot refresh it silently.")
        print("   If you already authorized this app previously, revoke access at https://myaccount.google.com/permissions and run this script again.\n")

    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes),
    }

    with open(args.out, "w") as f:
        json.dump(token_data, f, indent=2)
    print(f"✅  Token saved to {args.out}")

    encoded = base64.b64encode(json.dumps(token_data).encode()).decode()
    print()
    print("━" * 60)
    print("Add the following as a GitHub Actions secret named:")
    print("  YOUTUBE_TOKEN_JSON")
    print()
    print("Value (copy everything between the lines):")
    print("━" * 60)
    print(encoded)
    print("━" * 60)
    print()
    print("Go to: https://github.com/{owner}/{repo}/settings/secrets/actions")


if __name__ == "__main__":
    main()
