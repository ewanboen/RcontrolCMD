import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

latest_command = ""
AUTH_KEY = os.getenv("AUTH_KEY", "default_key")

class CommandHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/command":
            client_key = self.headers.get("Authorization", "")
            if client_key != f"Bearer {AUTH_KEY}":
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Unauthorized")
                return

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"command": latest_command}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/command":
            client_key = self.headers.get("Authorization", "")
            if client_key != f"Bearer {AUTH_KEY}":
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Unauthorized")
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                global latest_command
                latest_command = data.get("command", "")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Command stored")
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()
