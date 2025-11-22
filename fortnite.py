import requests
import discord
import json

# ============================
# FORTNITE API
# ============================
FORTNITE_BASE = "https://fortnite-api.com/v2"

def fortnite_api_get(path, params, api_key):
    """Helper to make GET requests to Fortnite API"""
    try:
        r = requests.get(
            f"{FORTNITE_BASE}{path}",
            headers={"Authorization": api_key},
            params=params,
            timeout=10
        )
        if r.status_code != 200:
            print("FORTNITE API ERROR:", r.status_code, r.text)
            return None
        return r.json()
    except Exception as e:
        print("FORTNITE REQUEST ERROR:", e)
        return None


def fetch_fortnite_stats(username, account_type, api_key):
    """Fetch Fortnite stats for a player."""
    return fortnite_api_get(
        "/stats/br/v2",
        params={"name": username, "accountType": account_type},
        api_key=api_key
    )


# ============================
# EMBED BUILDERS
# ============================
def build_fortnite_embed(data):
    """Build embed for Fortnite player stats"""
    account = data["data"]["account"]
    stats = data["data"]["stats"]
    battle_pass = data["data"].get("battlePass", {})
    
    # Get overall stats
    overall = stats["all"]["overall"]
    
    # Calculate stats
    matches = overall.get("matches", 0)
    wins = overall.get("wins", 0)
    kills = overall.get("kills", 0)
    deaths = overall.get("deaths", 0)
    kd = overall.get("kd", 0)
    winrate = overall.get("winRate", 0)
    top10 = overall.get("top10", 0)
    top5 = overall.get("top5", 0)
    top3 = overall.get("top3", 0)
    
    # Get mode-specific stats
    solo = stats["all"].get("solo", {})
    duo = stats["all"].get("duo", {})
    squad = stats["all"].get("squad", {})
    ltm = stats["all"].get("ltm", {})
    
    embed = discord.Embed(
        title=f"🎮 {account['name']} — Fortnite Battle Royale",
        color=discord.Color.purple(),
        description=f"Battle Pass Level: **{battle_pass.get('level', 'N/A')}**" if battle_pass else None
    )
    
    embed.add_field(
        name="📊 OVERALL STATS",
        value=(
            f"**Matches:** {matches:,}\n"
            f"**Wins:** {wins:,} ({winrate:.1f}%)\n"
            f"**Kills:** {kills:,}\n"
            f"**K/D Ratio:** {kd:.2f}\n"
            f"**Top 3/5/10:** {top3}/{top5}/{top10}"
        ),
        inline=False
    )
    
    # Solo stats
    if solo and solo.get("matches", 0) > 0:
        embed.add_field(
            name="🎯 SOLO",
            value=(
                f"Matches: **{solo.get('matches', 0):,}**\n"
                f"Wins: **{solo.get('wins', 0):,}**\n"
                f"K/D: **{solo.get('kd', 0):.2f}**\n"
                f"WR: **{solo.get('winRate', 0):.1f}%**"
            ),
            inline=True
        )
    
    # Duo stats
    if duo and duo.get("matches", 0) > 0:
        embed.add_field(
            name="👥 DUO",
            value=(
                f"Matches: **{duo.get('matches', 0):,}**\n"
                f"Wins: **{duo.get('wins', 0):,}**\n"
                f"K/D: **{duo.get('kd', 0):.2f}**\n"
                f"WR: **{duo.get('winRate', 0):.1f}%**"
            ),
            inline=True
        )
    
    # Squad stats
    if squad and squad.get("matches", 0) > 0:
        embed.add_field(
            name="👨‍👩‍👧‍👦 SQUAD",
            value=(
                f"Matches: **{squad.get('matches', 0):,}**\n"
                f"Wins: **{squad.get('wins', 0):,}**\n"
                f"K/D: **{squad.get('kd', 0):.2f}**\n"
                f"WR: **{squad.get('winRate', 0):.1f}%**"
            ),
            inline=True
        )
    
    # LTM stats (if significant)
    if ltm and ltm.get("matches", 0) > 100:
        embed.add_field(
            name="🎪 LIMITED TIME MODES",
            value=(
                f"Matches: **{ltm.get('matches', 0):,}**\n"
                f"Wins: **{ltm.get('wins', 0):,}**\n"
                f"K/D: **{ltm.get('kd', 0):.2f}**"
            ),
            inline=True
        )
    
    embed.set_footer(text=f"Account ID: {account['id']}")
    
    return embed


