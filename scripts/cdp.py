"""Small standard-library CDP client for local development probes only."""

import base64
import hashlib
import json
import os
import socket
import struct
from urllib.parse import urlsplit


class CDP:
    def __init__(self, url):
        address = urlsplit(url)
        if address.scheme != "ws" or address.hostname != "127.0.0.1":
            raise ValueError("Only a local, unencrypted inspector endpoint is supported")
        self.socket = socket.create_connection((address.hostname, address.port), timeout=10)
        self.socket.settimeout(20)
        self.sequence = 0
        self.pending = b""
        key = base64.b64encode(os.urandom(16)).decode()
        request = (
            f"GET {address.path} HTTP/1.1\r\nHost: {address.netloc}\r\n"
            f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        self.socket.sendall(request.encode())
        header = b""
        while b"\r\n\r\n" not in header:
            chunk = self.socket.recv(4096)
            if not chunk:
                raise ConnectionError("Inspector closed during handshake")
            header += chunk
        header, self.pending = header.split(b"\r\n\r\n", 1)
        expected = base64.b64encode(hashlib.sha1(
            (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
        ).digest())
        if not header.startswith(b"HTTP/1.1 101 ") or expected not in header:
            self.socket.close()
            raise ConnectionError("Invalid inspector WebSocket handshake")

    def _read(self, count):
        while len(self.pending) < count:
            chunk = self.socket.recv(max(4096, count - len(self.pending)))
            if not chunk:
                raise ConnectionError("Inspector disconnected")
            self.pending += chunk
        data, self.pending = self.pending[:count], self.pending[count:]
        return data

    def _send(self, payload, opcode=1):
        mask = os.urandom(4)
        size = len(payload)
        header = bytes([0x80 | opcode])
        if size < 126:
            header += bytes([0x80 | size])
        elif size < 65536:
            header += bytes([0x80 | 126]) + struct.pack("!H", size)
        else:
            header += bytes([0x80 | 127]) + struct.pack("!Q", size)
        self.socket.sendall(header + mask + bytes(v ^ mask[i % 4] for i, v in enumerate(payload)))

    def _receive(self):
        message = bytearray()
        while True:
            first, second = self._read(2)
            opcode, size = first & 15, second & 127
            if size == 126:
                size = struct.unpack("!H", self._read(2))[0]
            elif size == 127:
                size = struct.unpack("!Q", self._read(8))[0]
            if size > 32 * 1024 * 1024:
                raise ValueError("Inspector frame exceeds probe limit")
            mask = self._read(4) if second & 128 else None
            data = self._read(size)
            if mask:
                data = bytes(v ^ mask[i % 4] for i, v in enumerate(data))
            if opcode == 8:
                raise ConnectionError("Inspector closed the WebSocket")
            if opcode == 9:
                self._send(data, 10)
                continue
            if opcode == 10:
                continue
            message.extend(data)
            if len(message) > 32 * 1024 * 1024:
                raise ValueError("Inspector message exceeds probe limit")
            if first & 128:
                return json.loads(message)

    def call(self, method, **params):
        self.sequence += 1
        ident = self.sequence
        self._send(json.dumps({"id": ident, "method": method, "params": params}).encode())
        while True:
            result = self._receive()
            if result.get("id") != ident:
                continue
            if "error" in result:
                raise RuntimeError(result["error"])
            result = result.get("result", {})
            if "exceptionDetails" in result:
                raise RuntimeError(result["exceptionDetails"].get("text", "Evaluation failed"))
            return result

    def evaluate(self, expression, by_value=True):
        return self.call("Runtime.evaluate", expression=expression,
                         returnByValue=by_value, awaitPromise=True)["result"]

    def close(self):
        self.socket.close()
