import sqlite3
import os
from cryptography.fernet import Fernet
from flask import current_app

from bot_backend.config import DB_PATH, LLM_URL, LLM_MODEL, LLM_API_KEY, ALLOWED_USERS


# Clé de chiffrement dans les variables d'environnement
SECRET_KEY = os.environ.get("MASTER_ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher = Fernet(SECRET_KEY.encode())

def connexion():
    return sqlite3.connect(DB_PATH)

def init_db():
    try:
        with connexion() as db:
            with current_app.open_resource("./bot_backend/schema.sql") as f:
                db.executescript(f.read().decode("utf8"))
    except Exception as e:
        print(f"Error initializing database: {e}")

def insert_new_transcription(file_id, transcription, date):
    try:
        with connexion() as db:
            query = f"INSERT INTO audio_transcriptions (file_id, transcription, date) VALUES (?,?,?)"
            db.execute(query, (file_id, transcription, date))
            db.commit()
    except Exception as e:
        print(f"Error inserting new transcription into database: {e}")

def get_transcription(file_id):
    try:
        with connexion() as db:
            query = f"SELECT * FROM audio_transcriptions WHERE file_id = ?"
            cursor = db.execute(query, (file_id,))
            result = cursor.fetchone()
            return result
    except Exception as e:
        print(f"Error retrieving transcription from database: {e}")
        return None

def remove_old_transcriptions(days):
    try:
        with connexion() as db:
            query = f"DELETE FROM audio_transcriptions WHERE date < datetime('now', '-{days} days')"
            db.execute(query)
            db.commit()
    except Exception as e:
        print(f"Error removing old transcriptions from database: {e}")

def update_config(llm_url=None, llm_model=None, llm_api_key=None, allowed_users=None):
    if all(value is None for value in (llm_url, llm_model, llm_api_key, allowed_users)):
        return

    try:
        encrypted_api_key = (
            cipher.encrypt(llm_api_key.encode()).decode()
            if llm_api_key is not None else None
        )
        values = (llm_url, llm_model, encrypted_api_key, allowed_users)
        with connexion() as db:
            cursor = db.execute("""
                UPDATE config SET
                    llm_url = COALESCE(?, llm_url),
                    model = COALESCE(?, model),
                    encrypted_api_key = COALESCE(?, encrypted_api_key),
                    allowed_users = COALESCE(?, allowed_users)
            """, values)
            if cursor.rowcount == 0:
                db.execute("""
                    INSERT INTO config (llm_url, model, encrypted_api_key, allowed_users)
                    VALUES (?, ?, ?, ?)
                """, values)
            db.commit()
    except Exception as e:
        print(f"Error updating config in database: {e}")

def init_config():
    try:
        update_config(
            llm_url=LLM_URL,
            llm_model=LLM_MODEL,
            llm_api_key=LLM_API_KEY,
            allowed_users=",".join(ALLOWED_USERS)
        )
    except Exception as e:
        current_app.logger.error(f"Error initializing config in database: {e}")
        

def get_llm_config():
    with connexion() as conn:
        row = conn.execute("""
            SELECT llm_url, model, encrypted_api_key
            FROM config
            ORDER BY id
            LIMIT 1
        """).fetchone()

    if row is None:
        raise ValueError("No LLM configuration stored in config table")

    llm_url, llm_model, encrypted_api_key = row

    if isinstance(encrypted_api_key, str):
        encrypted_api_key = encrypted_api_key.encode()

    api_key = (
        cipher.decrypt(encrypted_api_key).decode()
        if encrypted_api_key else None
    )
    return llm_url, llm_model, api_key