"""Serve only the generated email review page on loopback."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def handler_for(directory):
    root = Path(directory).resolve()
    class Handler(BaseHTTPRequestHandler):
        # Browsers may preconnect without sending a request. Bound each wait.
        timeout = 5

        def do_GET(self):
            name = {'/': 'index.html', '/index.html': 'index.html'}.get(self.path.split('?', 1)[0])
            target = root / name if name else None
            if target is None or any(p.is_symlink() for p in (target, target.parent)) or not target.is_file() or root not in target.resolve().parents:
                self.send_error(404)
                return
            body = target.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *_):
            pass
    return Handler


def create_server(directory, port):
    return ThreadingHTTPServer(('127.0.0.1', port), handler_for(directory))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', default='local/email-demo/review')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    server = create_server(args.directory, args.port)
    print(f'Read-only review: http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
