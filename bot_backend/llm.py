import os
import litellm
import requests
from flask import current_app

from .config import MAX_TOOL_CALLS
from .functions import SCHEMA, execute_tool
from .database import get_llm_config, update_config

def prompt_llm(messages):
    current_app.logger.info(f"Prompting LLM with messages: {messages}")
    llm_url, llm_model, decrypted_api_key = get_llm_config()
    current_app.logger.info(f"LLM configuration: URL={llm_url}, Model={llm_model}, API Key={'***' if decrypted_api_key else None}")
    if llm_url and llm_model and decrypted_api_key:
        response = litellm.completion(
            model=f"openai/{llm_model}",               
            api_key=decrypted_api_key,          
            api_base=llm_url,  
            messages=messages,
            tools=SCHEMA,
        )
        return response

def ask_ai(message, recent_messages=None):
    current_app.logger.info(f"Received message: {message}")
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
            current_app.logger.info(f"Tool calls detected: {tool_calls}")
            messages.append(response_message)
            for tool_call in tool_calls:
                current_app.logger.info(f"\nExecuting tool call\n{tool_call}")
                resultat = execute_tool(tool_call.function.name, tool_call.function.arguments)
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": resultat})
        else:
            if response_message.content:
                return response_message.content
            else:
                # If the ai reponse has no content, add a system message to the messages and continue the loop
                messages.append({"role": "system","content": "You didn't provide any content in your response. Please provide a response with content."})
                continue


def getAvailableModels():
    try:
        llm_url, llm_model, decrypted_api_key = get_llm_config()
        if llm_url and decrypted_api_key:
            endpoint = f"{llm_url}/models"
            availableModels = requests.get(endpoint, headers={"Authorization": f"Bearer {decrypted_api_key}"})
            model_ids=[model["id"] for model in availableModels.json().get("data", [])]
            current_app.logger.info(f"Available models ids: {model_ids}")
            return model_ids
        else:
            current_app.logger.error("LLM configuration is incomplete. Please check the database for LLM_URL, LLM_MODEL, and LLM_API_KEY.")
            return None
    except Exception as e:
        current_app.logger.error(f"Error while fetching available models: {e}")
        return None

def getLoadedModel():
    llm_url, llm_model, decrypted_api_key = get_llm_config()
    if llm_url and decrypted_api_key:
        endpoint = f"{llm_url}/running"
        loadedModel = requests.get(endpoint, headers={"Authorization": f"Bearer {decrypted_api_key}"})
        return loadedModel.json()
    else:
        current_app.logger.error("LLM configuration is incomplete. Please check the database for LLM_URL, LLM_MODEL, and LLM_API_KEY.")
        return None

def handle_llm_config_vote(payload_vote):
    selected_options = payload_vote.get("selectedOptions")
    if len(selected_options) > 1:
        current_app.logger.warning(f"Received multiple selected options in poll vote: {selected_options}. This is probably because the poll is not actually a model config poll, ignoring.")
        return
    if len(selected_options) == 0:
        current_app.logger.warning(f"Received poll vote with no selected options: {payload_vote}. ")
        return
    selected_option = selected_options[0]
    current_app.logger.info(f"Received poll vote: {selected_option}")
    if selected_option:
        available_models = getAvailableModels()
        if selected_option in available_models:
            update_config(llm_model=selected_option)
