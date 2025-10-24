from __future__ import annotations


import codecs
import json
import re
from typing import Dict, Iterable, List, Optional


import requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree


SJC_URL = "https://sjc.com.vn/GoldPrice/Services/PriceService.ashx"
DOJI_XML_URL = "http://update.giavang.doji.vn/banggia/doji_92411/92411"
PHU_QUY_URL = "https://phuquygroup.vn/"
NGOC_THAM_URL = "https://ngoctham.com/bang-gia-vang/"
PNJ_URL = "https://edge-api.pnj.io/ecom-frontend/v1/get-gold-price?zone=00"


VNĐ_PER_CHI = "VNĐ/chỉ"


REQUEST_HEADERS = {
   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
}


SJC_TARGETS = {
   "Vàng SJC 0.5 chỉ, 1 chỉ, 2 chỉ": "SJC miếng 0.5-2 chỉ",
   "Vàng nhẫn SJC 99,99% 1 chỉ, 2 chỉ, 5 chỉ": "SJC nhẫn 9999 1-5 chỉ",
   "Vàng nhẫn SJC 99,99% 0.5 chỉ, 0.3 chỉ": "SJC nhẫn 9999 0.3-0.5 chỉ",
}


DOJI_TARGETS = {
   "nhẫn tròn 9999": "Doji nhẫn tròn 9999",
}


PHU_QUY_TARGETS = {
   "nhẫn tròn phú quý": "Phú Quý nhẫn tròn 999.9",
}


NGOC_THAM_TARGETS = {
   "nhẫn 999.9": "Ngọc Thẩm nhẫn 999.9",
}


PNJ_TARGETS = {
   "N24K": "PNJ nhẫn trơn 999.9",
   "TL": "PNJ phúc lộc tài 999.9",
}


SOURCE_PRIORITY = {
   "SJC": 0,
   "Doji": 1,
   "PNJ": 2,
   "Phú Quý": 3,
   "Ngọc Thẩm": 4,
}




def _clean_number(value: object, *, multiplier: float = 1.0, divisor: float = 1.0) -> Optional[int]:
   if value is None:
       return None


   if isinstance(value, (int, float)):
       numeric = float(value)
   elif isinstance(value, str):
       cleaned = re.sub(r"[^\d]", "", value)
       if not cleaned:
           return None
       numeric = float(cleaned)
   else:
       return None


   numeric = numeric * multiplier / divisor
   return int(round(numeric))




def _format_currency(value: Optional[int]) -> str:
   if value is None:
       return "--"
   return f"{value:,}".replace(",", ".")




def _request_text(url: str, *, max_attempts: int = 3) -> Optional[str]:
   last_exc: Optional[Exception] = None
   for attempt in range(max_attempts):
       try:
           response = requests.get(url, headers=REQUEST_HEADERS, timeout=10)
           response.raise_for_status()
           content = response.content
           if content.startswith(codecs.BOM_UTF8):
               return content.decode("utf-8-sig")


           encoding = response.encoding or "utf-8"
           try:
               return content.decode(encoding)
           except UnicodeDecodeError:
               return content.decode("utf-8", errors="replace")
       except requests.RequestException as exc:
           last_exc = exc
           continue


   if last_exc:
       print(f"[sources] Request failed for {url}: {last_exc}")
   return None




def _request_json(url: str) -> Optional[dict]:
   text = _request_text(url)
   if text is None:
       return None
   try:
       return json.loads(text)
   except json.JSONDecodeError as exc:
       print(f"[sources] Failed to decode JSON from {url}: {exc}")
       return None




def fetch_sjc_prices() -> List[Dict[str, object]]:
   payload = _request_json(SJC_URL)
   if payload is None:
       return []


   results: List[Dict[str, object]] = []
   for item in payload.get("data", []):
       type_name = item.get("TypeName", "")
       if type_name not in SJC_TARGETS:
           continue
       if item.get("BranchName") != "Hồ Chí Minh":
           continue


       buy_vnd = _clean_number(item.get("BuyValue"), divisor=10) or _clean_number(item.get("Buy"), multiplier=100)
       sell_vnd = _clean_number(item.get("SellValue"), divisor=10) or _clean_number(item.get("Sell"), multiplier=100)


       results.append(
           {
               "source": "SJC",
               "product": SJC_TARGETS[type_name],
               "buy": buy_vnd,
               "sell": sell_vnd,
               "unit": VNĐ_PER_CHI,
           }
       )


   return results




