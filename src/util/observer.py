from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def signal(self, event: str, *data):
        pass

class Emitter:
    def __init__(self):
        self._observers = []
    
    def connect(self, observer: Observer):
        self._observers.append(observer)
    
    def disconnect(self, observer: Observer):
        self._observers.remove(observer)
    
    def emit(self, event: str, data):
        for observer in self._observers:
            observer.signal(event, data)