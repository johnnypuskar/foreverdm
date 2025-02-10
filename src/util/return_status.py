class ReturnStatus:
    def __init__(self, success: bool, message: str):
        self._success = success
        self._message = message

    @property
    def success(self):
        return self._success
    
    @property
    def message(self):
        return self._message