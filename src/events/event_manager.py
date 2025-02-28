import asyncio
from src.events.observer import Emitter
from src.events.event import CompositeEvent, ReactionEvent

class EventManager:
    def __init__(self):
        self._subscribers = []

    def subscribe(self, subscriber):
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        self._subscribers.remove(subscriber)

    async def fire_event(self, event):
        if isinstance(event, ReactionEvent):
            await self.fire_event(CompositeEvent(event))
            return
        elif isinstance(event, CompositeEvent):
            tasks = [subscriber.handle_reaction(event) for subscriber in self._subscribers]
            return await asyncio.gather(*tasks)