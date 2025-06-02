class DataStorer:
    def __init__(self):
        self._mappings = []

    def map_data_property(self, property_name: str, data_entry_name: str, no_import = False) -> None:
        self._mappings.append(DataStorer.PropertyMapping(
            property_name = property_name,
            data_entry_name = data_entry_name,
            no_import = no_import
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
        for mapping in self._mappings:
            if not mapping.no_import and hasattr(self, mapping.property_name) and mapping.data_entry_name in data:
                if isinstance(getattr(self, mapping.property_name, None), DataStorer):
                    getattr(self, mapping.property_name).import_data(data[mapping.data_entry_name])
                else:
                    setattr(self, mapping.property_name, data[mapping.data_entry_name])

    class PropertyMapping:
        def __init__(self, property_name: str, data_entry_name: str, no_import: bool = False):
            self.property_name = property_name
            self.data_entry_name = data_entry_name
            self.no_import = no_import