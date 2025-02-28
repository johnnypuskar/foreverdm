from src.instances.instance import Instance
from src.util.return_status import ReturnStatus
from uuid import uuid4

class InstanceManager:
    def __init__(self):
        self._instances = {}
    
    def create_instance(self, instance_class):
        if isinstance(instance_class, Instance):
            instance = instance_class()
            instance_id = str(uuid4())
            self._instances[instance_id] = instance
            return instance_id
        return None
    
    def join_instance(self, instance_id, controller):
        if instance_id in self._instances:
            instance = self._instances[instance_id]
            if not instance.has_controller(controller):
                instance.add_controller(controller)
                return True
        return False
    
    def leave_instance(self, instance_id, controller):
        if instance_id in self._instances:
            instance = self._instances[instance_id]
            if instance.has_controller(controller):
                instance.remove_controller(controller)
                return True
        return False

    def issue_command(self, instance_id, controller, command):
        if instance_id in self._instances:
            instance = self._instances[instance_id]
            return instance.issue_command(controller, command)
        return ReturnStatus(False, f"Instance ID {str(instance_id)} not found.")