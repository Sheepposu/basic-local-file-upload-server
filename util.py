from response import RawBytesHTTPResponse
import os
import re


def handle_file_download(request, download_path, success_return):
    content_type, boundary = request.headers["Content-Type"].split(";")
    boundary = boundary.split("=")[1].encode()
    content_length = int(request.headers['Content-Length'])
    line = request.rfile.readline()
    content_length -= len(line)
    if boundary not in line:
        return RawBytesHTTPResponse(400, b"boundary did not match first line of file",
                                    headers={"Content-Type": "text/html"})
    line = request.rfile.readline()
    content_length -= len(line)
    fn = re.findall(r'Content-Disposition.*name="filename"; filename="(.*)"', line.decode())
    if not fn:
        return RawBytesHTTPResponse(400, b"cannot find out file name",
                                    headers={"Content-Type": "text/html"})
    fn = os.path.join(download_path, fn[0])
    for _ in range(2):
        line = request.rfile.readline()
        content_length -= len(line)
    with open(fn, "wb") as out:
        preline = request.rfile.readline()
        content_length -= len(preline)
        while content_length > 0:
            line = request.rfile.readline()
            content_length -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                return success_return
            else:
                out.write(preline)
                preline = line
    return RawBytesHTTPResponse(400, b"unexpected end of data",
                                headers={"Content-Type": "text/html"})
