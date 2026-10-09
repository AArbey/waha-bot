FROM python:3

RUN apt-get update && apt-get install -y python3-dev portaudio19-dev

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --force-reinstall --no-deps git+https://github.com/SYSTRAN/faster-whisper.git

COPY main.py ./
RUN mkdir -p ./bot_data/audio/transcribed
RUN mkdir -p ./bot_data/images/

CMD [ "python", "./main.py" ]