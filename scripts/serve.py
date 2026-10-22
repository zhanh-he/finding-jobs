"""Loopback-only preview. Serve exactly one separated directory; never the repo root."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import argparse,functools
ap=argparse.ArgumentParser();ap.add_argument('--view',choices=['private','public-safe'],default='private');ap.add_argument('--port',type=int,default=8765);a=ap.parse_args()
root=Path(__file__).resolve().parents[1]/a.view
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def list_directory(self,path):self.send_error(403,'Directory listing disabled');return None
 def end_headers(self):
  self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'");super().end_headers()
handler=functools.partial(Handler,directory=str(root))
server=ThreadingHTTPServer(('127.0.0.1',a.port),handler)
print(f'Local {a.view} preview: http://127.0.0.1:{a.port}/',flush=True)
try:server.serve_forever()
except KeyboardInterrupt:server.server_close()
