import collections.abc

class DataStorer:
    def __init__(self):
        self._mappings = []

    def map_data_property(self, property_name: str, data_entry_name: str, export_function: callable = lambda v: v, export_falsy = True,
                            import_function: callable = lambda df, v: v, import_reliant_properties: list = []) -> None:
        self._mappings.append(DataStorer.PropertyMapping(
            property_name = property_name,
            data_entry_name = data_entry_name,
            export_function = export_function,
            export_falsy = export_falsy,
            import_function = import_function,
            import_reliant_properties = import_reliant_properties
        ))
    
    def export_data(self) -> dict:
        exported_data = {}
        for mapping in self._mappings:
            value = mapping.export_function(getattr(self, mapping.property_name))
            if not mapping.export_falsy and not bool(value):
                continue
            if isinstance(value, DataStorer):
                exported_data[mapping.data_entry_name] = value.export_data()
            else:
                exported_data[mapping.data_entry_name] = value
        return exported_data
    
    def import_data(self, data: dict) -> None:
        imported_properties = set()

        def _import_property(mapping):
            for reliant_property in mapping.import_reliant_properties:
                if reliant_property not in imported_properties:
                    reliant_mapping = next((m for m in self._mappings if m.property_name == reliant_property), None)
                    _import_property(reliant_mapping)

            if hasattr(self, mapping.property_name) and mapping.data_entry_name in data:
                import_value = mapping.import_function(getattr(self, mapping.property_name), data[mapping.data_entry_name])
                if isinstance(getattr(self, mapping.property_name, None), DataStorer):
                    getattr(self, mapping.property_name).import_data(import_value)
                else:
                    setattr(self, mapping.property_name, import_value)
            
            imported_properties.add(mapping.property_name)

        for mapping in self._mappings:
            _import_property(mapping)

    @classmethod
    def new_from_data(cls, data: dict, *args):
        instance = cls(*args)
        instance.import_data(data)
        return instance

    class PropertyMapping:
        def __init__(self, property_name: str, data_entry_name: str, export_function: callable = lambda v: v, export_falsy: bool = True,
                    import_function: callable = lambda df, v: v, import_reliant_properties: list = []):
            self.property_name = property_name
            self.data_entry_name = data_entry_name
            self.export_function = export_function
            self.export_falsy = export_falsy
            self.import_function = import_function
            self.import_reliant_properties = import_reliant_properties