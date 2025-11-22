# 🎮 Multi-Game Stats Discord Bot

A modular Discord bot for Clash Royale and Fortnite stats with player registration and comparison features!

## 📁 Project Structure

```
VideoGameStats/
├── main_bot.py                          # Main bot file - run this!
├── clash_royale.py                      # Clash Royale module
├── fortnite.py                          # Fortnite module
├── test_apis.py                         # Interactive API testing
├── clash_royale_registrations.json      # Auto-generated player registrations
├── .env                                 # Your API keys (DON'T COMMIT!)
└── README.md                            # This file
```

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate     # Windows

# Install packages
pip install discord.py requests python-dotenv
```

### 2. Configure API Keys

Create a `.env` file:

```env
DISCORD_TOKEN=your_discord_bot_token
CLASH_ROYALE_API_KEY=your_clash_royale_key
FORTNITE_API_KEY=ea2d6b3f-dc35-4dfe-a383-131aff8ab7cf
```

### 3. Fix Clash Royale API Key Issue

The "Invalid IP address" error means you need to whitelist your IP:

**Option A: Allow All IPs (Easiest)**
- In the Clash Royale API Key creation form
- Under "ALLOWED IP ADDRESSES", enter: `0.0.0.0/0`
- This allows requests from any IP address

**Option B: Whitelist Your Specific IP (More Secure)**
1. Find your public IP: Go to https://whatismyipaddress.com/
2. Copy your IPv4 address (e.g., `123.456.789.012`)
3. In the API Key form, enter your IP address
4. Click "Create Key"

**Note:** If you're on a dynamic IP (changes frequently), use Option A or you'll need to update the key regularly.

### 4. Run the Bot

```bash
python main_bot.py
```

## 🧪 Testing APIs

Before running the bot, test your API keys:

```bash
python test_apis.py
```

This interactive tool lets you:
- Test Clash Royale API with any player tag
- Test Fortnite API with any username
- View full JSON responses to debug issues

## 📋 Bot Commands

### Clash Royale Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/clashroyale` | Get player stats | `/clashroyale player:#2ABC123` |
| `/crregister` | Register your player tag | `/crregister username:john player_tag:#2ABC123` |
| `/crunregister` | Remove registration | `/crunregister username:john` |

**After registering**, you can use your username instead of typing your tag every time:
```
/clashroyale player:john  # Instead of /clashroyale player:#2ABC123
```

### Fortnite Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/fortnite` | Get player stats | `/fortnite username:Ninja platform:Epic` |
| `/fncompare` | Compare two players | `/fncompare player1:Alice platform1:Epic player2:Bob platform2:PSN` |

### Universal Compare

| Command | Description | Example |
|---------|-------------|---------|
| `/compare` | Compare players (any game) | `/compare game:Clash Royale player1:#ABC player2:#XYZ` |

**Note:** For Fortnite, use `/fncompare` to specify platforms.

## 🎯 Features

### ✅ Modular Design
- Each game has its own module (`clash_royale.py`, `fortnite.py`)
- Easy to add new games
- Cleaner code organization

### ✅ Player Registration (Clash Royale)
- Save your player tag once
- Use your username for all future lookups
- Stored in `clash_royale_registrations.json`

### ✅ Comparison System
- Compare two Clash Royale players
- Compare two Fortnite players
- AI-powered win probability predictions
- Detailed stat breakdowns

### ✅ Testing Tools
- Interactive API tester (`test_apis.py`)
- View full JSON responses
- Debug API issues easily

## 🔧 Troubleshooting

### "Invalid IP address" Error (Clash Royale)
- Solution: Use `0.0.0.0/0` in the IP allowlist
- Or add your specific public IP from whatismyipaddress.com

### "403 Forbidden" Error (Fortnite)
- Player has private stats
- Ask them to enable: Settings → Account and Privacy → Show on Career Leaderboard

### Bot Not Responding
1. Check if bot is online: Look for "✅ Bot online" message
2. Check if commands synced: Should see "✅ Commands synced: 6"
3. Make sure bot has proper Discord permissions

### Registration Not Working
- The bot creates `clash_royale_registrations.json` automatically
- Make sure the bot has write permissions in the folder
- Check the file exists after first registration

## 📊 Example Usage

### Register Once, Use Forever (Clash Royale)
```
User: /crregister username:john player_tag:#2ABC123
Bot:  ✅ Successfully registered!
      Username: john
      Player: John's Account
      Tag: #2ABC123

User: /clashroyale player:john
Bot:  [Shows full stats]

User: /compare game:Clash Royale player1:john player2:#XYZ999
Bot:  [Shows comparison with win prediction]
```

### Compare Fortnite Players
```
User: /fncompare player1:Ninja platform1:Epic player2:Tfue platform2:Epic
Bot:  [Shows 1v1 prediction with detailed stats]
```

## 🎨 Customization

### Adding a New Game

1. Create `new_game.py` module:
```python
def fetch_stats(player_id, api_key):
    # Your API logic
    pass

def build_embed(data):
    # Create Discord embed
    pass
```

2. Import in `main_bot.py`:
```python
import new_game
```

3. Add commands following the same pattern

### Changing Prediction Weights

Edit the weight values in comparison functions:
- **Clash Royale**: `clash_royale.py` → `build_clash_comparison_embed()`
- **Fortnite**: `fortnite.py` → `calculate_win_probability()`

## 📝 Notes

- Player registrations are saved locally in JSON
- Bot requires `Send Messages` and `Embed Links` permissions
- Clash Royale tags must include the `#` symbol
- Fortnite requires platform specification

## 🆘 Support

If you encounter issues:
1. Run `python test_apis.py` to test API connectivity
2. Check your `.env` file has all keys
3. Verify your Clash Royale IP whitelist settings
4. Make sure virtual environment is activated

## 📄 License

Feel free to use and modify for your own Discord servers!