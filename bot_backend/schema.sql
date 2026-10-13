CREATE TABLE IF NOT EXISTS audio_transcriptions(
    file_id TEXT PRIMARY KEY,
    transcription TEXT NOT NULL,
    sent_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    llm_url TEXT NOT NULL,
    encrypted_api_key BLOB,
    allowed_users TEXT             
);
CREATE TABLE IF NOT EXISTS rappels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT NOT NULL,
    message TEXT NOT NULL,
    target_time TEXT NOT NULL,
    last_reminer_sent_time TEXT NOT NULL,
    importance INTEGER NOT NULL DEFAULT 0,
    sent_count INTEGER NOT NULL DEFAULT 0
);