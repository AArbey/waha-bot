from os import getenv
import time

from .audio import get_text_from_audio
from .config import BASE_URL, MEDIA_RESPONSE_BASE_URL, PUBLIC_BASE_URL

import requests


def read_message(payload, app):
    text, image_url = None, None
    try:
        if payload.get("_data").get("type") == "revoked":
            return text, image_url

        if payload.get("body") and payload.get("body") != "":
            text = payload["body"]

        if payload["hasMedia"]:
            if payload["media"]["mimetype"].startswith("audio/"):
                text = get_text_from_audio(payload, app)

            if payload["media"]["mimetype"].startswith("image/"):
                image_url = payload["media"]["url"].replace(MEDIA_RESPONSE_BASE_URL, PUBLIC_BASE_URL).replace("@", "%40")

        message_context = []
        if text:
            message_context.append({ "type": "text", "text": text })
        if image_url:
            message_context.append({ "type": "image_url", "image_url": { "url": image_url } })

        message_context = message_context if message_context else "User sent a message with no text and no audio."
        message_role = "assistant" if payload.get("fromMe") else "user"
    except Exception as e:
        app.logger.error(f"Error while reading message payload: {e}")
        message_context = "Error while reading message payload."
        message_role = "assistant"
    return {"role": message_role, "content": message_context}

def send_post_request(endpoint, payload):
    headers = {}
    if api_key := getenv("WAHA_API_KEY"):
        headers["x-api-key"] = api_key

    response = requests.post(
        BASE_URL + endpoint,
        json=payload,
        headers=headers
    )
    response.raise_for_status()
    return response

def send_get_request(endpoint, payload):
    headers = {}
    if api_key := getenv("WAHA_API_KEY"):
        headers["x-api-key"] = api_key

    response = requests.get(
        BASE_URL + endpoint,
        params=payload,
        headers=headers
    )
    response.raise_for_status()
    return response

def send_message(chat_id, text):
    # Send a text back via WhatsApp HTTP API
    payload = {
        "chatId": chat_id,
        "text": text,
        "session": "default",
    }
    send_post_request("sendText", payload)

def reply(chat_id, message_id, text):
    payload = {
        "chatId": chat_id,
        "text": text,
        "reply_to": message_id,
        "session": "default",
    }
    send_post_request("reply", payload)

def send_seen(chat_id, message_id, participant):
    payload = {
        "session": "default",
        "chatId": chat_id,
        "messageId": message_id,
        "participant": participant,
    }
    send_post_request("sendSeen", payload)

def start_typing(chat_id):
    payload = {
        "session": "default",
        "chatId": chat_id,
    }
    send_post_request("startTyping", payload)

def stop_typing(chat_id):
    payload = {
        "session": "default",
        "chatId": chat_id,
    }
    send_post_request("stopTyping", payload)

def get_recent_messages(chat_id, app):
    # We need to get the messages from the past 24 hours to provide context to the AI
    current_timestamp = int(time.time())
    twenty_four_hours_ago = current_timestamp - 24 * 60 * 60
    ####################
    # We add an offset of 1 to avoid getting the last message which is the one we just received
    # We also limit to 100 messages AND last 24 hours to avoid too much context for the AI
    ###############
    endpoint = "default/chats/" + chat_id + "/messages?sortBy=timestamp&merge=true&limit=100&offset=1&filter.timestamp.gte=" + str(twenty_four_hours_ago)

    whatsapp_response = send_get_request(endpoint, {}).json()

    recent_messages = []
    # Need to filter
    for message_data in whatsapp_response:
        recent_messages.append(read_message(message_data, app=app))
        

    # We need to reverse the list so that the most recent messages are at the end
    recent_messages.reverse()
    return recent_messages

def getPhoneNumberFromLid(lid):
    endpoint = "default/lids/" + lid
    response = send_get_request(endpoint, {}).json()

    pn = response.get("pn")
    real_number = pn.split("@")[0]
    return real_number
