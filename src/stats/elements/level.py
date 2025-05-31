from server.backend.database.util.data_storer import DataStorer

class Level(DataStorer):
    def __init__(self):
        super().__init__()
        self._levels = {}
        self.map_data_property("_levels", "levels")
    
    def get_level(self, class_name = None):
        """
        Returns the level of the given class_name. If class_name is None, returns the total sum level of all classes.

        param class_name: str - name of the class to get the level of (optional)
        
        return: int - level of the given class_name or the total sum level of all classes. If class_name is not found, returns -1.
        """
        if class_name is not None:
            return self._levels.get(class_name, -1)
        return sum(self._levels.values())
    
    def add_level(self, class_name, level = 1):
        """
        Adds the given amount of levels to the given class_name.
        
        param class_name: str - name of the class to add the levels to
        param level: int - amount of levels to add, default is 1

        return: None
        """
        if class_name not in self._levels:
            self._levels[class_name] = level
        else:
            self._levels[class_name] += level