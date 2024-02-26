import google.ai.generativelanguage as glm

class Interactable():

    def __init__(self, name, description):
        self._name = name
        self._description = description
        self._position = None

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        self._position = value

    @property
    def update_func_declaration(self):
        return glm.FunctionDeclaration(
            name = 'update',
            description = 'Sets the description of this object as a result of an interaction.',
            parameters = glm.Schema(
                type = glm.Type.OBJECT,
                properties = {
                    'new_description': glm.Schema(type = glm.Type.STRING)
                },
                required = ['new_description']
            )
        )

    def update(self, new_description):
        self._description = new_description