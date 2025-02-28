from abc import ABC

class ControllerCommand(ABC):
    def __init__(self, name):
        self._name = name
        self._parameters = {}
    
    def get_name(self):
        return self._name

    def __getattr__(self, name):
        if name in self._parameters:
            return self._parameters[name]
        raise AttributeError(f"ControllerCommand has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        if name not in ["_name", "_parameters"]:
            self._parameters[name] = value
        else:
            super().__setattr__(name, value)
