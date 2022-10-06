from dataclasses import dataclass, field


@dataclass
class HTTPResponse:
    response_code: int
    headers: dict = field(default_factory=dict)


@dataclass
class FileHTTPResponse:
    response_code: int
    path: str
    mimetype: str = None
    headers: dict = field(default_factory=dict)


@dataclass
class RawBytesHTTPResponse:
    response_code: int
    raw: bytes
    headers: dict = field(default_factory=dict)


@dataclass()
class RedirectHTTPResponse:
    location: str
