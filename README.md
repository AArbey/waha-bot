# Waha bot

Waha bot connects your WhatsApp account to an AI model. It uses recent chat history and supports text, French voice messages, and images with a compatible model.

## The WAHA API

Follow the [official WAHA installation guide](https://waha.devlike.pro/docs/how-to/install/).

## Waha bot

Create a `.env` file using `.env.example` as a reference. Set your WAHA credentials, AI endpoint and model, and `ALLOWED_USERS`.

```bash
docker compose up -d --build
```

Open the [WAHA dashboard](http://localhost:3001/dashboard), start the `default` session, and scan the QR code with WhatsApp.

Send the bot a message. Replies are in French by default.
