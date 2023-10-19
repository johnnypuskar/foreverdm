class StatProfile:
    def __init__(self, abilities):
        self._abilities = abilities

    def get_profile_data(self) -> str:
        return f"abilities{str(self._abilities)}"
    
    def get_abilities(self):
        return f" abilities{self._abilities}" if self._abilities else ""