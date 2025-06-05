class Command:
    def __init__(self, statblock_id, campaign_id):
        self.statblock_id = statblock_id
        self.campaign_id = campaign_id
    
    def validate_act(self, act):
        return False
    
    def execute(self, act):
        return (False, "Command not implemented.")
    
    class Response:
        def __init__(self, success, message):
            self.success = success
            self.message = message
