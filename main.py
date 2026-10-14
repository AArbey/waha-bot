from flask import Flask
from flask import request
import sqlite3

from bot_backend.llm import ask_ai, getAvailableModels, handle_llm_config_vote
from bot_backend.waha_api import get_recent_messages, getPhoneNumberFromLid, read_message, send_message, send_poll, send_seen, start_typing, stop_typing
from bot_backend.config import check_config
from bot_backend.database import init_db, init_config

app = Flask(__name__)

def checkCommand(payload, app):
    chat_id = payload["from"]
    phone_number = getPhoneNumberFromLid(chat_id)
    message_id = payload["id"]
    participant = payload.get('participant')
    try:
        send_seen(chat_id=chat_id, message_id=message_id, participant=participant)
        start_typing(chat_id=chat_id)
    except Exception as e:
        app.logger.error(f"Error while connectting to waha api: {e}")
    if payload.get("body"):
        text = payload["body"] 
        if text[0] == "/":
            app.logger.info(f"Received command from {phone_number}: {text}")
            if text == "/help":
                reply = "Hey !\n"
                stop_typing(chat_id=chat_id)
                send_message(chat_id=chat_id, text=reply)
                return True
            elif text == "/config":
                stop_typing(chat_id=chat_id)
                return True
            elif text == "/models":
                available_models = getAvailableModels()
                stop_typing(chat_id=chat_id)
                # WARNING, if you change question, you must also change the handle_llm_config_vote function in llm.py to match the new question
                send_poll(chat_id=chat_id, question="Available models:", options=available_models)
                return True
            else:
                reply = "Unknown command. Type /help for help."
                stop_typing(chat_id=chat_id)
                send_message(chat_id=chat_id, text=reply)
                return True
        else:
            return False
    else:
        return False

@app.route("/")
def whatsapp_echo():
    return "WhatsApp Bot is ready!"

@app.route("/bot", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        return "WhatsApp Bot is ready!"

    data = request.get_json()
    if data["event"] not in ["message", "poll.vote"]:
        app.logger.warning(f"Received unknown event {data['event']}")
        return f"Unknown event {data['event']}"

    if data["event"] == "poll.vote":
        payload = data["payload"]
        payload_poll = payload.get("poll")
        payload_vote = payload.get("vote")
        # Number in format 1231231231@lid
        chat_id = payload_vote["from"]
        phone_number = getPhoneNumberFromLid(chat_id)
        message_id = payload_vote["id"]
        # For groups - who sent the message
        participant = payload_vote.get('participant')
        if payload_poll.get("fromMe") == False:
            app.logger.info("Received poll vote for someone else's pole, ignoring.")
            return "OK"
    
        app.logger.info(f"Received poll vote from {phone_number}")
        send_seen(chat_id=chat_id, message_id=message_id, participant=participant)
        start_typing(chat_id=chat_id)
        handle_llm_config_vote(payload_vote)
        send_message(chat_id=chat_id, text=f"Your choice has been applied.")
        stop_typing(chat_id=chat_id)
        
        return "OK"

    payload = data["payload"]
    # Number in format 1231231231@lid
    chat_id = payload["from"]
    phone_number = getPhoneNumberFromLid(chat_id)
    message_id = payload["id"]
    # For groups - who sent the message
    participant = payload.get('participant')

    if not checkCommand(payload, app):
        try:
            send_seen(chat_id=chat_id, message_id=message_id, participant=participant)
            start_typing(chat_id=chat_id)
        except Exception as e:
            app.logger.error(f"Error while connectting to waha api: {e}")
        try:
            message = read_message(payload)
            app.logger.info(f"Received message from {phone_number}: {message}")
            history = get_recent_messages(chat_id=chat_id)
            reply = ask_ai(message, recent_messages=history, chat_id=chat_id)
        except Exception as e:
            app.logger.error(f"Error while processing message from {phone_number}: {e}")
            reply = "Sorry, I couldn't process your message. Please try again later.\nFull error: " + str(e)
        finally:
            stop_typing(chat_id=chat_id)
            send_message(chat_id=chat_id, text=reply)
    # Send OK back
    return "OK"

if __name__ == '__main__':
    with app.app_context():
        check_config()
        init_db()
        init_config()

    app.run(host='0.0.0.0', port=5000, debug=True)
    
