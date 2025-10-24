from typing import Iterable, Optional


import schedule
import time


try:  # pragma: no cover - support script-style imports
   from .dispatcher import send_price_update
except ImportError:  # pragma: no cover
   from dispatcher import send_price_update




class Scheduler:
   def __init__(self, telegram_client, dispatch_times: Optional[Iterable[str]] = None) -> None:
       self.telegram_client = telegram_client
       self.dispatch_times = list(dispatch_times or ["09:00", "12:00", "15:00"])
       schedule.clear("gold-price-job")
       for moment in self.dispatch_times:
           schedule.every().day.at(moment).do(self._run_job).tag("gold-price-job")


   def _run_job(self) -> None:
       if not send_price_update(self.telegram_client):
           print("[Scheduler] Dispatch skipped")


   def start(self) -> None:
       while True:
           schedule.run_pending()
           time.sleep(1)

