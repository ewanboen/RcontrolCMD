import os
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

# === Setup logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

latest_command = ""
AUTH_KEY = os.getenv("AUTH_KEY", "default_key")


class CommandHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override default logging to use Python logging"""
        logging.info("%s - %s" % (self.address_string(), format % args))

    def do_GET(self):
        if self.path == "/command":
            client_key = self.headers.get("Authorization", "")
            if client_key != f"Bearer {AUTH_KEY}":
                logging.warning("Unauthorized GET attempt")
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Unauthorized")
                return

            logging.info("Command requested -> %s", latest_command)
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
                logging.warning("Unauthorized POST attempt")
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Unauthorized")
                return

            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)

                global latest_command
                latest_command = data.get("command", "")

                logging.info("New command stored -> %s", latest_command)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Command stored")
            except Exception as e:
                logging.error("Error in POST /command: %s", e)
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))  # Render provides PORT env var
    server = HTTPServer(("0.0.0.0", port), CommandHandler)
    logging.info("Server started on port %s", port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error("Server crashed: %s", e)
    finally:
        server.server_close()
        logging.info("Server stopped")
