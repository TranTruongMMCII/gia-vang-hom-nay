from datetime import datetime, timedelta, timezone
from itertools import groupby
from typing import Dict, List, Optional


try:  # pragma: no cover - support script-style imports
   from .price_fetchers.sources import fetch_gold_price_entries
except ImportError:  # pragma: no cover
   from price_fetchers.sources import fetch_gold_price_entries




def _format_currency(value: Optional[int]) -> str:
   if value is None:
       return "--"
   return f"{value:,}".replace(",", ".")




def _format_section(source: str, rows: List[Dict[str, object]]) -> str:
   unit = rows[0].get("unit", "VND/chi")
   product_width = max(len("Product"), *(len(str(row["product"])) for row in rows))
   buy_values = [_format_currency(row.get("buy")) for row in rows]
   sell_values = [_format_currency(row.get("sell")) for row in rows]
   buy_width = max(len("Buy"), *(len(value) for value in buy_values))
   sell_width = max(len("Sell"), *(len(value) for value in sell_values))


   lines = [
       f"{source} ({unit})",
       f"{'Product'.ljust(product_width)}  {'Buy'.rjust(buy_width)}  {'Sell'.rjust(sell_width)}",
       f"{'-' * product_width}  {'-' * buy_width}  {'-' * sell_width}",
   ]


   for row, buy_text, sell_text in zip(rows, buy_values, sell_values):
       product = str(row["product"]).ljust(product_width)
       buy = buy_text.rjust(buy_width)
       sell = sell_text.rjust(sell_width)
       lines.append(f"{product}  {buy}  {sell}")


   return f"<pre>{'\n'.join(lines)}</pre>"




def _build_message(entries: List[Dict[str, object]]) -> str:
   tz = timezone(timedelta(hours=7))
   timestamp = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S GMT+7")
   header = f"Cập nhật giá vàng lúc {timestamp}:"


   sections: List[str] = []
   for source, group in groupby(entries, key=lambda item: item["source"]):
       rows = list(group)
       if rows:
           sections.append(_format_section(source, rows))


   return "\n\n".join([header, *sections]) if sections else header




def _fetch_entries() -> Optional[List[Dict[str, object]]]:
   try:
       return fetch_gold_price_entries()
   except Exception as exc:  # pragma: no cover - defensive logging
       print(f"[Dispatcher] Failed to fetch prices: {exc}")
       return None




def send_price_update(telegram_client) -> bool:
   entries = _fetch_entries()
   if not entries:
       print("[Dispatcher] No prices retrieved; skipping dispatch")
       return False


   message = _build_message(entries)
   telegram_client.send_message(message)
   return True



