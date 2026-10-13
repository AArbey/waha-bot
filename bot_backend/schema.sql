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