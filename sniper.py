import requests
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

try:
    from plyer import notification
    DESKTOP_NOTIFICATIONS = True
except ImportError:
    DESKTOP_NOTIFICATIONS = False

class CSFloatSniper:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.api_key = self.config['api_key']
        self.base_url = "https://csfloat.com/api/v1"
        self.headers = {}
        if self.api_key and self.api_key != "YOUR_API_KEY_HERE":
            self.headers["Authorization"] = self.api_key
        self.seen_file = "seen_listings.json"
        self.seen_listings = self._load_seen_listings()
    
    def _load_seen_listings(self) -> dict:
        """Load previously seen listings from file"""
        if os.path.exists(self.seen_file):
            try:
                with open(self.seen_file, 'r') as f:
                    data = json.load(f)
                    listings = data.get('listings', {})
                    
                    # Migrate old format (list) to new format (dict with timestamps)
                    if isinstance(listings, list):
                        print("🔄 Migrating seen_listings to new format...")
                        current_time = time.time()
                        listings = {listing_id: current_time for listing_id in listings}
                        # Save migrated data
                        with open(self.seen_file, 'w') as fw:
                            json.dump({'listings': listings}, fw)
                    
                    return listings
            except Exception as e:
                print(f"Error loading seen listings: {e}")
        return {}
    
    def _save_seen_listings(self):
        """Persist seen listings to file"""
        try:
            with open(self.seen_file, 'w') as f:
                json.dump({'listings': self.seen_listings}, f)
        except Exception as e:
            print(f"Error saving seen listings: {e}")
    
    def _cleanup_old_listings(self):
        """Remove listings older than 24 hours"""
        current_time = time.time()
        cutoff_time = current_time - (24 * 60 * 60)  # 24 hours ago
        
        old_count = len(self.seen_listings)
        self.seen_listings = {
            listing_id: timestamp 
            for listing_id, timestamp in self.seen_listings.items()
            if timestamp > cutoff_time
        }
        
        removed = old_count - len(self.seen_listings)
        if removed > 0:
            print(f"🧹 Cleaned up {removed} old listings from cache")
            self._save_seen_listings()
        
    def get_listings(self, **params) -> List[Dict]:
        """Fetch listings from CSFloat API"""
        url = f"{self.base_url}/listings"
        params.setdefault('limit', 50)
        params.setdefault('sort_by', 'most_recent')
        
        try:
            # Try with API key first if available
            if self.headers:
                response = requests.get(url, headers=self.headers, params=params)
            else:
                # Try without auth (public endpoint)
                response = requests.get(url, params=params)
            
            response.raise_for_status()
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, dict):
                # New format: {"data": [...], "cursor": "..."}
                if 'data' in data:
                    return data['data']
                # Old format: {"listings": [...]}
                elif 'listings' in data:
                    return data['listings']
                else:
                    return []
            elif isinstance(data, list):
                # Direct list format
                return data
            else:
                print(f"Unexpected response format: {type(data)}")
                return []
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited - return empty and let caller handle backoff
                return None
            print(f"Error fetching listings: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching listings: {e}")
            return []
    
    def calculate_discount(self, listing: Dict) -> float:
        """Calculate discount percentage vs reference price"""
        # Try new API format first (reference object)
        reference = listing.get('reference', {})
        reference_price = reference.get('predicted_price') or reference.get('base_price', 0)
        
        # Fallback to old format (scm in item)
        if not reference_price:
            item = listing.get('item', {})
            reference_price = item.get('scm', {}).get('price', 0)
        
        listing_price = listing.get('price', 0)
        
        if reference_price > 0:
            discount = ((reference_price - listing_price) / reference_price) * 100
            return round(discount, 2)
        return 0.0
    
    def meets_criteria(self, listing: Dict) -> bool:
        """Check if listing meets snipe criteria"""
        criteria = self.config['criteria']
        item = listing.get('item', {})
        price = listing.get('price', 0)
        
        # Price check
        max_price = criteria.get('max_price')
        if max_price and price > max_price:
            return False
        
        # Discount check
        min_discount = criteria.get('min_discount_percent', 0)
        if min_discount > 0:
            discount = self.calculate_discount(listing)
            if discount < min_discount:
                return False
        
        # Market hash name filter
        hash_names = criteria.get('market_hash_names', [])
        if hash_names:
            if item.get('market_hash_name') not in hash_names:
                return False
        
        # Float value checks
        min_float = criteria.get('min_float')
        max_float = criteria.get('max_float')
        float_value = item.get('float_value')
        
        if min_float is not None and float_value < min_float:
            return False
        if max_float is not None and float_value > max_float:
            return False
        
        return True
    
    def send_discord_notification(self, log_entry: Dict):
        """Send Discord webhook notification for snipe"""
        if not self.config['notifications'].get('discord', False):
            return
        
        webhook_url = self.config.get('discord', {}).get('webhook_url')
        if not webhook_url:
            return
        
        try:
            # Build fields list
            fields = [
                {
                    "name": "💰 Price",
                    "value": f"${log_entry['price']:.2f}",
                    "inline": True
                },
                {
                    "name": "📊 Discount",
                    "value": f"{log_entry['discount_percent']:.2f}%",
                    "inline": True
                }
            ]
            
            # Only add float field if it exists
            if log_entry['float'] != 'N/A':
                fields.append({
                    "name": "🎲 Float",
                    "value": f"{log_entry['float']:.6f}",
                    "inline": True
                })
            
            # Create rich embed for Discord
            embed = {
                "title": "🎯 CSFloat Snipe Found!",
                "description": f"**{log_entry['item_name']}**",
                "color": 3066993,  # Green color
                "fields": fields,
                "url": log_entry['url'],
                "timestamp": log_entry['timestamp'],
                "footer": {
                    "text": "Act fast! 🏃"
                }
            }
            
            payload = {
                "content": "@here New snipe alert!",
                "embeds": [embed]
            }
            
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            print("💬 Discord notification sent")
        except Exception as e:
            print(f"Failed to send Discord notification: {e}")
    
    def send_desktop_notification(self, log_entry: Dict):
        """Send desktop notification for snipe"""
        if not self.config['notifications'].get('desktop', False):
            return
        
        if not DESKTOP_NOTIFICATIONS:
            return
        
        try:
            message = f"{log_entry['item_name']}\n${log_entry['price']:.2f} ({log_entry['discount_percent']:.1f}% off)"
            
            notification.notify(
                title=f"🎯 CSFloat Snipe Found!",
                message=message,
                app_name="CSFloat Sniper",
                timeout=10
            )
        except Exception as e:
            print(f"Failed to send desktop notification: {e}")
    
    def log_snipe(self, listing: Dict):
        """Log sniped listing to file and send notifications"""
        log_file = self.config['notifications'].get('log_file', 'snipes.log')
        
        item = listing.get('item', {})
        discount = self.calculate_discount(listing)
        float_value = item.get('float_value')
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'listing_id': listing.get('id'),
            'item_name': item.get('market_hash_name'),
            'price': listing.get('price') / 100,  # Convert cents to dollars
            'float': float_value if float_value is not None else 'N/A',
            'discount_percent': discount,
            'url': f"https://csfloat.com/item/{listing.get('id')}"
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"\n🎯 SNIPE FOUND!")
        print(f"Item: {log_entry['item_name']}")
        print(f"Price: ${log_entry['price']:.2f}")
        if float_value is not None:
            print(f"Float: {float_value:.6f}")
        else:
            print(f"Float: N/A (not applicable)")
        print(f"Discount: {log_entry['discount_percent']:.2f}%")
        print(f"URL: {log_entry['url']}\n")
        
        # Send notifications
        self.send_desktop_notification(log_entry)
        self.send_discord_notification(log_entry)
    
    def run(self):
        """Main bot loop"""
        print("CSFloat Sniper Bot Started")
        print(f"Checking every {self.config['check_interval']} seconds")
        
        # Display active filters
        filters = self.config.get('filters', {})
        print(f"Filters: {json.dumps(filters, indent=2)}")
        print(f"Criteria: {json.dumps(self.config['criteria'], indent=2)}\n")
        
        # Cleanup old listings on startup
        self._cleanup_old_listings()
        
        last_cleanup = time.time()
        cleanup_interval = 3600  # Run cleanup every hour
        
        base_interval = self.config['check_interval']
        current_interval = base_interval
        rate_limit_count = 0
        
        while True:
            try:
                # Build query params from filters
                params = {}
                
                # Apply filters from config
                filters = self.config.get('filters', {})
                params.update(filters)
                
                # Override with criteria if specified
                criteria = self.config['criteria']
                if criteria.get('category'):
                    params['category'] = criteria['category']
                if criteria.get('min_float') is not None:
                    params['min_float'] = criteria['min_float']
                if criteria.get('max_float') is not None:
                    params['max_float'] = criteria['max_float']
                
                # Add market hash names if specified
                hash_names = criteria.get('market_hash_names', [])
                if hash_names:
                    # Note: API might not support this directly, will filter client-side
                    pass
                
                listings = self.get_listings(**params)
                
                # Handle rate limiting
                if listings is None:
                    rate_limit_count += 1
                    current_interval = min(base_interval * (2 ** rate_limit_count), 120)  # Max 2 minutes
                    print(f"⚠️  Rate limited! Backing off to {current_interval}s interval...")
                    time.sleep(current_interval)
                    continue
                
                # Reset interval on successful request
                if rate_limit_count > 0:
                    rate_limit_count = 0
                    current_interval = base_interval
                    print(f"✅ Rate limit cleared, back to {base_interval}s interval")
                
                new_count = 0
                snipe_count = 0
                
                for listing in listings:
                    listing_id = listing.get('id')
                    
                    if not listing_id:
                        continue
                    
                    # Skip if already seen
                    if listing_id in self.seen_listings:
                        continue
                    
                    self.seen_listings[listing_id] = time.time()
                    new_count += 1
                    
                    # Check if meets snipe criteria
                    if self.meets_criteria(listing):
                        self.log_snipe(listing)
                        snipe_count += 1
                
                # Save seen listings after each check
                if new_count > 0:
                    self._save_seen_listings()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checked {new_count} new listings, found {snipe_count} snipes")
                else:
                    # Show periodic status even when no new listings
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] No new listings (checked {len(listings)} total, all previously seen)")
                
                # Periodic cleanup
                if time.time() - last_cleanup > cleanup_interval:
                    self._cleanup_old_listings()
                    last_cleanup = time.time()
                
                time.sleep(current_interval)
                
            except KeyboardInterrupt:
                print("\nBot stopped by user")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(current_interval)

if __name__ == "__main__":
    sniper = CSFloatSniper()
    sniper.run()
