from datetime import datetime, timedelta, timezone
from itertools import groupby
from typing import Dict, List, Optional


try:  # pragma: no cover - support script-style imports
   from . import cache
   from .price_fetchers.sources import fetch_gold_price_entries
except ImportError:  # pragma: no cover
   import cache
   from price_fetchers.sources import fetch_gold_price_entries




def _format_currency(value: Optional[int]) -> str:
   if value is None:
       return "--"
   thousands = int(round(value / 1000))
   return f"{thousands:,}".replace(",", ".")




def _format_difference(current: Optional[int], previous: Optional[int]) -> Optional[str]:
   if current is None or previous is None:
       return None


   diff = current - previous
   diff_thousands = int(round(diff / 1000))
   if diff_thousands == 0:
       return "=0"
   return f"{diff_thousands:+,}".replace(",", ".")




def _format_value(current: Optional[int], previous: Optional[int]) -> str:
   current_text = _format_currency(current)
   if current is None:
       return current_text
   if previous is None:
       return current_text


   previous_text = _format_currency(previous)
   diff_text = _format_difference(current, previous)
   if diff_text is None:
       return current_text
   return f"{current_text} ({diff_text} vs {previous_text})"




def _format_section(
   source: str,
   rows: List[Dict[str, object]],
   previous_lookup: Dict[str, Dict[str, Dict[str, Optional[int]]]],
) -> str:
   unit = rows[0].get("unit", "k VND/chi")
   previous_by_product = previous_lookup.get(source, {})
   product_width = max(len("Product"), *(len(str(row["product"])) for row in rows))
   buy_values: List[str] = []
   sell_values: List[str] = []


   for row in rows:
       product_name = str(row["product"])
       previous_entry = previous_by_product.get(product_name, {})
       buy_values.append(_format_value(row.get("buy"), previous_entry.get("buy")))
       sell_values.append(_format_value(row.get("sell"), previous_entry.get("sell")))


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




def _build_message(
   entries: List[Dict[str, object]],
   previous_lookup: Dict[str, Dict[str, Dict[str, Optional[int]]]],
) -> str:
   tz = timezone(timedelta(hours=7))
   timestamp = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S GMT+7")
   header = f"Cap nhat gia vang luc {timestamp}:"


   sections: List[str] = []
   for source, group in groupby(entries, key=lambda item: item["source"]):
       rows = list(group)
       if rows:
           sections.append(_format_section(source, rows, previous_lookup))


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


   previous_lookup = cache.load_previous_prices()
   message = _build_message(entries, previous_lookup)
   telegram_client.send_message(message)
   try:
       cache.save_current_prices(entries)
   except Exception as exc:  # pragma: no cover - defensive logging
       print(f"[Dispatcher] Failed to persist cache: {exc}")
   return True



