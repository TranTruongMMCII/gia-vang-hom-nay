import os
from typing import Optional

import requests


class TelegramClient:
    """Thin wrapper around Telegram's sendMessage endpoint."""

    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None) -> None:
        self.token = token or os.getenv("TELEGRAM_TOKEN")
        self.chat_id = chat_id or os.getenv("CHAT_ID")
        self.base_url: Optional[str] = None
        if self.token:
            self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, message: str) -> Optional[dict]:
        """Send a message or fall back to printing if credentials are missing."""

        if not self.token or not self.chat_id or not self.base_url:
            print("[TelegramClient] Missing TELEGRAM_TOKEN or CHAT_ID; printing message instead:")
            print(message)
            return None

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        try:
            response = requests.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            print(f"[TelegramClient] Failed to send message: {exc}")
            return None
