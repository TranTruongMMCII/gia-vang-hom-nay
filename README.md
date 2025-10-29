# Gold Price Notifier for Telegram

A Telegram bot that retrieves gold prices from multiple Vietnamese sources (SJC, Doji, PNJ, Phú Quý, Ngọc Thẩm) and sends formatted updates at scheduled times (6 AM, 9 AM, 12 PM, and 3 PM GMT+7). The bot runs on GitHub Actions and uses Redis to persist price snapshots for delta tracking.

## Features

- **Multi-source price fetching**: Retrieves live gold prices from SJC, Doji, PNJ, Phú Quý, and Ngọc Thẩm.
- **Scheduled updates**: Automatically sends updates at 6 AM, 9 AM, 12 PM, and 3 PM GMT+7.
- **Price change tracking**: Shows price deltas (e.g., `+450`, `-200`) compared to the previous update.
- **Redis persistence**: Stores the latest snapshot in Redis to maintain history across workflow runs.
- **Thousand-dong formatting**: Displays prices in thousands of VND (k VND/chỉ) for readability.
- **GitHub Actions integration**: Runs on GitHub-hosted runners with pip caching for faster builds.

## Project Structure

```text
gia-vang-hom-nay/
├── .github/
│   └── workflows/
│       └── gold-price-runner.yaml    # GitHub Actions workflow for scheduled runs
├── .env.example                      # Template for environment variables
├── .gitignore                        # Git ignore rules
├── README.md                         # Project documentation
├── requirements.txt                  # Python dependencies
├── data/                             # Local cache directory (fallback if Redis unavailable)
├── scripts/
│   └── start.sh                      # Shell script for local execution
└── src/
    ├── cache.py                      # Redis/file-based cache for price snapshots
    ├── dispatcher.py                 # Message formatting and Telegram dispatch
    ├── main.py                       # CLI entrypoint (supports --once flag)
    ├── show_prices.py                # CLI tool to print prices without sending
    ├── telegram_client.py            # Telegram bot wrapper
    └── price_fetchers/
        └── sources.py                # Fetchers for SJC, Doji, PNJ, Phú Quý, Ngọc Thẩm
```

## Prerequisites

- **Python 3.8+** (tested with Python 3.12)
- A **Telegram bot token** and **chat ID** (see setup instructions below)
- (Optional) A **Redis instance** for persistent price history across workflow runs

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/TranTruongMMCII/gia-vang-hom-nay.git
cd gia-vang-hom-nay
```

### 2. Install Dependencies

Ensure Python 3.8+ is installed, then install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Create a Telegram Bot and Get Credentials

#### 3.1. Create a Bot

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts to name your bot.
3. BotFather will provide a **bot token** (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`). Save this token.

#### 3.2. Get Your Chat ID

1. Start a conversation with your newly created bot (find it by the username you set).
2. Send any message to the bot (e.g., "Hello").
3. Visit the following URL in your browser (replace `<YOUR_BOT_TOKEN>` with your actual token):

   ```text
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```

4. Look for the `"chat":{"id":...}` field in the JSON response. The `id` value (e.g., `123456789`) is your **chat ID**.

Alternatively, you can use **@userinfobot** on Telegram:

1. Search for `@userinfobot` and start a conversation.
2. It will reply with your user ID, which you can use as the chat ID for personal messages.

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
TELEGRAM_TOKEN=your-bot-token-here
CHAT_ID=your-chat-id-here

# Redis connection (choose URL or host/port credentials)
# Option 1: Use a connection URL (recommended for managed Redis services)
REDIS_URL=rediss://default:password@your-redis-host:port/0

# Option 2: Use individual host/port/username/password
# REDIS_HOST=your-redis-host
# REDIS_PORT=6379
# REDIS_USERNAME=default
# REDIS_PASSWORD=your-redis-password

# Optional: customize the Redis key name
# REDIS_CACHE_KEY=gold:last
```

**Redis Setup Notes:**

- For a free Redis instance, consider [Redis Cloud](https://redis.com/try-free/) (30 MB free tier).
- If you don't configure Redis, the bot will fall back to a local JSON file (`data/last_prices.json`), but price history will not persist across GitHub Actions runs.

### 5. Set GitHub Secrets (for GitHub Actions)

To run the bot on GitHub Actions, add the following secrets to your repository:

1. Go to your repository on GitHub.
2. Navigate to **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret** and add:
   - `TELEGRAM_TOKEN`: Your bot token
   - `CHAT_ID`: Your chat ID
   - `REDIS_URL`: Your Redis connection URL (or use `REDIS_HOST`, `REDIS_PORT`, `REDIS_USERNAME`, `REDIS_PASSWORD` individually)

### 6. Run the Application

#### Local Execution

Use the provided shell script:

```bash
./scripts/start.sh
```

Or run directly:

```bash
python src/main.py --once   # Single run
# python src/main.py          # Continuous mode with scheduler
```

#### GitHub Actions

The workflow (`.github/workflows/gold-price-runner.yaml`) runs automatically at:

- **6 AM GMT+7** (23:00 UTC previous day)
- **9 AM GMT+7** (02:00 UTC)
- **12 PM GMT+7** (05:00 UTC)
- **3 PM GMT+7** (08:00 UTC)

You can also trigger it manually:

1. Go to **Actions** > **Telegram Gold Notifier**.
2. Click **Run workflow**.

## Usage

Once configured, the bot will:

1. Fetch gold prices from all sources.
2. Compare with the previous snapshot (from Redis or file cache).
3. Format a message showing current prices with deltas (e.g., `14.720 (+50)`).
4. Send the message to your Telegram chat.

### Example Output

```text
Cập nhật giá vàng lúc 25/10/2025 20:51:32 GMT+7:

SJC (k VND/chỉ)
Sản phẩm                       Mua        Bán
-------------------------  ----------  ----------
SJC miếng 0.5-2 chỉ        14.720 (0)  14.923 (0)
SJC nhẫn 9999 0.3-0.5 chỉ  14.610 (0)  14.870 (0)

Doji (k VND/chỉ)
Sản phẩm                     Mua        Bán
-------------------  ----------  ----------
Doji nhẫn tròn 9999  14.650 (0)  14.910 (0)

...
```

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the project.

## License

This project is open source and available under the MIT License.
