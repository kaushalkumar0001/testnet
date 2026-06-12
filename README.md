# Binance Futures Testnet Trading Bot

A clean, well-structured Python CLI application for placing orders on the Binance Futures Testnet (USDT-M).

---

## Features

- Place **MARKET**, **LIMIT**, and **STOP_MARKET** orders (bonus type included)
- Supports **BUY** and **SELL** sides
- Full input validation with clear error messages
- Structured logging to `logs/trading_bot.log` (DEBUG-level detail)
- Clean separation: `client.py` (API layer) → `orders.py` (business logic) → `cli.py` (CLI layer)
- Credentials loaded securely from a `.env` file

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper (signing, requests, error handling)
│   ├── orders.py          # Order placement logic + OrderResult formatting
│   ├── validators.py      # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py  # Structured logging setup
├── cli.py                 # CLI entry point (argparse)
├── logs/
│   └── trading_bot.log    # Auto-created on first run
├── .env          # Template for credentials
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Register on Binance Futures Testnet

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Sign up / log in with your GitHub or Google account
3. Navigate to **API Key Management**
4. Click **Generate Key** and save your **API Key** and **Secret Key**

### 2. Clone / Download the project

```bash
git clone <your-repo-url>
cd trading_bot
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Requires Python 3.8+.

### 4. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

---

## Usage

```
python cli.py --symbol SYMBOL --side SIDE --type TYPE --quantity QTY [--price PRICE] [--stop-price STOP_PRICE] [--tif TIF]
```

### Arguments

| Argument       | Required | Description                                                  |
|----------------|----------|--------------------------------------------------------------|
| `--symbol`     | Yes      | Trading pair, e.g. `BTCUSDT`, `ETHUSDT`                     |
| `--side`       | Yes      | `BUY` or `SELL`                                              |
| `--type`       | Yes      | `MARKET`, `LIMIT`, or `STOP_MARKET`                          |
| `--quantity`   | Yes      | Order quantity, e.g. `0.001`                                 |
| `--price`      | LIMIT    | Limit price (required for LIMIT orders)                      |
| `--stop-price` | STOP     | Stop trigger price (required for STOP_MARKET orders)         |
| `--tif`        | No       | Time-in-force: `GTC` (default) \| `IOC` \| `FOK`            |

---

## Run Examples

### Market BUY

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Output:
```
╔══════════════════════════════════════════════════
║  ORDER REQUEST SUMMARY
╠══════════════════════════════════════════════════
║  Symbol     : BTCUSDT
║  Side       : BUY
║  Type       : MARKET
║  Quantity   : 0.001
╚══════════════════════════════════════════════════

┌─────────────────────────────────────────────
│  Order ID      : 3851920
│  Symbol        : BTCUSDT
│  Side          : BUY
│  Type          : MARKET
│  Status        : FILLED
│  Orig Qty      : 0.001
│  Executed Qty  : 0.001
│  Avg Price     : 43215.60
└─────────────────────────────────────────────

✅  Order placed successfully!
```

### Limit SELL

```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3500
```

### Market SELL

```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### Stop-Market BUY (Bonus order type)

```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 65000
```

### Limit BUY with IOC time-in-force

```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 40000 --tif IOC
```

---

## Logging

All requests, responses, and errors are logged to `logs/trading_bot.log`.

- **DEBUG** level: full API request params, raw response bodies
- **INFO** level: order placements and CLI completion
- **ERROR** level: validation failures, API errors, network issues

Console output is **WARNING** and above only (errors). Full detail is in the log file.

---

## Error Handling

| Scenario               | Exit Code | Behaviour                                  |
|------------------------|-----------|--------------------------------------------|
| Invalid input          | 2         | Prints validation message, logs error      |
| Binance API error      | 3         | Prints error code + message, logs error    |
| Network / timeout      | 4         | Prints connection error, logs error        |
| Unexpected exception   | 5         | Prints error + full traceback in log file  |

---

## Assumptions

- Only USDT-M futures are supported (the testnet only supports USDT-M)
- Quantity precision must match the symbol's lot size filter on Binance. If you get a `-1111` error, adjust your quantity precision (e.g. use `0.001` not `0.0012345` for BTC)
- The testnet sometimes resets balances; if you get `Margin is insufficient`, generate a new testnet API key to get fresh funds
- `python-binance` library is not used — direct REST calls via `requests` keep the dependency footprint minimal and make the API layer fully transparent

---

## Requirements

```
requests>=2.31.0
python-dotenv>=1.0.0
```
