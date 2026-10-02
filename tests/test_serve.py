import io
from pathlib import Path
import tempfile
import unittest

import serve


class ServeTests(unittest.TestCase):
    def test_idle_browser_connection_does_not_block_review(self):
        import socket
        import threading
        import urllib.request
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory)/'index.html').write_text('review is ready')
            try:
                server = serve.create_server(directory, 0)
            except PermissionError:
                self.skipTest('Loopback sockets are unavailable in this sandbox.')
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            idle = None
            try:
                idle = socket.create_connection(server.server_address, timeout=1)
                with urllib.request.urlopen('http://127.0.0.1:'+str(server.server_port)+'/', timeout=1) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.read(), b'review is ready')
            finally:
                if idle is not None:
                    idle.close()
                server.shutdown(); server.server_close(); thread.join(timeout=2)

    def test_server_only_review_file_and_refuses_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'index.html').write_text('public page')
            (root/'secret.txt').write_text('secret')
            (root/'linked.html').symlink_to(root/'secret.txt')
            handler_class = serve.handler_for(root)
            for path, expected in [('/',200),('/index.html',200),('/secret.txt',404),
                                   ('/linked.html',404),('/../secret.txt',404),
                                   ('/%2e%2e/secret.txt',404),('/rubric.html',404),('/results.csv',404)]:
                handler = object.__new__(handler_class)
                handler.path = path; handler.wfile = io.BytesIO(); statuses = []
                handler.send_response = statuses.append; handler.send_error = statuses.append
                handler.send_header = lambda *args: None; handler.end_headers = lambda: None
                handler.do_GET()
                self.assertEqual(statuses, [expected])
            (root/'index.html').unlink(); (root/'index.html').symlink_to(root/'secret.txt')
            handler.path = '/'; statuses.clear(); handler.do_GET()
            self.assertEqual(statuses, [404])
