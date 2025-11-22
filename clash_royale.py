import requests
import urllib.parse
import discord
import json
import os

# ============================
# CLASH ROYALE API
# ============================
CLASH_ROYALE_BASE = "https://api.clashroyale.com/v1"

def clash_royale_api_get(path, api_key):
    """Helper to make GET requests to Clash Royale API"""
    try:
        r = requests.get(
            f"{CLASH_ROYALE_BASE}{path}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if r.status_code != 200:
            print("CLASH ROYALE API ERROR:", r.status_code, r.text)
            return None
        return r.json()
    except Exception as e:
        print("CLASH ROYALE REQUEST ERROR:", e)
        return None


def fetch_clash_royale_stats(player_tag, api_key):
    """Fetch Clash Royale player stats. Player tag must include #"""
    # URL encode the player tag (e.g., #2ABC becomes %232ABC)
    encoded_tag = urllib.parse.quote(player_tag)
    return clash_royale_api_get(f"/players/{encoded_tag}", api_key)


# ============================
# PLAYER REGISTRATION STORAGE
# ============================
REGISTRATION_FILE = "clash_royale_registrations.json"

def load_registrations():
    """Load registered players from file"""
    if os.path.exists(REGISTRATION_FILE):
        try:
            with open(REGISTRATION_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_registrations(registrations):
    """Save registered players to file"""
    with open(REGISTRATION_FILE, 'w') as f:
        json.dump(registrations, f, indent=2)

def register_player(username, player_tag):
    """Register a username with their player tag"""
    registrations = load_registrations()
    # Ensure tag starts with #
    if not player_tag.startswith("#"):
        player_tag = "#" + player_tag
    registrations[username.lower()] = player_tag
    save_registrations(registrations)
    return player_tag

def get_player_tag(username):
    """Get player tag from registered username"""
    registrations = load_registrations()
    return registrations.get(username.lower())

def unregister_player(username):
    """Remove a registered player"""
    registrations = load_registrations()
    if username.lower() in registrations:
        del registrations[username.lower()]
        save_registrations(registrations)
        return True
    return False


# ============================
# EMBED BUILDERS
# ============================
def build_clash_royale_embed(data):
    """Build embed for Clash Royale player stats"""
    
    # Basic info
    name = data.get("name", "Unknown")
    tag = data.get("tag", "")
    exp_level = data.get("expLevel", 0)
    trophies = data.get("trophies", 0)
    best_trophies = data.get("bestTrophies", 0)
    
    # Battle stats
    wins = data.get("wins", 0)
    losses = data.get("losses", 0)
    battle_count = data.get("battleCount", 0)
    three_crown_wins = data.get("threeCrownWins", 0)
    
    # Calculate win rate
    win_rate = (wins / battle_count * 100) if battle_count > 0 else 0
    
    # Clan info
    clan_info = "No Clan"
    clan_role = ""
    if "clan" in data and data["clan"]:
        clan_info = data["clan"].get("name", "Unknown Clan")
        clan_role = data["clan"].get("role", "member").title()
    
    # Arena
    arena_name = "Unknown Arena"
    if "arena" in data and data["arena"]:
        arena_name = data["arena"].get("name", "Unknown Arena")
    
    # Donations
    donations = data.get("donations", 0)
    donations_received = data.get("donationsReceived", 0)
    total_donations = data.get("totalDonations", 0)
    
    # League statistics
    current_season_trophies = None
    previous_season_trophies = None
    best_season_trophies = None
    
    if "leagueStatistics" in data and data["leagueStatistics"]:
        league_stats = data["leagueStatistics"]
        if "currentSeason" in league_stats and league_stats["currentSeason"]:
            current_season_trophies = league_stats["currentSeason"].get("trophies")
        if "previousSeason" in league_stats and league_stats["previousSeason"]:
            previous_season_trophies = league_stats["previousSeason"].get("trophies")
        if "bestSeason" in league_stats and league_stats["bestSeason"]:
            best_season_trophies = league_stats["bestSeason"].get("trophies")
    
    # Create embed
    embed = discord.Embed(
        title=f"👑 {name}",
        description=f"**{arena_name}** • Level {exp_level}",
        color=discord.Color.orange()
    )
    
    # Trophy info
    trophy_text = f"**Current:** {trophies:,} 🏆\n**Best:** {best_trophies:,} 🏆"
    if current_season_trophies:
        trophy_text += f"\n**Season:** {current_season_trophies:,} 🏆"
    
    embed.add_field(
        name="🏆 TROPHIES",
        value=trophy_text,
        inline=True
    )
    
    # Battle stats
    embed.add_field(
        name="⚔️ BATTLES",
        value=(
            f"**Total:** {battle_count:,}\n"
            f"**Wins:** {wins:,}\n"
            f"**Losses:** {losses:,}\n"
            f"**Win Rate:** {win_rate:.1f}%\n"
            f"**3-Crowns:** {three_crown_wins:,}"
        ),
        inline=True
    )
    
    # Clan & donations
    embed.add_field(
        name="🏰 CLAN & CONTRIBUTIONS",
        value=(
            f"**Clan:** {clan_info}\n"
            f"**Role:** {clan_role if clan_role else 'No Clan'}\n"
            f"**Donated:** {donations:,} (Total: {total_donations:,})\n"
            f"**Received:** {donations_received:,}"
        ),
        inline=True
    )
    
    # Add current deck if available
    if "currentDeck" in data and data["currentDeck"]:
        deck_cards = []
        for card in data["currentDeck"][:8]:
            card_name = card.get("name", "Unknown")
            card_level = card.get("level", 0)
            evolution_level = card.get("evolutionLevel", 0)
            
            # Add evolution indicator if evolved
            if evolution_level > 0:
                deck_cards.append(f"{card_name} Lv{card_level}⭐")
            else:
                deck_cards.append(f"{card_name} Lv{card_level}")
        
        if deck_cards:
            # Split into two rows for better formatting
            deck_line1 = " • ".join(deck_cards[:4])
            deck_line2 = " • ".join(deck_cards[4:8]) if len(deck_cards) > 4 else ""
            
            deck_display = deck_line1
            if deck_line2:
                deck_display += "\n" + deck_line2
            
            embed.add_field(
                name="🃏 CURRENT DECK",
                value=deck_display,
                inline=False
            )
    
    # Add badges if player has notable achievements
    if "badges" in data and data["badges"]:
        notable_badges = []
        for badge in data["badges"][:3]:  # Show top 3 badges
            badge_name = badge.get("name", "").replace("Mastery", "").strip()
            badge_level = badge.get("level", 0)
            if badge_level > 0:
                notable_badges.append(f"{badge_name} ⭐{badge_level}")
        
        if notable_badges:
            embed.add_field(
                name="🏅 TOP BADGES",
                value=" • ".join(notable_badges),
                inline=False
            )
    
    embed.set_footer(text=f"Player Tag: {tag}")
    
    return embed


def build_clash_comparison_embed(data1, data2):
    """Build a comparison embed for two Clash Royale players"""
    
    # Extract player info
    name1 = data1.get("name", "Player 1")
    name2 = data2.get("name", "Player 2")
    
    # Battle stats
    wins1 = data1.get("wins", 0)
    wins2 = data2.get("wins", 0)
    losses1 = data1.get("losses", 0)
    losses2 = data2.get("losses", 0)
    battles1 = data1.get("battleCount", 0)
    battles2 = data2.get("battleCount", 0)
    
    # Calculate win rates
    wr1 = (wins1 / battles1 * 100) if battles1 > 0 else 0
    wr2 = (wins2 / battles2 * 100) if battles2 > 0 else 0
    
    # Trophies
    trophies1 = data1.get("trophies", 0)
    trophies2 = data2.get("trophies", 0)
    best1 = data1.get("bestTrophies", 0)
    best2 = data2.get("bestTrophies", 0)
    
    # 3-crown wins
    three_crown1 = data1.get("threeCrownWins", 0)
    three_crown2 = data2.get("threeCrownWins", 0)
    
    # Calculate win probability (based on trophies 50%, win rate 30%, 3-crown 20%)
    trophy_score1 = (trophies1 / (trophies1 + trophies2) * 50) if (trophies1 + trophies2) > 0 else 25
    trophy_score2 = (trophies2 / (trophies1 + trophies2) * 50) if (trophies1 + trophies2) > 0 else 25
    
    wr_score1 = (wr1 / (wr1 + wr2) * 30) if (wr1 + wr2) > 0 else 15
    wr_score2 = (wr2 / (wr1 + wr2) * 30) if (wr1 + wr2) > 0 else 15
    
    tc_score1 = (three_crown1 / (three_crown1 + three_crown2) * 20) if (three_crown1 + three_crown2) > 0 else 10
    tc_score2 = (three_crown2 / (three_crown1 + three_crown2) * 20) if (three_crown1 + three_crown2) > 0 else 10
    
    total1 = trophy_score1 + wr_score1 + tc_score1
    total2 = trophy_score2 + wr_score2 + tc_score2
    
    p1_chance = round((total1 / (total1 + total2) * 100), 1)
    p2_chance = round((total2 / (total1 + total2) * 100), 1)
    
    # Determine winner
    if p1_chance > p2_chance:
        winner_text = f"👑 **{name1}** has the advantage!"
        winner_color = discord.Color.orange()
    elif p2_chance > p1_chance:
        winner_text = f"👑 **{name2}** has the advantage!"
        winner_color = discord.Color.blue()
    else:
        winner_text = "⚔️ **It's a perfect match!**"
        winner_color = discord.Color.gold()
    
    # Create embed
    embed = discord.Embed(
        title="⚔️ CLASH ROYALE 1v1 PREDICTION ⚔️",
        description=(
            f"{winner_text}\n\n"
            f"**{name1}** — {p1_chance}% chance to win\n"
            f"**{name2}** — {p2_chance}% chance to win\n"
            f"```\n"
            f"{name1[:12]:12} [{'█' * int(p1_chance/5)}{' ' * (20-int(p1_chance/5))}] {p1_chance}%\n"
            f"{name2[:12]:12} [{'█' * int(p2_chance/5)}{' ' * (20-int(p2_chance/5))}] {p2_chance}%\n"
            f"```"
        ),
        color=winner_color
    )
    
    # Player 1 Stats
    embed.add_field(
        name=f"📊 {name1}",
        value=(
            f"**Trophies:** {trophies1:,} 🏆\n"
            f"**Best:** {best1:,} 🏆\n"
            f"**Battles:** {battles1:,}\n"
            f"**Win Rate:** {wr1:.1f}%\n"
            f"**3-Crowns:** {three_crown1:,}\n"
            f"**Wins:** {wins1:,}"
        ),
        inline=True
    )
    
    # VS Separator
    embed.add_field(
        name="⚔️",
        value=(
            f"**VS**\n"
            f"━━━━\n"
            f"**Battle!**"
        ),
        inline=True
    )
    
    # Player 2 Stats
    embed.add_field(
        name=f"📊 {name2}",
        value=(
            f"**Trophies:** {trophies2:,} 🏆\n"
            f"**Best:** {best2:,} 🏆\n"
            f"**Battles:** {battles2:,}\n"
            f"**Win Rate:** {wr2:.1f}%\n"
            f"**3-Crowns:** {three_crown2:,}\n"
            f"**Wins:** {wins2:,}"
        ),
        inline=True
    )
    
    # Key differentiators
    better_trophies = name1 if trophies1 > trophies2 else name2
    better_wr = name1 if wr1 > wr2 else name2
    better_3crown = name1 if three_crown1 > three_crown2 else name2
    
    embed.add_field(
        name="📈 KEY ADVANTAGES",
        value=(
            f"**Higher Trophies:** {better_trophies}\n"
            f"**Better Win Rate:** {better_wr}\n"
            f"**More 3-Crowns:** {better_3crown}"
        ),
        inline=False
    )
    
    embed.set_footer(text="⚡ Prediction based on Trophies (50%), Win Rate (30%), 3-Crowns (20%)")
    
    return embed


# ============================
# TEST FUNCTION
# ============================
def test_clash_royale_api(player_tag, api_key):
    """Test the Clash Royale API and print JSON response"""
    print(f"\n{'='*60}")
    print(f"Testing Clash Royale API for: {player_tag}")
    print(f"{'='*60}\n")
    
    data = fetch_clash_royale_stats(player_tag, api_key)
    
    if data:
        print("✅ Success! Data retrieved.\n")
        print("📄 Full API Response:")
        print(json.dumps(data, indent=2))
        return True
    else:
        print("❌ Failed to retrieve data")
        return False