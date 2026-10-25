"""Sirve los assets pesados de los carteles (frames de Blender, texturas) con CORS para Remotion.
Así no pasan por --public-dir, que Remotion copia entero en cada render.

  python3 serve.py <carpeta> [puerto=8765]
"""
import functools, http.server, sys


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'max-age=3600')
        super().end_headers()

    def log_message(self, *a):
        pass


port = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(H, directory=sys.argv[1])).serve_forever()
