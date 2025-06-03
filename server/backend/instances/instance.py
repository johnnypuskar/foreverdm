from server.backend.instances.acts.act_factory import ActFactory

class Instance:
    def __init__(self, campaign_id, location_id):
        self.campaign_id = campaign_id
        self.location_id = location_id
        self.act = None
    
    def has_statblock(self, statblock_id):
        if self.act is None:
            return False
        return statblock_id in self.act.statblock_ids

    def set_act_type(self, act_type):
        if self.act is not None and self.act.type == act_type:
            return
        self.act = ActFactory.new(act_type, self.campaign_id, self.location_id, self.act.statblock_ids if self.act is not None else set())
    
    def add_statblock(self, statblock_id):
        if self.act is None:
            return
        
        if statblock_id not in self.act.statblock_ids:
            self.act.statblock_ids.add(statblock_id)
    
    def remove_statblock(self, statblock_id):
        if self.act is None:
            return
        
        if statblock_id in self.act.statblock_ids:
            self.act.statblock_ids.remove(statblock_id)

    def get_view_data(self, statblock_id):
        if self.act is None:
            return None
        
        return self.act.get_view_data(statblock_id)