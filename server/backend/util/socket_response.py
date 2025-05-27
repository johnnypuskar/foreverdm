from __future__ import annotations

class SocketResponse:
    def __init__(self, signal: str, data: dict = {}, disconnect: bool = False):
        self.signal = signal
        self.data = data
        self.disconnect = disconnect
    
    @staticmethod
    def Redirect(url: str, disconnect = True) -> SocketResponse:
        return SocketResponse('redirect', {'url': url}, disconnect)