def calculate_win_probability(player1_stats, player2_stats):
    """Calculate win probability based on multiple factors"""
    
    # Extract key stats
    p1_kd = player1_stats.get("kd", 0)
    p1_winrate = player1_stats.get("winRate", 0)
    p1_kills_per_match = player1_stats.get("killsPerMatch", 0)
    p1_matches = player1_stats.get("matches", 0)
    
    p2_kd = player2_stats.get("kd", 0)
    p2_winrate = player2_stats.get("winRate", 0)
    p2_kills_per_match = player2_stats.get("killsPerMatch", 0)
    p2_matches = player2_stats.get("matches", 0)
    
    # Weighted scoring system
    # K/D is most important (40%), Win Rate (30%), Kills per Match (20%), Experience (10%)
    
    # K/D Score (40%)
    kd_total = p1_kd + p2_kd
    p1_kd_score = (p1_kd / kd_total * 40) if kd_total > 0 else 20
    p2_kd_score = (p2_kd / kd_total * 40) if kd_total > 0 else 20
    
    # Win Rate Score (30%)
    wr_total = p1_winrate + p2_winrate
    p1_wr_score = (p1_winrate / wr_total * 30) if wr_total > 0 else 15
    p2_wr_score = (p2_winrate / wr_total * 30) if wr_total > 0 else 15
    
    # Kills per Match Score (20%)
    kpm_total = p1_kills_per_match + p2_kills_per_match
    p1_kpm_score = (p1_kills_per_match / kpm_total * 20) if kpm_total > 0 else 10
    p2_kpm_score = (p2_kills_per_match / kpm_total * 20) if kpm_total > 0 else 10
    
    # Experience Score (10%) - more matches = slight advantage
    exp_total = p1_matches + p2_matches
    p1_exp_score = (p1_matches / exp_total * 10) if exp_total > 0 else 5
    p2_exp_score = (p2_matches / exp_total * 10) if exp_total > 0 else 5
    
    # Total scores
    p1_total = p1_kd_score + p1_wr_score + p1_kpm_score + p1_exp_score
    p2_total = p2_kd_score + p2_wr_score + p2_kpm_score + p2_exp_score
    
    # Convert to percentages
    total = p1_total + p2_total
    p1_win_chance = (p1_total / total * 100) if total > 0 else 50
    p2_win_chance = (p2_total / total * 100) if total > 0 else 50
    
    return round(p1_win_chance, 1), round(p2_win_chance, 1)


