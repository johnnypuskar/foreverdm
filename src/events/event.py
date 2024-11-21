class CompositeEvent():
    def __init__(self, *events):
        self._event_entries = []
        for event in events:
            if not isinstance(event, ReactionEvent):
                raise TypeError("CompositeEvent only accepts Event objects")
            self._event_entries.append(event)
    
    @property
    def event_entries(self):
        return self._event_entries

class ReactionEvent():
    def __init__(self, event_type, context):
        self._event_type = event_type
        self._context = context

    @property
    def event_type(self):
        return self._event_type
    
    @property
    def context(self):
        return self._context
    
    def decompose_context(self):
        return self._context.decompose()
