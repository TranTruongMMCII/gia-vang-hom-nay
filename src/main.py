import argparse
import os
from typing import List, Optional


from dotenv import load_dotenv


try:  # pragma: no cover - allow running as both module and script
   from .dispatcher import send_price_update
   from .scheduler import Scheduler
   from .telegram_client import TelegramClient
except ImportError:  # pragma: no cover - script execution fallback
   from dispatcher import send_price_update
   from scheduler import Scheduler
   from telegram_client import TelegramClient




def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
   parser = argparse.ArgumentParser(description="Dispatch gold price updates")
   parser.add_argument("--once", action="store_true", help="Send one update and exit")
   return parser.parse_args(argv)




def main(argv: Optional[List[str]] = None) -> int:
   args = _parse_args(argv)
   load_dotenv()


   telegram_client = TelegramClient(os.getenv("TELEGRAM_TOKEN"), os.getenv("CHAT_ID"))


   run_once = args.once or os.getenv("DISPATCH_ONCE", "").lower() in {"1", "true", "yes"}
   if run_once:
       success = send_price_update(telegram_client)
       return 0 if success else 1


   scheduler = Scheduler(telegram_client)
   scheduler.start()
   return 0




if __name__ == "__main__":  # pragma: no cover - CLI entry
   raise SystemExit(main())

