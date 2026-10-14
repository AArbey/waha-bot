import json

from pydantic import ValidationError
from bot_backend.tools.addreminder import AddReminderArgs, doAddReminder
from bot_backend.tools.editreminder import EditReminderArgs, doEditReminder
from bot_backend.tools.removereminder import RemoveReminderArgs, doRemoveReminder
from bot_backend.tools.weather import doGetWeather, GetWeatherArgs
from bot_backend.tools.getdate import GetDateArgs, doGetDate
from bot_backend.tools.checkReminder import CheckRemindersArgs, doCheckReminders

SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "GetWeather",
            "description": "Returns the current weather for a given city.",
            "parameters": GetWeatherArgs.model_json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "GetDate",
            "description": "Returns the current date and time.",
            "parameters": GetDateArgs.model_json_schema(),
        },
    }
    #{
    #    "type": "function",
    #    "function": {
    #        "name": "AddReminder",
    #        "description": "Adds a reminder for the user.",
    #        "parameters": AddReminderArgs.model_json_schema(),
    #    },
    #},
    #{
    #    "type": "function",
    #    "function": {
    #        "name": "CheckReminders",
    #        "description": "Checks the reminders for the current user.",
    #        "parameters": CheckRemindersArgs.model_json_schema(),
    #    },
    #},
    #{
    #    "type": "function",
    #    "function": {
    #        "name": "RemoveReminder",
    #        "description": "Removes a reminder for the user.",
    #        "parameters": RemoveReminderArgs.model_json_schema(),
    #    },
    #},
    #{
    #    "type": "function",
    #    "function": {
    #        "name": "EditReminder",
    #        "description": "Edits a reminder for the user. You don't have to provide all the fields, only the ones you want to change. The reminder_id is required.",
    #        "parameters": EditReminderArgs.model_json_schema(),
    #    },
    #}
]



def execute_tool(toolName: str, arguments_json: str, chat_id: str = None) -> str:
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
    function_name = "do" + toolName
    if args_class_name not in globals():
        raise ValueError(f"Error: No argument class found for tool '{toolName}'.")
    if function_name not in globals():
        raise ValueError(f"Error: No function found for tool '{toolName}'.")

    try:
        args = globals()[args_class_name](**data)
    except ValidationError as erreur:
        detail = erreur.errors()[0]
        return f"Error: Validation error ({detail['loc']}) : {detail['msg']}."
    if toolName in ["AddReminder", "CheckReminders", "EditReminder"]:
        return globals()[function_name](args, chat_id=chat_id)
    return globals()[function_name](args)
