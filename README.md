# Gold Price Notifier for Telegram


This project is a Telegram bot that retrieves gold prices from specified websites and sends updates at scheduled times (9 AM, 12 PM, and 3 PM). It is designed to run on a self-hosted GitHub Actions runner.


## Features


- Fetches gold prices from multiple sources.
- Sends updates to a specified Telegram chat.
- Scheduled updates at 9 AM, 12 PM, and 3 PM.


## Project Structure


```
github-telegram-gold-notifier
├── .github
│   └── workflows
│       └── self_hosted_runner.yml
├── configs
│   ├── settings.example.env
│   └── sources.yaml
├── requirements.txt
├── scripts
│   └── start.sh
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── scheduler.py
│   ├── telegram_client.py
│   ├── price_fetchers
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── sources.py
│   └── utils
│       ├── __init__.py
│       └── parser.py
└── README.md
```


## Setup Instructions


1. **Clone the repository:**
  ```
  git clone https://github.com/yourusername/github-telegram-gold-notifier.git
  cd github-telegram-gold-notifier
  ```


2. **Install dependencies:**
  Make sure you have Python 3.x installed. Then, install the required packages:
  ```
  pip install -r requirements.txt
  ```


3. **Configure environment variables:**
  Copy `settings.example.env` to `.env` and fill in your Telegram bot token and any other necessary configurations.


4. **Configure sources:**
  Edit `configs/sources.yaml` to include the URLs of the websites from which you want to fetch gold prices.


5. **Run the application:**
  You can start the application using the provided shell script:
  ```
  ./scripts/start.sh
  ```


## Usage


Once the application is running, it will automatically fetch gold prices from the configured sources and send updates to your Telegram chat at the specified times.


## Contributing


Feel free to submit issues or pull requests if you have suggestions or improvements for the project.

