from flask import Flask
from flask import request

from bot_backend.llm import ask_ai
from bot_backend.waha_api import get_recent_messages, getPhoneNumberFromLid, read_message, send_message, send_seen, start_typing, stop_typing
from bot_backend.config import check_config

app = Flask(__name__)

def checkCommand(payload):
    reply = None
    if payload.get("body"):
        text = payload["body"] 
        if text[0] == "/":
            if text == "/help":
                reply = "Hey !\n"
            if text == "/config":
                configuring = True
                init_config()
            else:
                reply = "Unknown command. Type /help for help."
    return reply

def init_config():
    app.logger.info("Initializing config...")

@app.route("/")
def whatsapp_echo():
    return "WhatsApp Bot is ready!"

@app.route("/bot", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        return "WhatsApp Bot is ready!"

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
            message = read_message(payload, app=app)
            app.logger.info(f"Received message from {phone_number}: {message}")
            history = get_recent_messages(chat_id=chat_id, app=app)
            reply = ask_ai(message, recent_messages=history, app=app)
    except Exception as e:
        app.logger.error(f"Error while processing message from {phone_number}: {e}")
        reply = "Sorry, I couldn't process your message. Please try again later.\nFull error: " + str(e)
    finally:
        stop_typing(chat_id=chat_id)
        send_message(chat_id=chat_id, text=reply)
    # Send OK back
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    check_config()
