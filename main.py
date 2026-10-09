import requests
from dotenv import load_dotenv
import os

from time import sleep
import pytz
from flask import Flask
from flask import request
from faster_whisper import WhisperModel
import time
import datetime


app = Flask(__name__)

load_dotenv()
api_key = os.getenv("WAHA_API_KEY")

headers = {
    "x-api-key": api_key
}

BASE_URL = os.getenv("WAHA_URL")
PUBLIC_BASE_URL = os.getenv("WAHA_PUBLIC_URL")
LLM_URL = os.getenv("LLM_URL")
LLM_MODEL = os.getenv("LLM_MODEL")
ALLOWED_USERS = os.getenv('ALLOWED_USERS').split(',')

TIMEZONE = pytz.timezone(os.getenv("TZ"))
MEDIA_RESPONSE_BASE_URL = "http://localhost:3000/api/"
AUDIO_SAVE_PATH = "./bot_data/audio/"
IMAGE_SAVE_PATH = "./bot_data/images/"

model_size = "faster-whisper"
model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8",
    cpu_threads=16
)

def transcribe_audio(file_path):
    segments, info = model.transcribe(
        file_path,
        language="fr",
        beam_size=5,
        vad_filter=True
    )
    transcription = []
    for segment in segments:
        print(
            f"[{segment.start:.2f} - {segment.end:.2f}] "
            f"{segment.text}"
        )
        transcription.append(segment.text.strip())
    
    output_text = " ".join(transcription)
    app.logger.info(f"Transcription result: {output_text}")
    return output_text


def send_message(chat_id, text):
    """
    Send message to chat_id.
    :param chat_id: Phone number + "@c.us" suffix - 1231231231@c.us
    :param text: Message for the recipient
    """
    # Send a text back via WhatsApp HTTP API
    response = requests.post(
        BASE_URL + "sendText",
        json={
            "chatId": chat_id,
            "text": text,
            "session": "default",
        },
        headers=headers
    )
    response.raise_for_status()

def reply(chat_id, message_id, text):
    response = requests.post(
        BASE_URL + "reply",
        json={
            "chatId": chat_id,
            "text": text,
            "reply_to": message_id,
            "session": "default",
        },
        headers=headers
    )
    response.raise_for_status()


def send_seen(chat_id, message_id, participant):
    response = requests.post(
        BASE_URL + "sendSeen",
        json={
            "session": "default",
            "chatId": chat_id,
            "messageId": message_id,
            "participant": participant,
        },
        headers=headers
    )
    response.raise_for_status()

def get_file(file_url, file_path):
    # file url is in format http://192.168.1.115:3001/api/files/default/id.oga
    response = requests.get(
        file_url,
        headers=headers,
    )
    response.raise_for_status()

    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
    else :
        app.logger.error(f"Failed to download file from {file_url}. Status code: {response.status_code}") 

def start_typing(chat_id):
    response = requests.post(
        BASE_URL + "startTyping",
        json={
            "session": "default",
            "chatId": chat_id,
        },
        headers=headers
    )
    response.raise_for_status()

def stop_typing(chat_id):
    response = requests.post(
        BASE_URL + "stopTyping",
        json={
            "session": "default",
            "chatId": chat_id,
        },
        headers=headers
    )
    response.raise_for_status()

def typing(chat_id, seconds):
    start_typing(chat_id=chat_id)
    sleep(seconds)
    stop_typing(chat_id=chat_id)

