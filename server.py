from http.server import HTTPServer as BaseHTTPServer, BaseHTTPRequestHandler
from response import *
import mimetypes
import os


class InternalResponseError(Exception):
    """Raised when the function of a route doesn't return a valid response object."""


class RouteHandler:
    def __init__(self):
        self.routes = {
            "GET": {},
            "POST": {}
        }

    @staticmethod
    def parse_path_syntax(path):
        if not path.startswith("/"):
            path = "/"+path
        return path.lower()

    def add_route(self, path, method, func):
        self.routes[method][self.parse_path_syntax(path)] = func

    def get_route_func(self, path, method):
        path = path.lower()
        if path in self.routes[method]:
            return self.routes[method][path]


class Handler(BaseHTTPRequestHandler):
    def handle_path(self, method):
        route_func = self.server.routes.get_route_func(self.path, method)
        if route_func:
            response = route_func(self)
        else:
            response = HTTPResponse(404)
        self._handle_sending_response(response)

    def do_GET(self):
        file_to_serve = self.path[1:]
        if os.path.isfile(file_to_serve):
            self.send_response(200)
            self._specify_content_type(file_to_serve)
            self.end_headers()
            self._serve_file(file_to_serve)
        else:
            self.handle_path("GET")

    def do_POST(self):
        self.handle_path("POST")

    def _handle_sending_response(self, response):
        def handle_response_headers():
            for header_k, header_v in response.headers.items():
                self.send_header(header_k, header_v)

        if isinstance(response, HTTPResponse):
            self.send_response(response.response_code)
            handle_response_headers()
            self.end_headers()
        elif isinstance(response, FileHTTPResponse):
            self.send_response(response.response_code)
            handle_response_headers()
            self._specify_content_type(response.path)
            self.end_headers()
            self._serve_file(response.path)
        elif isinstance(response, RedirectHTTPResponse):
            self.send_response(301)
            self.send_header("Location", response.location)
            self.end_headers()
        elif isinstance(response, RawBytesHTTPResponse):
            self.send_response(response.response_code)
            handle_response_headers()
            self.end_headers()
            self.wfile.write(response.raw)
        else:
            raise InternalResponseError(f"Invalid response object returned for the following route: {self.path}")

    def _specify_content_type(self, path, mimetype=None):
        if mimetype is None:
            mimetype = mimetypes.guess_type(path)
        self.send_header("Content", mimetype if mimetype is not None else "text/plain")

    def _serve_file(self, path):
        with open(path, "rb") as html_file:
            self.wfile.write(html_file.read())


class HTTPServer(BaseHTTPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.routes = RouteHandler()

    def route(self, path, method="GET"):
        method = method.upper()
        def decor_func(func):
            self.routes.add_route(path, method, func)
        return decor_func


def create_server(host, port):
    server = HTTPServer((host, port), Handler)
    return server
