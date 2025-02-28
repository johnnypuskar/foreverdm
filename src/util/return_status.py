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
    
    def unpack(self):
        return (self._success, self._message)

    def __eq__(self, value):
        return self._success == value.success and self._message == value.message
    
    def __repr__(self):
        return f"<ReturnStatus({self._success}, '{self._message}')>"