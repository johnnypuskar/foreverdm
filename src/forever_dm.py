import openai

api_key_file = "C:/Users/johnn/Programming/Python/ForeverDM/ForeverDM/src/openai_api_key.txt"
OPENAI_API_KEY = None

SYSTEM_PROMPT = "Call "
INITIAL_MESSAGE = ""

with open(api_key_file, 'r') as file:
    OPENAI_API_KEY = file.read().strip()

if OPENAI_API_KEY is None:
    raise FileNotFoundError

openai.api_key = os.getenv(OPENAI_API_KEY)

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", INITIAL_MESSAGE}
    ],
    functions={
        {
            "name": "get_game_data",
            "description": "Returns a string of stats, descriptors, and information about the requested elements of the current D&D game.",
            "parameters": {
                "type": "string",
                "properties": {
                    "data": {
                        "type": "list",
                        
                    }
                },
                "required": ["data"]
            }
        }
    },
    function_call={"name": "get_game_data"},
    max_tokens=256
)

print(response)