import os
from faster_whisper import WhisperModel
import requests
from flask import current_app

from .config import BASE_URL, NUMBER_OF_THREADS_FOR_WHISPER_MODEL, MEDIA_RESPONSE_BASE_URL, AUDIO_SAVE_PATH

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8",
    cpu_threads=NUMBER_OF_THREADS_FOR_WHISPER_MODEL
)

def get_file(file_url, file_path):
    # file url is in format http://192.168.1.115:3001/api/files/default/id.oga
    response = requests.get(
        file_url
    )
    response.raise_for_status()

    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
    else :
        current_app.logger.error(f"Failed to download file from {file_url}. Status code: {response.status_code}") 

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
    return output_text

def get_text_from_audio(payload):
    try:
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
            text = f"Transcribed text from audio: {transcribed_text}"
        else: 
            current_app.logger.warning("No text could be transcribed from audio message")
            text = "User tried to send an audio message but it could not be transcribed."
    except Exception as e:
        current_app.logger.error(f"Error while transcribing audio: {e}")
        text = "Error while transcribing audio."
    return text