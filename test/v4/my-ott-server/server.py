import http.server
import socketserver
import os

PORT = 8000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")

os.chdir(WEB_DIR)

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:

    print("MY OTT SERVER START")
    print("http://localhost:8000")

    httpd.serve_forever()