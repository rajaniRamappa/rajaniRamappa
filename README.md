# SGX Day Trading Dashboard

A browser-based live trading dashboard for Singapore Exchange (SGX) stocks, built with Moomoo OpenAPI, FastAPI, and Chart.js.

## Prerequisites

1. **Moomoo account** with SGX trading access enabled
2. **Moomoo OpenD gateway** running on your computer:
   - Open Moomoo desktop app → Settings → OpenAPI → Enable API
   - Or download OpenD separately from the Moomoo developer portal
   - Ensure it runs at `127.0.0.1:11111`
3. **Python 3.11+**

## Setup

```bash
git clone <repo-url>
cd rajaniRamappa

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure (copy and edit if needed)
cp .env.example .env
```

The default `.env` settings work if OpenD runs on the standard port.

## Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Open your browser at **http://localhost:8080**

## First Use

1. **Unlock trading** — enter your Moomoo trade PIN/password in the top-right field and click "Unlock Trading"
2. **Add symbols** — type SGX codes (e.g. `SG.D05`, `SG.U11`, `SG.C6L`) in the watchlist input and press Enter or `+`
3. **View chart** — click any symbol in the watchlist; use 1m / 5m / 15m buttons to change the candle interval
4. **Set alerts** — use the bottom bar to set price-above or price-below alerts; browser desktop notifications fire when triggered
5. **Place orders** — select a symbol, choose BUY/SELL, LIMIT/MARKET, enter quantity and price, click Submit
6. **Cancel orders** — open orders appear in the right panel; click Cancel next to any order

## SGX Market Hours

| Session       | Singapore Time (SGT, UTC+8) |
|---------------|-----------------------------|
| Pre-open      | 08:30 – 09:00               |
| Morning       | 09:00 – 12:30               |
| Lunch break   | 12:30 – 14:00               |
| Afternoon     | 14:00 – 17:00               |

The dashboard header shows a live market open/closed indicator.

## SGX Symbol Format

| Company            | Symbol   |
|--------------------|----------|
| DBS Group          | SG.D05   |
| United Overseas Bk | SG.U11   |
| Singapore Airlines | SG.C6L   |
| Singtel            | SG.Z74   |
| OCBC Bank          | SG.O39   |

## Architecture

```
Moomoo OpenD (127.0.0.1:11111)
        |
  moomoo-api Python SDK
        |
FastAPI backend (port 8080)
        | WebSocket
  Browser (HTML + JS)
```

- Real-time quotes and kline updates are pushed from Moomoo → backend → browser via WebSocket
- All blocking Moomoo SDK calls run in a thread pool (`run_in_executor`) so the async event loop stays free
- Trade password is entered in the browser, sent once to unlock, never stored on disk
