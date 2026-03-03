# CSFloat Sniper Bot

A Python bot that monitors the CSFloat marketplace and alerts you when skins matching your criteria are listed at good prices.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get your CSFloat API key:
   - Go to https://csfloat.com
   - Navigate to your profile → Developer tab
   - Generate an API key

3. Configure the bot:
   - Open `config.json`
   - Add your API key
   - Set your snipe criteria

## Configuration

Edit `config.json` to customize:

- `api_key`: Your CSFloat API key
- `check_interval`: Seconds between checks (recommended: 15-20)
- `filters`: Pre-filter listings from the API (more efficient!)
  - `sort_by`: How to sort results
    - `highest_discount` - Best for sniping deals
    - `best_deal` - CSFloat's algorithm for good deals
    - `lowest_price` - Cheapest items first
    - `most_recent` - Newest listings
    - `expires_soon` - Ending soonest
  - `type`: `buy_now` or `auction`
  - `max_price`: Maximum price in cents (50000 = $500)
  - `limit`: How many listings to check (max 50)
- `criteria`: Additional filters applied after fetching
  - `min_discount_percent`: Minimum discount vs Steam Market (%)
  - `market_hash_names`: Specific items to watch (empty = all items)
  - `min_float`: Minimum float value
  - `max_float`: Maximum float value
  - `category`: 0=any, 1=normal, 2=stattrak, 3=souvenir
- `notifications`:
  - `desktop`: Enable desktop notifications (true/false)
  - `discord`: Enable Discord webhook notifications (true/false)
  - `log_file`: File to log all snipes
- `discord`: Discord webhook settings (only needed if Discord notifications enabled)
  - Get webhook URL: Server Settings → Integrations → Webhooks → New Webhook

## Efficient Sniping Strategy

The bot now uses CSFloat's built-in filters to be much more efficient:

1. **Sort by highest_discount**: Only checks items already discounted
2. **Set max_price**: Focus on your budget range
3. **Set min_discount_percent**: Only alert on deals above your threshold

Example config for sniping cheap deals:
```json
"filters": {
  "sort_by": "highest_discount",
  "type": "buy_now",
  "max_price": 10000,
  "limit": 50
},
"criteria": {
  "min_discount_percent": 20
}
```

This checks the top 50 highest-discounted items under $100, and only alerts if discount is 20%+.

## Notifications

The bot supports multiple notification methods:

1. **Console Output** (always on): Prints alerts to terminal
2. **Desktop Notifications** (optional): Pop-up notifications on your desktop
3. **Discord Webhooks** (optional): Sends rich embeds to your Discord channel
4. **Log File** (always on): Records all snipes to `snipes.log`

To set up Discord notifications:
1. Go to your Discord server
2. Server Settings → Integrations → Webhooks
3. Click "New Webhook"
4. Copy the webhook URL
5. Paste it in `config.json` under `discord.webhook_url`
6. Set `"discord": true` in notifications

## Duplicate Prevention

The bot tracks seen listings in `seen_listings.json` so it won't alert you multiple times for the same item, even after restarting. This file persists between runs, so you won't get spammed with alerts for items you've already seen.

## Usage

Run the bot:
```bash
python sniper.py
```

The bot will:
- Monitor new listings every 5 seconds (configurable)
- Check if they meet your criteria
- Log good deals to `snipes.log`
- Print alerts to console

## Example Criteria

Watch for cheap AK-47 Redlines under $20 with good float:
```json
{
  "max_price": 2000,
  "min_discount_percent": 10,
  "market_hash_names": ["AK-47 | Redline (Field-Tested)"],
  "max_float": 0.20
}
```

## Notes

- Prices are in cents (100 = $1.00)
- The bot only monitors - it doesn't auto-buy
- Check `snipes.log` for all found deals
- Respect CSFloat's rate limits