def ask_ai(message, recent_messages=None):
    instructions = (
        "Réponds en français. "
        "Utilise le contexte fourni pour poursuivre la conversation si c'est cohérent avec la demande. "
        "Le contexte contient tes messages précédents et ceux de l'utilisateur, avec l'horodatage, cependant ne commence pas tes réponses avec l'horodatage."
        "Tu n'auras que les 100 derniers messages ou les dernières 24h."
    )
    

    messages = [
        {"role": "system", "content": instructions},
        *(recent_messages or []),
        message,
    ]


    headers = {}
    if key := os.getenv("LLM_API_KEY"):
        headers["Authorization"] = f"Bearer {key}"

    response = requests.post(
        f"{LLM_URL.rstrip('/')}/chat/completions",
        headers=headers,
        json={
            "model": LLM_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "stream": False,
            "cache_prompt": True,
        },
        timeout=(10, 300),
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def get_recent_messages(chat_id, ):
    # We need to get the messages from the past 24 hours to provide context to the AI
    current_timestamp = int(time.time())
    twenty_four_hours_ago = current_timestamp - 24 * 60 * 60
    ####################
    # We add an offset of 1 to avoid getting the last message which is the one we just received
    # We also limit to 100 messages AND last 24 hours to avoid too much context for the AI
    ###############
    URL= BASE_URL + "default/chats/" + chat_id + "/messages?sortBy=timestamp&merge=true&limit=100&offset=1&filter.timestamp.gte=" + str(twenty_four_hours_ago)
    whatsapp_response = requests.get(
        URL,
        headers=headers
    )

    RECENT_MESSAGES = []
    # Need to filter
    for message_data in whatsapp_response.json():
        RECENT_MESSAGES.append(read_message(message_data))
        

    # We need to reverse the list so that the most recent messages are at the end
    RECENT_MESSAGES.reverse()
    whatsapp_response.raise_for_status()
    return RECENT_MESSAGES

def getPhoneNumberFromLid(lid):
    response = requests.get(
            BASE_URL + "default/lids/" + lid ,
            headers=headers
    )
    response.raise_for_status()
    pn = response.json().get("pn")
    real_number = pn.split("@")[0]
    return real_number

def read_message(payload):
    text, image_url = None, None
    if payload.get("_data").get("type") == "revoked":
        return text, image_url
    
    if payload.get("body") and payload.get("body") != "":
        text = payload["body"]

    if payload["hasMedia"]:
        if payload["media"]["mimetype"].startswith("audio/"):
            audio_url = payload["media"]["url"].replace(MEDIA_RESPONSE_BASE_URL, BASE_URL)
            file_type = payload["media"]["url"].split(".")[-1]
            file_id = payload['id']
            audio_file_path = f"{AUDIO_SAVE_PATH}{file_id}.{file_type}"
            transcribed_file_path = f"{AUDIO_SAVE_PATH}transcribed/{file_id}.txt"

            if os.path.exists(transcribed_file_path):
                with open(transcribed_file_path, "r") as f:
                    transcribed_text = f.read()
            else: 
                get_file(audio_url, audio_file_path)
                transcribed_text = transcribe_audio(audio_file_path)
                with open(transcribed_file_path, "w") as f:
                    f.write(transcribed_text)

            if transcribed_text:
                text = transcribed_text
            else: 
                app.logger.warning("No text could be transcribed from audio message")
                text = "User tried to send an audio message but it could not be transcribed."
        
        if payload["media"]["mimetype"].startswith("image/"):
            image_url = payload["media"]["url"].replace(MEDIA_RESPONSE_BASE_URL, PUBLIC_BASE_URL).replace("@", "%40")
    
    message_context = text
    if text and image_url:
        message_context = [
            { "type": "text", "text": text },
            { "type": "image_url", "image_url": { "url": image_url } }
        ]
    elif image_url and text is None:
        message_context = [
            { "type": "image_url", "image_url": { "url": image_url } }
        ]

    message_context = message_context if message_context else "User sent a message with no text and no audio."
    message_role = "assistant" if payload.get("fromMe") else "user"
    
    return {"role": message_role, "content": message_context}

def checkCommand(payload):
    reply = None
    if payload.get("body"):
        text = payload["body"] 
        if text[0] == "/":
            if text == "/help":
                reply = "Hey !\n"
            if text == "/config":
                init_config()
            else:
                reply = "Unknown command. Type /help for help."
    return reply

def init_config():
    app.logger.info("Initializing config...")

@app.route("/")
def whatsapp_echo():
    return "WhatsApp Echo Bot is ready!"


@app.route("/bot", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        return "WhatsApp Echo Bot is ready!"

    data = request.get_json()


    
    if data["event"] not in ["message"]:
        app.logger.warning(f"Received unknown event {data['event']}")
        return f"Unknown event {data['event']}"
    payload = data["payload"]
    # Number in format 1231231231@lid
    chat_id = payload["from"]
    phone_number = getPhoneNumberFromLid(chat_id)
    message_id = payload["id"]
    # For groups - who sent the message
    participant = payload.get('participant')
    
    send_seen(chat_id=chat_id, message_id=message_id, participant=participant)
    start_typing(chat_id=chat_id)
    reply = None
    try:
        reply = checkCommand(payload)
        if reply is None:
            message = read_message(payload)
            app.logger.info(f"Received message from {phone_number}: {message}")
            history = get_recent_messages(chat_id=chat_id)
            reply = ask_ai(message, recent_messages=history)
    except Exception as e:
        app.logger.error(f"Error while processing message from {phone_number}: {e}")
        reply = "Sorry, I couldn't process your message. Please try again later.\nFull error: " + str(e)
    finally:
        stop_typing(chat_id=chat_id)
        send_message(chat_id=chat_id, text=reply)
    # Send OK back
    return "OK"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