def fetch_doji_prices() -> List[Dict[str, object]]:
   xml_text = _request_text(DOJI_XML_URL)
   if not xml_text:
       return []


   try:
       root = ElementTree.fromstring(xml_text)
   except ElementTree.ParseError as exc:
       print(f"[sources] Failed to parse Doji XML: {exc}")
       return []


   results: List[Dict[str, object]] = []
   for row in root.findall(".//Row"):
       name = row.attrib.get("Name", "").lower()
       target_label = None
       for needle, label in DOJI_TARGETS.items():
           if needle in name:
               target_label = label
               break
       if not target_label:
           continue


       buy_vnd = _clean_number(row.attrib.get("Buy"), multiplier=1000)
       sell_vnd = _clean_number(row.attrib.get("Sell"), multiplier=1000)


       results.append(
           {
               "source": "Doji",
               "product": target_label,
               "buy": buy_vnd,
               "sell": sell_vnd,
               "unit": VNĐ_PER_CHI,
           }
       )


   return results




def fetch_phu_quy_prices() -> List[Dict[str, object]]:
   html = _request_text(PHU_QUY_URL)
   if not html:
       return []


   soup = BeautifulSoup(html, "html.parser")
   results: List[Dict[str, object]] = []
   seen: set[str] = set()


   for row in soup.select("#priceList tbody tr"):
       cells = row.find_all("td")
       if len(cells) < 3:
           continue
       name = cells[0].get_text(strip=True)
       key = name.lower()


       target_label = None
       for needle, label in PHU_QUY_TARGETS.items():
           if needle in key:
               target_label = label
               break
       if not target_label or target_label in seen:
           continue


       seen.add(target_label)
       buy_vnd = _clean_number(cells[1].get_text(strip=True))
       sell_vnd = _clean_number(cells[2].get_text(strip=True))


       results.append(
           {
               "source": "Phú Quý",
               "product": target_label,
               "buy": buy_vnd,
               "sell": sell_vnd,
               "unit": VNĐ_PER_CHI,
           }
       )


   return results




def fetch_ngoc_tham_prices() -> List[Dict[str, object]]:
   html = _request_text(NGOC_THAM_URL)
   if not html:
       return []


   soup = BeautifulSoup(html, "html.parser")
   results: List[Dict[str, object]] = []
   seen: set[str] = set()


   for row in soup.select("#gold-price-menu table.price-table tbody tr"):
       cells = row.find_all("td")
       if len(cells) < 3:
           continue
       name = cells[0].get_text(strip=True)
       key = name.lower()


       target_label = None
       for needle, label in NGOC_THAM_TARGETS.items():
           if needle in key:
               target_label = label
               break
       if not target_label or target_label in seen:
           continue


       seen.add(target_label)
       buy_vnd = _clean_number(cells[1].get_text(strip=True))
       sell_vnd = _clean_number(cells[2].get_text(strip=True))


       results.append(
           {
               "source": "Ngọc Thẩm",
               "product": target_label,
               "buy": buy_vnd,
               "sell": sell_vnd,
               "unit": VNĐ_PER_CHI,
           }
       )


   return results




def fetch_pnj_prices() -> List[Dict[str, object]]:
   payload = _request_json(PNJ_URL)
   if payload is None:
       return []


   results: List[Dict[str, object]] = []
   for item in payload.get("data", []):
       code = item.get("masp")
       target_label = PNJ_TARGETS.get(code)
       if not target_label:
           continue


       buy_vnd = _clean_number(item.get("giamua"), multiplier=1000)
       sell_vnd = _clean_number(item.get("giaban"), multiplier=1000)


       results.append(
           {
               "source": "PNJ",
               "product": target_label,
               "buy": buy_vnd,
               "sell": sell_vnd,
               "unit": VNĐ_PER_CHI,
           }
       )


   return results




def fetch_gold_prices() -> List[str]:
   entries: List[Dict[str, object]] = []
   for fetcher in (
       fetch_sjc_prices,
       fetch_doji_prices,
       fetch_phu_quy_prices,
       fetch_ngoc_tham_prices,
       fetch_pnj_prices,
   ):
       entries.extend(fetcher())


   if not entries:
       return []


   entries.sort(key=lambda item: (SOURCE_PRIORITY.get(item["source"], 99), item["product"]))


   lines: List[str] = []
   for item in entries:
       unit = item.get("unit", VNĐ_PER_CHI)
       buy = _format_currency(item.get("buy"))
       sell = _format_currency(item.get("sell"))
       lines.append(f"[{item['source']}] {item['product']} - Mua: {buy} {unit} | Bán: {sell} {unit}")


   return lines

