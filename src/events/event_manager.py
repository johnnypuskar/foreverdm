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

    # async def fire_events(self, events: list, context):
    #     tasks = [subscriber.handle_event(event, context) for subscriber in self._subscribers for event in events]
    #     await asyncio.gather(*tasks)
    
    # async def fire_multievents(self, event_data: list):
    #     tasks = [subscriber.handle_event(event[0], event[1]) for subscriber in self._subscribers for event in event_data]
    #     await asyncio.gather(*tasks)