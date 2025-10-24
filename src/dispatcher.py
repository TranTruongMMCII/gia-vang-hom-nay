from datetime import datetime
from typing import List, Optional


try:  # pragma: no cover - support script-style imports
   from .price_fetchers.sources import fetch_gold_prices
except ImportError:  # pragma: no cover
   from price_fetchers.sources import fetch_gold_prices




def _build_message(lines: List[str]) -> str:
   timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
   header = f"Cap nhat gia vang luc {timestamp}:"
   return "\n".join([header, *lines])




def _fetch_lines() -> Optional[List[str]]:
   try:
       return fetch_gold_prices()
   except Exception as exc:  # pragma: no cover - defensive logging
       print(f"[Dispatcher] Failed to fetch prices: {exc}")
       return None




def send_price_update(telegram_client) -> bool:
   lines = _fetch_lines()
   if not lines:
       print("[Dispatcher] No prices retrieved; skipping dispatch")
       return False


   message = _build_message(lines)
   telegram_client.send_message(message)
   return True



