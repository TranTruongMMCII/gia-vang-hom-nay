try:  # pragma: no cover - allow both package and script execution
   from .price_fetchers.sources import fetch_gold_prices
except ImportError:  # pragma: no cover
   from price_fetchers.sources import fetch_gold_prices




def main() -> None:
   lines = fetch_gold_prices()
   if not lines:
       print("Không lấy được dữ liệu giá vàng.")
       return


   for line in lines:
       print(line)




if __name__ == "__main__":
   main()



