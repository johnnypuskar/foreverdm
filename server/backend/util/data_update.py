class DataUpdate:
    @staticmethod
    def set(value, *path):
        return {"value": value, "path": path}