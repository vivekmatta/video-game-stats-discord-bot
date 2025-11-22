import requests
import urllib.parse
import discord
import json
import os

# ============================
# BRAWL STARS API
# ============================
BRAWL_STARS_BASE = "https://api.brawlstars.com/v1"

def brawl_stars_api_get(path, api_key):
    """Helper to make GET requests to Brawl Stars API"""
    try:
        r = requests.get(
            f"{BRAWL_STARS_BASE}{path}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if r.status_code != 200:
            print("BRAWL STARS API ERROR:", r.status_code, r.text)
            return None
        return r.json()
    except Exception as e:
        print("BRAWL STARS REQUEST ERROR:", e)
        return None


def fetch_brawl_stars_stats(player_tag, api_key):
    """Fetch Brawl Stars player stats. Player tag must include #"""
    # URL encode the player tag (e.g., #Q8YYOJU becomes %23Q8YYOJU)
    encoded_tag = urllib.parse.quote(player_tag)
    return brawl_stars_api_get(f"/players/{encoded_tag}", api_key)


# ============================
# PLAYER REGISTRATION STORAGE
# ============================
REGISTRATION_FILE = "brawl_stars_registrations.json"

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
def build_brawl_stars_embed(data):
    """Build embed for Brawl Stars player stats"""
    
    # Basic info
    name = data.get("name", "Unknown")
    tag = data.get("tag", "")
    exp_level = data.get("expLevel", 0)
    trophies = data.get("trophies", 0)
    highest_trophies = data.get("highestTrophies", 0)
    
    # Victory stats
    solo_victories = data.get("soloVictories", 0)
    duo_victories = data.get("duoVictories", 0)
    trio_victories = data.get("3vs3Victories", 0)
    total_victories = solo_victories + duo_victories + trio_victories
    
    # Club info
    club_info = "No Club"
    if "club" in data and data["club"]:
        club_info = data["club"].get("name", "Unknown Club")
    
    # Brawlers
    brawlers = data.get("brawlers", [])
    total_brawlers = len(brawlers)
    
    # Get top 5 brawlers by trophies
    sorted_brawlers = sorted(brawlers, key=lambda x: x.get("trophies", 0), reverse=True)
    top_brawlers = sorted_brawlers[:5]
    
    # Calculate power level stats
    max_power_brawlers = len([b for b in brawlers if b.get("power", 0) == 11])
    
    # Create embed
    embed = discord.Embed(
        title=f"⭐ {name}",
        description=f"**Experience Level:** {exp_level}",
        color=discord.Color.gold()
    )
    
    # Trophy stats
    embed.add_field(
        name="🏆 TROPHIES",
        value=(
            f"**Current:** {trophies:,}\n"
            f"**Highest:** {highest_trophies:,}\n"
            f"**Per Brawler:** {trophies // total_brawlers if total_brawlers > 0 else 0}"
        ),
        inline=True
    )
    
    # Victory stats
    embed.add_field(
        name="🎯 VICTORIES",
        value=(
            f"**Total:** {total_victories:,}\n"
            f"**3v3:** {trio_victories:,}\n"
            f"**Duo:** {duo_victories:,}\n"
            f"**Solo:** {solo_victories:,}"
        ),
        inline=True
    )
    
    # Brawler collection
    embed.add_field(
        name="🎮 BRAWLERS",
        value=(
            f"**Unlocked:** {total_brawlers}\n"
            f"**Power 11:** {max_power_brawlers}\n"
            f"**Club:** {club_info}"
        ),
        inline=True
    )
    
    # Top 5 brawlers
    if top_brawlers:
        brawler_lines = []
        for i, brawler in enumerate(top_brawlers, 1):
            name_b = brawler.get("name", "Unknown").title()
            trophies_b = brawler.get("trophies", 0)
            rank = brawler.get("rank", 0)
            power = brawler.get("power", 0)
            
            # Add power level indicator
            power_indicator = "⚡" * min(power, 3) if power >= 9 else ""
            
            brawler_lines.append(
                f"**{i}. {name_b}** • {trophies_b:,} 🏆 • R{rank} • Lv{power} {power_indicator}"
            )
        
        embed.add_field(
            name="🌟 TOP 5 BRAWLERS",
            value="\n".join(brawler_lines),
            inline=False
        )
    
    # Add fun stats if available
    fun_stats = []
    
    # Count total star powers and gadgets
    total_star_powers = sum(len(b.get("starPowers", [])) for b in brawlers)
    total_gadgets = sum(len(b.get("gadgets", [])) for b in brawlers)
    total_gears = sum(len(b.get("gears", [])) for b in brawlers)
    
    if total_star_powers > 0 or total_gadgets > 0 or total_gears > 0:
        fun_stats.append(f"⭐ Star Powers: **{total_star_powers}**")
        fun_stats.append(f"🔧 Gadgets: **{total_gadgets}**")
        if total_gears > 0:
            fun_stats.append(f"⚙️ Gears: **{total_gears}**")
    
    if fun_stats:
        embed.add_field(
            name="📊 COLLECTION",
            value=" • ".join(fun_stats),
            inline=False
        )
    
    embed.set_footer(text=f"Player Tag: {tag}")
    
    return embed


def build_brawl_stars_comparison_embed(data1, data2):
    """Build a comparison embed for two Brawl Stars players"""
    
    # Extract player info
    name1 = data1.get("name", "Player 1")
    name2 = data2.get("name", "Player 2")
    
    # Trophy stats
    trophies1 = data1.get("trophies", 0)
    trophies2 = data2.get("trophies", 0)
    highest1 = data1.get("highestTrophies", 0)
    highest2 = data2.get("highestTrophies", 0)
    
    # Victory stats
    total_victories1 = data1.get("soloVictories", 0) + data1.get("duoVictories", 0) + data1.get("3vs3Victories", 0)
    total_victories2 = data2.get("soloVictories", 0) + data2.get("duoVictories", 0) + data2.get("3vs3Victories", 0)
    
    # Brawler stats
    brawlers1 = len(data1.get("brawlers", []))
    brawlers2 = len(data2.get("brawlers", []))
    
    # Calculate win probability (based on trophies 60%, victories 30%, brawlers 10%)
    trophy_score1 = (trophies1 / (trophies1 + trophies2) * 60) if (trophies1 + trophies2) > 0 else 30
    trophy_score2 = (trophies2 / (trophies1 + trophies2) * 60) if (trophies1 + trophies2) > 0 else 30
    
    victory_score1 = (total_victories1 / (total_victories1 + total_victories2) * 30) if (total_victories1 + total_victories2) > 0 else 15
    victory_score2 = (total_victories2 / (total_victories1 + total_victories2) * 30) if (total_victories1 + total_victories2) > 0 else 15
    
    brawler_score1 = (brawlers1 / (brawlers1 + brawlers2) * 10) if (brawlers1 + brawlers2) > 0 else 5
    brawler_score2 = (brawlers2 / (brawlers1 + brawlers2) * 10) if (brawlers1 + brawlers2) > 0 else 5
    
    total1 = trophy_score1 + victory_score1 + brawler_score1
    total2 = trophy_score2 + victory_score2 + brawler_score2
    
    p1_chance = round((total1 / (total1 + total2) * 100), 1)
    p2_chance = round((total2 / (total1 + total2) * 100), 1)
    
    # Determine winner
    if p1_chance > p2_chance:
        winner_text = f"⭐ **{name1}** has the advantage!"
        winner_color = discord.Color.gold()
    elif p2_chance > p1_chance:
        winner_text = f"⭐ **{name2}** has the advantage!"
        winner_color = discord.Color.blue()
    else:
        winner_text = "⚔️ **It's a perfect match!**"
        winner_color = discord.Color.purple()
    
    # Create embed
    embed = discord.Embed(
        title="⚔️ BRAWL STARS 1v1 PREDICTION ⚔️",
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
            f"**Highest:** {highest1:,} 🏆\n"
            f"**Victories:** {total_victories1:,}\n"
            f"**Brawlers:** {brawlers1}"
        ),
        inline=True
    )
    
    # VS Separator
    embed.add_field(
        name="⚔️",
        value=(
            f"**VS**\n"
            f"━━━━\n"
            f"**Brawl!**"
        ),
        inline=True
    )
    
    # Player 2 Stats
    embed.add_field(
        name=f"📊 {name2}",
        value=(
            f"**Trophies:** {trophies2:,} 🏆\n"
            f"**Highest:** {highest2:,} 🏆\n"
            f"**Victories:** {total_victories2:,}\n"
            f"**Brawlers:** {brawlers2}"
        ),
        inline=True
    )
    
    # Key advantages
    better_trophies = name1 if trophies1 > trophies2 else name2
    better_victories = name1 if total_victories1 > total_victories2 else name2
    more_brawlers = name1 if brawlers1 > brawlers2 else name2
    
    embed.add_field(
        name="📈 KEY ADVANTAGES",
        value=(
            f"**Higher Trophies:** {better_trophies}\n"
            f"**More Victories:** {better_victories}\n"
            f"**More Brawlers:** {more_brawlers}"
        ),
        inline=False
    )
    
    embed.set_footer(text="⚡ Prediction based on Trophies (60%), Victories (30%), Brawlers (10%)")
    
    return embed


# ============================
# TEST FUNCTION
# ============================
def test_brawl_stars_api(player_tag, api_key):
    """Test the Brawl Stars API and print JSON response"""
    print(f"\n{'='*60}")
    print(f"Testing Brawl Stars API for: {player_tag}")
    print(f"{'='*60}\n")
    
    data = fetch_brawl_stars_stats(player_tag, api_key)
    
    if data:
        print("✅ Success! Data retrieved.\n")
        print("📄 Full API Response:")
        print(json.dumps(data, indent=2))
        return True
    else:
        print("❌ Failed to retrieve data")
        return False