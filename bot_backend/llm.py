import os
import litellm

from .config import LLM_URL, LLM_MODEL, MAX_TOOL_CALLS
from .functions import SCHEMA, execute_tool

def prompt_llm(messages):
    response = litellm.completion(
        model=f"openai/{LLM_MODEL}",               # add `openai/` prefix to model so litellm knows to route to OpenAI
        api_key=os.getenv("LLM_API_KEY"),                  # api key to your openai compatible endpoint
        api_base=LLM_URL,     # set API Base of your Custom OpenAI Endpoint
        messages=messages,
        tools=SCHEMA,
    )
    return response

def ask_ai(message, app, recent_messages=None):
    app.logger.info(f"Received message: {message}")
    # Read instructions from "instructions.txt" file
    with open("instructions.txt", "r") as f:
        instructions = f.read()

    messages = [
        {"role": "system", "content": instructions},
        *(recent_messages or []),
        message,
    ]

    for _ in range(MAX_TOOL_CALLS):  
        ai_response = prompt_llm(messages)
        response_message = ai_response.choices[0].message
        tool_calls = ai_response.choices[0].message.tool_calls
        if tool_calls:
            app.logger.info(f"Tool calls detected: {tool_calls}")
            messages.append(response_message)
            for tool_call in tool_calls:
                app.logger.info(f"\nExecuting tool call\n{tool_call}")
                resultat = execute_tool(tool_call.function.name, tool_call.function.arguments)
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": resultat})
        else:
            if response_message.content:
                return response_message.content
            else:
                # If the ai reponse has no content, add a system message to the messages and continue the loop
                messages.append({"role": "system","content": "You didn't provide any content in your response. Please provide a response with content."})
                continue
