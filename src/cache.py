import json
import os
from pathlib import Path
from typing import Dict, Iterable, Optional


Entry = Dict[str, object]
PriceSnapshot = Dict[str, Dict[str, Dict[str, Optional[int]]]]




def _default_cache_file() -> Path:
   custom = os.getenv("PRICE_CACHE_FILE")
   if custom:
       return Path(custom).expanduser()
   base_dir = Path(__file__).resolve().parent.parent
   return base_dir / "data" / "last_prices.json"




def load_previous_prices(path: Optional[os.PathLike[str]] = None) -> PriceSnapshot:
   target = Path(path) if path else _default_cache_file()
   if not target.exists():
       return {}


   try:
       with target.open("r", encoding="utf-8") as handle:
           data = json.load(handle)
   except (OSError, json.JSONDecodeError) as exc:
       print(f"[cache] Failed to load previous prices: {exc}")
       return {}


   snapshot: PriceSnapshot = {}
   if not isinstance(data, dict):
       return snapshot


   for source, products in data.items():
       if not isinstance(products, dict):
           continue
       source_key = str(source)
       snapshot[source_key] = {}
       for product, payload in products.items():
           if not isinstance(payload, dict):
               continue
           product_key = str(product)
           snapshot[source_key][product_key] = {
               "buy": payload.get("buy"),
               "sell": payload.get("sell"),
               "unit": payload.get("unit"),
           }
   return snapshot




def save_current_prices(entries: Iterable[Entry], path: Optional[os.PathLike[str]] = None) -> None:
   target = Path(path) if path else _default_cache_file()
   target.parent.mkdir(parents=True, exist_ok=True)


   payload: PriceSnapshot = {}
   for entry in entries:
       source = str(entry.get("source", "")).strip()
       product = str(entry.get("product", "")).strip()
       if not source or not product:
           continue


       payload.setdefault(source, {})[product] = {
           "buy": entry.get("buy"),
           "sell": entry.get("sell"),
           "unit": entry.get("unit"),
       }


   with target.open("w", encoding="utf-8") as handle:
       json.dump(payload, handle, ensure_ascii=False, indent=2)



