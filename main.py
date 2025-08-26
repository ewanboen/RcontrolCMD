import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

AUTH_KEY = os.getenv("AUTH_KEY", "default_key")

# Store latest command per client
latest_commands = {}  # {client_id: command}

class CommandHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override default logging to use logging module
        logging.info("%s - %s" % (self.client_address[0], format % args))

    def do_GET(self):
        client_id = self.headers.get("Client-ID", "unknown")

        if self.path == "/command":
            client_key = self.headers.get("Authorization", "")
            if client_key != f"Bearer {AUTH_KEY}":
                self.send_response(403)
                self.end_headers()
                logging.warning(f"Unauthorized GET attempt from {self.client_address[0]}")
                return

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            # Get command for this client
            command = latest_commands.get(client_id, "")
            self.wfile.write(json.dumps({"command": command}).encode())
            logging.info(f"[{client_id}] Command sent: {command}")

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        client_id = self.headers.get("Client-ID", "unknown")

        if self.path == "/command":
            client_key = self.headers.get("Authorization", "")
            if client_key != f"Bearer {AUTH_KEY}":
                self.send_response(403)
                self.end_headers()
                logging.warning(f"Unauthorized POST attempt from {self.client_address[0]}")
                return

            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)

                # Log output from receiver
                output = data.get("output", "")
                if output:
                    logging.info(f"[{client_id}] Output: {output}")

                # Clear the command after it was sent
                latest_commands[client_id] = ""

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Command received")

            except Exception as e:
                self.send_response(400)
                self.end_headers()
                logging.error(f"[{client_id}] Error processing POST: {e}")
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=CommandHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Server started on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    PORT = int(os.getenv("PORT", 8000))
    run(port=PORT)
