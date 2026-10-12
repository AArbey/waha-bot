import json

from pydantic import ValidationError
from bot_backend.tools.weather import getWeather, WeatherArgs



SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "Weather",
            "description": "Returns the current weather for a given city.",
            "parameters": WeatherArgs.model_json_schema(),
        },
    }
]


def execute_tool(toolName: str, arguments_json: str) -> str:
    try:
        data = json.loads(arguments_json)
    except json.JSONDecodeError:
        return "Error: arguments_json is not valid JSON."

    if toolName not in [tool["function"]["name"] for tool in SCHEMA]:
        return f"Error: The tool '{toolName}' is not authorized."

    # To validate the arguments, we use the Pydantic model associated with the tool.
    # The class name is derived from the tool name by appending 'Args'.
    # Same for the function name, which is derived from the tool name by adding 'get' prefix.
    
    args_class_name = toolName + "Args"
    function_name = "get" + toolName
    if args_class_name not in globals():
        raise ValueError(f"Error: No argument class found for tool '{toolName}'.")
    if function_name not in globals():
        raise ValueError(f"Error: No function found for tool '{toolName}'.")

    try:
        args = globals()[args_class_name](**data)
    except ValidationError as erreur:
        detail = erreur.errors()[0]
        return f"Error: Validation error ({detail['loc']}) : {detail['msg']}."
    return globals()[function_name](args)
