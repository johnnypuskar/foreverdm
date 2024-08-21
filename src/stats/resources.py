from src.util.resettable_value import ResettableValue

class ResourceIndex:
    def __init__(self):
        self._resources = {}
    
    def add(self, name, value):
        if name in self._resources:
            raise ValueError("Resource already exists in index.")
        self._resources[name] = ResettableValue(value)
    
    def expend(self, name, amount = 1):
        if name not in self._resources:
            return (False, "Resource does not exist in index.")
        if self._resources[name] < amount:
            return (False, f"Cannot use {amount} {name}, only {self._resources[name]} left.")
        self._resources[name] -= amount
        return (True, f"Used {amount} {name}.")
    
    def restore(self, name, amount = 1):
        if name not in self._resources:
            return (False, "Resource does not exist in index")
        self._resources[name] += amount
        if self._resources[name] > self._resources[name].initial:
            self._resources[name] = self._resources[name].initial
        return (True, f"Restored {name} to {self._resources[name]}.")
    
    def reset(self, name):
        if name not in self._resources:
            return (False, "Resource does not exist in index.")
        self._resources[name].reset()
        return (True, f"Reset {name}.")
    
    def reset_all(self):
        for resource in self._resources.values():
            resource.reset()
        return (True, "Reset all resources.")

    def get(self, name):
        if name not in self._resources:
            raise ValueError("Resource does not exist in index.")
        return self._resources[name]