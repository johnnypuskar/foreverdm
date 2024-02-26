import json
import openai

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class GPTAPIWrapper:
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

class GeminiAPIWrapper:
    def __init__(self, key):
        genai.configure(api_key = key)
    
    def get_tokens(self, content):
        model = genai.GenerativeModel('gemini-pro')
        tokens = model.count_tokens(content)
        return tokens

    def send_request(self, message):
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(message,
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ]
        )
        return response.text