def build_fortnite_comparison_embed(data1, data2, platform1_name, platform2_name):
    """Build a comparison embed for two Fortnite players"""
    
    account1 = data1["data"]["account"]
    account2 = data2["data"]["account"]
    
    stats1 = data1["data"]["stats"]["all"]["overall"]
    stats2 = data2["data"]["stats"]["all"]["overall"]
    
    # Calculate win probabilities
    p1_chance, p2_chance = calculate_win_probability(stats1, stats2)
    
    # Determine winner
    if p1_chance > p2_chance:
        winner_text = f"🏆 **{account1['name']}** has the advantage!"
        winner_color = discord.Color.green()
    elif p2_chance > p1_chance:
        winner_text = f"🏆 **{account2['name']}** has the advantage!"
        winner_color = discord.Color.blue()
    else:
        winner_text = "⚔️ **It's a perfect match!**"
        winner_color = discord.Color.gold()
    
    # Create embed
    embed = discord.Embed(
        title="⚔️ FORTNITE 1v1 PREDICTION ⚔️",
        description=(
            f"{winner_text}\n\n"
            f"**{account1['name']}** — {p1_chance}% chance to win\n"
            f"**{account2['name']}** — {p2_chance}% chance to win\n"
            f"```\n"
            f"{account1['name'][:12]:12} [{'█' * int(p1_chance/5)}{' ' * (20-int(p1_chance/5))}] {p1_chance}%\n"
            f"{account2['name'][:12]:12} [{'█' * int(p2_chance/5)}{' ' * (20-int(p2_chance/5))}] {p2_chance}%\n"
            f"```"
        ),
        color=winner_color
    )
    
    # Player 1 Stats
    embed.add_field(
        name=f"📊 {account1['name']} ({platform1_name})",
        value=(
            f"**Matches:** {stats1.get('matches', 0):,}\n"
            f"**Wins:** {stats1.get('wins', 0):,}\n"
            f"**Win Rate:** {stats1.get('winRate', 0):.1f}%\n"
            f"**K/D Ratio:** {stats1.get('kd', 0):.2f}\n"
            f"**Kills/Match:** {stats1.get('killsPerMatch', 0):.2f}\n"
            f"**Total Kills:** {stats1.get('kills', 0):,}"
        ),
        inline=True
    )
    
    # VS Separator
    embed.add_field(
        name="⚔️",
        value=(
            f"**VS**\n"
            f"━━━━\n"
            f"**Diff**\n"
            f"━━━━\n"
            f"**Analysis**"
        ),
        inline=True
    )
    
    # Player 2 Stats
    embed.add_field(
        name=f"📊 {account2['name']} ({platform2_name})",
        value=(
            f"**Matches:** {stats2.get('matches', 0):,}\n"
            f"**Wins:** {stats2.get('wins', 0):,}\n"
            f"**Win Rate:** {stats2.get('winRate', 0):.1f}%\n"
            f"**K/D Ratio:** {stats2.get('kd', 0):.2f}\n"
            f"**Kills/Match:** {stats2.get('killsPerMatch', 0):.2f}\n"
            f"**Total Kills:** {stats2.get('kills', 0):,}"
        ),
        inline=True
    )
    
    # Stat comparisons
    kd_diff = abs(stats1.get('kd', 0) - stats2.get('kd', 0))
    wr_diff = abs(stats1.get('winRate', 0) - stats2.get('winRate', 0))
    
    # Determine who's better at what
    better_kd = account1['name'] if stats1.get('kd', 0) > stats2.get('kd', 0) else account2['name']
    better_wr = account1['name'] if stats1.get('winRate', 0) > stats2.get('winRate', 0) else account2['name']
    better_kpm = account1['name'] if stats1.get('killsPerMatch', 0) > stats2.get('killsPerMatch', 0) else account2['name']
    
    embed.add_field(
        name="📈 KEY DIFFERENTIATORS",
        value=(
            f"**K/D Leader:** {better_kd} (+{kd_diff:.2f})\n"
            f"**Win Rate Leader:** {better_wr} (+{wr_diff:.1f}%)\n"
            f"**Aggression Leader:** {better_kpm}"
        ),
        inline=False
    )
    
    # Mode breakdown
    p1_solo = data1["data"]["stats"]["all"].get("solo", {})
    p2_solo = data2["data"]["stats"]["all"].get("solo", {})
    p1_duo = data1["data"]["stats"]["all"].get("duo", {})
    p2_duo = data2["data"]["stats"]["all"].get("duo", {})
    p1_squad = data1["data"]["stats"]["all"].get("squad", {})
    p2_squad = data2["data"]["stats"]["all"].get("squad", {})
    
    mode_comparison = ""
    
    if p1_solo.get("matches", 0) > 0 and p2_solo.get("matches", 0) > 0:
        solo_better = account1['name'] if p1_solo.get('kd', 0) > p2_solo.get('kd', 0) else account2['name']
        mode_comparison += f"**Solo:** {solo_better} ({max(p1_solo.get('kd', 0), p2_solo.get('kd', 0)):.2f} K/D)\n"
    
    if p1_duo.get("matches", 0) > 0 and p2_duo.get("matches", 0) > 0:
        duo_better = account1['name'] if p1_duo.get('kd', 0) > p2_duo.get('kd', 0) else account2['name']
        mode_comparison += f"**Duo:** {duo_better} ({max(p1_duo.get('kd', 0), p2_duo.get('kd', 0)):.2f} K/D)\n"
    
    if p1_squad.get("matches", 0) > 0 and p2_squad.get("matches", 0) > 0:
        squad_better = account1['name'] if p1_squad.get('kd', 0) > p2_squad.get('kd', 0) else account2['name']
        mode_comparison += f"**Squad:** {squad_better} ({max(p1_squad.get('kd', 0), p2_squad.get('kd', 0)):.2f} K/D)\n"
    
    if mode_comparison:
        embed.add_field(
            name="🎮 MODE DOMINANCE",
            value=mode_comparison.strip(),
            inline=False
        )
    
    embed.set_footer(text="⚡ Prediction based on K/D (40%), Win Rate (30%), Kills/Match (20%), Experience (10%)")
    
    return embed


# ============================
# TEST FUNCTION
# ============================
def test_fortnite_api(username, account_type, api_key):
    """Test the Fortnite API and print JSON response"""
    print(f"\n{'='*60}")
    print(f"Testing Fortnite API for: {username} ({account_type})")
    print(f"{'='*60}\n")
    
    data = fetch_fortnite_stats(username, account_type, api_key)
    
    if data and data.get("status") == 200:
        print("✅ Success! Data retrieved.\n")
        print("📄 Full API Response:")
        print(json.dumps(data, indent=2))
        return True
    elif data and data.get("status") == 403:
        print("🔒 Player stats are private")
        return False
    else:
        print("❌ Failed to retrieve data")
        return False