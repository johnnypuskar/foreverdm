class DataStorer:
    def __init__(self):
        self._mappings = []

    def map_data_property(self, property_name: str, data_entry_name: str) -> None:
        self._mappings.append(DataStorer.PropertyMapping(
            property_name = property_name,
            data_entry_name = data_entry_name
        ))
    
    def export_data(self) -> dict:
        exported_data = {}
        for mapping in self._mappings:
            value = getattr(self, mapping.property_name)
            if isinstance(value, DataStorer):
                exported_data[mapping.data_entry_name] = value.export_data()
            else:
                exported_data[mapping.data_entry_name] = getattr(self, mapping.property_name)
        return exported_data
    
    def import_data(self, data: dict) -> None:
        try:
            for mapping in self._mappings:
                if isinstance(getattr(self, mapping.property_name, None), DataStorer):
                    getattr(self, mapping.property_name).import_data(data[mapping.data_entry_name])
                else:
                    setattr(self, mapping.property_name, data[mapping.data_entry_name])
        except KeyError as e:
            raise KeyError(f"Data Import Error: {e}")

    class PropertyMapping:
        def __init__(self, property_name: str, data_entry_name: str):
            self.property_name = property_name
            self.data_entry_name = data_entry_name