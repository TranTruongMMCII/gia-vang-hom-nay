# Gold Price Notifier for Telegram


This project is a Telegram bot that retrieves gold prices from specified websites and sends updates at scheduled times (6 AM, 9 AM, 12 PM, and 3 PM GMT+7). It is designed to run on the GitHub-hosted runners provided by GitHub Actions.


## Features


- Fetches gold prices from multiple sources.
- Sends updates to a specified Telegram chat.
- Scheduled updates at 6 AM, 9 AM, 12 PM, and 3 PM GMT+7.
- Persists the latest snapshot in Redis so deltas can be included in messages.


## Project Structure


```text
github-telegram-gold-notifier
├── .github
│   └── workflows
│       └── self_hosted_runner.yml
├── .env.example
├── requirements.txt
├── scripts
│   └── start.sh
├── src
│   ├── __init__.py
│   ├── dispatcher.py
│   ├── main.py
│   ├── scheduler.py
│   ├── show_prices.py
│   ├── telegram_client.py
│   ├── price_fetchers
│   │   ├── __init__.py
│   │   └── sources.py
└── README.md
```


## Setup Instructions


1. **Clone the repository:**


  ```bash
  git clone https://github.com/yourusername/github-telegram-gold-notifier.git
  cd github-telegram-gold-notifier
  ```


2. **Install dependencies:**
  Make sure you have Python 3.x installed. Then, install the required packages:


  ```bash
  pip install -r requirements.txt
  ```


3. **Configure environment variables:**
  Copy `.env.example` to `.env` and fill in your Telegram bot token, chat ID, and Redis credentials (`REDIS_URL` or `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD`).


4. **Run the application:**
  You can start the application using the provided shell script:
 
  ```bash
  ./scripts/start.sh
  ```


## Usage


Once the application is running, it will automatically fetch gold prices from the configured sources and send updates to your Telegram chat at the specified times.


## Contributing


Feel free to submit issues or pull requests if you have suggestions or improvements for the project.



