import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


try:  # pragma: no cover - optional dependency for local dev
   import redis
except ImportError:  # pragma: no cover
   redis = None  # type: ignore




Entry = Dict[str, object]
PriceSnapshot = Dict[str, Dict[str, Dict[str, Optional[int]]]]




_REDIS_CLIENT: Optional[Any] = None




def _default_cache_file() -> Path:
   custom = os.getenv("PRICE_CACHE_FILE")
   if custom:
       return Path(custom).expanduser()
   base_dir = Path(__file__).resolve().parent.parent
   return base_dir / "data" / "last_prices.json"




def _normalise_snapshot(data: object) -> PriceSnapshot:
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




def _get_redis_client() -> Optional[Any]:
   global _REDIS_CLIENT
   if redis is None:
       return None
   if _REDIS_CLIENT is not None:
       return _REDIS_CLIENT


   url = os.getenv("REDIS_URL")
   host = os.getenv("REDIS_HOST")


   try:
       if url:
           client = redis.Redis.from_url(url, decode_responses=True)
       elif host:
           port = int(os.getenv("REDIS_PORT", "6379"))
           client = redis.Redis(
               host=host,
               port=port,
               username=os.getenv("REDIS_USERNAME") or None,
               password=os.getenv("REDIS_PASSWORD") or None,
               decode_responses=True,
           )
       else:
           return None


       client.ping()
   except (redis.RedisError, ValueError) as exc:
       print(f"[cache] Redis unavailable: {exc}")
       return None


   _REDIS_CLIENT = client
   return _REDIS_CLIENT




def _redis_key() -> str:
   return os.getenv("REDIS_CACHE_KEY", "gold:last")




def _load_from_file(target: Path) -> PriceSnapshot:
   if not target.exists():
       return {}


   try:
       with target.open("r", encoding="utf-8") as handle:
           data = json.load(handle)
   except (OSError, json.JSONDecodeError) as exc:
       print(f"[cache] Failed to load previous prices: {exc}")
       return {}


   return _normalise_snapshot(data)




def load_previous_prices(path: Optional[os.PathLike[str]] = None) -> PriceSnapshot:
   client = _get_redis_client()
   if client is not None:
       try:
           raw = client.get(_redis_key())
       except redis.RedisError as exc:  # pragma: no cover - network error
           print(f"[cache] Failed to read from Redis: {exc}")
       else:
           if not raw:
               return {}
           try:
               return _normalise_snapshot(json.loads(raw))
           except json.JSONDecodeError as exc:  # pragma: no cover - defensive
               print(f"[cache] Invalid JSON in Redis cache: {exc}")
               return {}


   target = Path(path) if path else _default_cache_file()
   return _load_from_file(target)




def _build_payload(entries: Iterable[Entry]) -> PriceSnapshot:
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
   return payload




def save_current_prices(entries: Iterable[Entry], path: Optional[os.PathLike[str]] = None) -> None:
   payload = _build_payload(entries)
   serialized = json.dumps(payload, ensure_ascii=False)


   client = _get_redis_client()
   redis_success = False
   if client is not None:
       try:
           client.set(_redis_key(), serialized)
           redis_success = True
       except redis.RedisError as exc:  # pragma: no cover - network error
           print(f"[cache] Failed to write to Redis: {exc}")


   explicit_path = path is not None or os.getenv("PRICE_CACHE_FILE")
   if redis_success and not explicit_path:
       return


   target = Path(path) if path else _default_cache_file()
   target.parent.mkdir(parents=True, exist_ok=True)
   with target.open("w", encoding="utf-8") as handle:
       handle.write(serialized)



