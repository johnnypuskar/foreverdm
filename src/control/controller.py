import asyncio
from src.events.event_context import EventContext
from src.util.constants import EventType
from src.events.event import ReactionEvent, CompositeEvent

class Controller:
    def __init__(self):
        self._event_manager = None
        self._statblock = None


    ## Event Management ##

    @property
    def event_manager(self):
        return self._event_manager
    
    @event_manager.setter
    def event_manager(self, event_manager):
        if self._event_manager is not None:
            self._event_manager.unsubscribe(self)
        self._event_manager = event_manager
        self._event_manager.subscribe(self)
    
    async def handle_reaction(self, event):
        if self._statblock is not None:
            await self._statblock.handle_reaction(event)

    # async def handle_events(self, events, context):
    #     if self._statblock is not None:
    #         await self._statblock.handle_events(events, context)

    def trigger_reaction(self, event_type: str, context: EventContext):
        if self._event_manager is not None:
            modifiers = self.fire_event(ReactionEvent(event_type, context))

            # TODO: Apply reaction modifiers list to context
    
    def trigger_reactions(self, events: list):
        if self._event_manager is not None:
            events = [ReactionEvent(event[0], event[1]) for event in events]
            self.fire_event(CompositeEvent(*events))

    def fire_event(self, event):
        if self._event_manager is not None:
            asyncio.run(self._event_manager.fire_event(event))

    # def fire_events(self, events, context):
    #     if self._event_manager is not None:
    #         asyncio.run(self._event_manager.fire_events(events, context))

    # def fire_multievents(self, event_data):
    #     if self._event_manager is not None:
    #         asyncio.run(self._event_manager.fire_multievents(event_data))

    ## Statblock ##

    @property
    def statblock(self):
        return self._statblock
    
    @statblock.setter
    def statblock(self, statblock):
        if self._statblock is not None:
            self._statblock._controller = None
        self._statblock = statblock
        self._statblock._controller = self

    def select(self, options):
        return options[0]
    
    ## Control Actions ##

    def end_turn(self):
        self.fire_event(EventType.TRIGGER_END_TURN, EventContext(self._statblock))