from server import create_server, Handler
from response import FileHTTPResponse, RedirectHTTPResponse
from util import handle_file_download


host = '0.0.0.0'
port = 8727

print("Creating server...")
server = create_server(host, port)


@server.route("/")
def index(request: Handler):
    return FileHTTPResponse(200, "html/index.html")


@server.route("/upload", "POST")
def download(request: Handler):
    return handle_file_download(request, "downloads", RedirectHTTPResponse("/"))


print("Server is up and running!")
server.serve_forever()
