import asyncio
from src.events.observer import Emitter

class EventManager:
    def __init__(self):
        self._subscribers = []

    def subscribe(self, subscriber):
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        self._subscribers.remove(subscriber)

    async def fire_event(self, event: str, context):
        tasks = [subscriber.handle_event(event, context) for subscriber in self._subscribers]
        await asyncio.gather(*tasks)