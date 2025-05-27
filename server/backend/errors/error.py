class Error(Exception):
    def __init__(self, code: int, name: str, message: str):
        self.code = code
        self.name = name
        self.message = message
    
    def __str__(self):
        return f"{self.name} {self.code}: {self.message}"