import json
import openai

class APIWrapper:
    def __init__(self, key, config, system_default):
        self._config = config
        openai.api_key = key
        self._system_default = system_default
    
    def add_function(self, function):
        self._functions.append(function.as_dict)
    
    def remove_function(self, name):
        self._functions[:] = filter(lambda x: x["name"] != name, self._functions)

    def send_request(self, message, system_extra = None):
        # Construct messages list
        messages = [{"role": "system", "content": self._system_default}]
        if system_extra is not None:
            messages.append({"role": "system", "content": system_extra})
        messages.append({"role": "user", "content": message})

        # Send completion request
        completion = openai.ChatCompletion.create(
            model = self._config["model"],
            messages = messages,
            functions = self._config["functions"],
            temperature = self._config["temperature"],
            top_p = self._config["top_p"],
            n = self._config["n"],
            presence_penalty = self._config["presence_penalty"],
            frequency_penalty = self._config["frequency_penalty"]
        )

        # TODO: Log token usage

        # Return message
        return completion