import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Import game modules
import clash_royale
import fortnite
import brawl_stars

# ============================
# LOAD ENVIRONMENTS
# ============================
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CLASH_ROYALE_API_KEY = os.getenv("CLASH_ROYALE_API_KEY")
FORTNITE_API_KEY = os.getenv("FORTNITE_API_KEY")
BRAWL_STARS_API_KEY = os.getenv("BRAWL_STARS_API_KEY")

if not DISCORD_TOKEN:
    print("❌ No DISCORD_TOKEN found.")
    exit(1)

if not CLASH_ROYALE_API_KEY:
    print("❌ No CLASH_ROYALE_API_KEY found.")
    exit(1)

if not FORTNITE_API_KEY:
    print("❌ No FORTNITE_API_KEY found.")
    exit(1)

if not BRAWL_STARS_API_KEY:
    print("❌ No BRAWL_STARS_API_KEY found.")
    exit(1)

# ============================
# BOT SETUP
# ============================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# ============================
# BRAWL STARS COMMANDS
# ============================
@bot.tree.command(name="brawlstars", description="Get Brawl Stars stats")
@app_commands.describe(
    player="Player tag (e.g., #Q8YYOJU) OR registered username"
)
async def brawlstars_cmd(interaction: discord.Interaction, player: str):
    await interaction.response.defer()
    
    # Check if it's a registered username first
    player_tag = brawl_stars.get_player_tag(player)
    
    # If not registered, treat as player tag
    if not player_tag:
        player_tag = player
        # Ensure the tag starts with #
        if not player_tag.startswith("#"):
            player_tag = "#" + player_tag
    
    data = brawl_stars.fetch_brawl_stars_stats(player_tag, BRAWL_STARS_API_KEY)
    
    if not data:
        await interaction.followup.send(
            f"❌ Could not find Brawl Stars player `{player_tag}`.\n"
            f"💡 Make sure the tag is correct or use `/bsregister` to save your tag!"
        )
        return
    
    embed = brawl_stars.build_brawl_stars_embed(data)
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="bsregister", description="Register your Brawl Stars player tag")
@app_commands.describe(
    username="Your username (used for quick lookups)",
    player_tag="Your Brawl Stars player tag (e.g., #Q8YYOJU)"
)
async def bs_register(interaction: discord.Interaction, username: str, player_tag: str):
    await interaction.response.defer()
    
    # Verify the player tag works
    if not player_tag.startswith("#"):
        player_tag = "#" + player_tag
    
    data = brawl_stars.fetch_brawl_stars_stats(player_tag, BRAWL_STARS_API_KEY)
    
    if not data:
        await interaction.followup.send(
            f"❌ Could not find player with tag `{player_tag}`.\n"
            f"Please make sure the tag is correct!"
        )
        return
    
    # Register the player
    saved_tag = brawl_stars.register_player(username, player_tag)
    player_name = data.get("name", username)
    
    await interaction.followup.send(
        f"✅ Successfully registered!\n"
        f"**Username:** {username}\n"
        f"**Player:** {player_name}\n"
        f"**Tag:** {saved_tag}\n\n"
        f"You can now use `/brawlstars player:{username}` instead of typing your tag!"
    )


@bot.tree.command(name="bsunregister", description="Remove your Brawl Stars registration")
@app_commands.describe(
    username="Your registered username"
)
async def bs_unregister(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    
    if brawl_stars.unregister_player(username):
        await interaction.followup.send(f"✅ Successfully removed registration for `{username}`")
    else:
        await interaction.followup.send(f"❌ No registration found for `{username}`")


# ============================
# CLASH ROYALE COMMANDS
# ============================
@bot.tree.command(name="clashroyale", description="Get Clash Royale stats")
@app_commands.describe(
    player="Player tag (e.g., #2ABC123) OR registered username"
)
async def clashroyale_cmd(interaction: discord.Interaction, player: str):
    await interaction.response.defer()
    
    # Check if it's a registered username first
    player_tag = clash_royale.get_player_tag(player)
    
    # If not registered, treat as player tag
    if not player_tag:
        player_tag = player
        # Ensure the tag starts with #
        if not player_tag.startswith("#"):
            player_tag = "#" + player_tag
    
    data = clash_royale.fetch_clash_royale_stats(player_tag, CLASH_ROYALE_API_KEY)
    
    if not data:
        await interaction.followup.send(
            f"❌ Could not find Clash Royale player `{player_tag}`.\n"
            f"💡 Make sure the tag is correct or use `/crregister` to save your tag!"
        )
        return
    
    embed = clash_royale.build_clash_royale_embed(data)
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="crregister", description="Register your Clash Royale player tag")
@app_commands.describe(
    username="Your username (used for quick lookups)",
    player_tag="Your Clash Royale player tag (e.g., #2ABC123)"
)
async def cr_register(interaction: discord.Interaction, username: str, player_tag: str):
    await interaction.response.defer()
    
    # Verify the player tag works
    if not player_tag.startswith("#"):
        player_tag = "#" + player_tag
    
    data = clash_royale.fetch_clash_royale_stats(player_tag, CLASH_ROYALE_API_KEY)
    
    if not data:
        await interaction.followup.send(
            f"❌ Could not find player with tag `{player_tag}`.\n"
            f"Please make sure the tag is correct!"
        )
        return
    
    # Register the player
    saved_tag = clash_royale.register_player(username, player_tag)
    player_name = data.get("name", username)
    
    await interaction.followup.send(
        f"✅ Successfully registered!\n"
        f"**Username:** {username}\n"
        f"**Player:** {player_name}\n"
        f"**Tag:** {saved_tag}\n\n"
        f"You can now use `/clashroyale player:{username}` instead of typing your tag!"
    )


@bot.tree.command(name="crunregister", description="Remove your Clash Royale registration")
@app_commands.describe(
    username="Your registered username"
)
async def cr_unregister(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    
    if clash_royale.unregister_player(username):
        await interaction.followup.send(f"✅ Successfully removed registration for `{username}`")
    else:
        await interaction.followup.send(f"❌ No registration found for `{username}`")


# ============================
# FORTNITE COMMANDS
# ============================
@bot.tree.command(name="fortnite", description="Get Fortnite stats for a username")
@app_commands.describe(
    username="The Fortnite username",
    platform="Choose your login platform"
)
@app_commands.choices(platform=[
    app_commands.Choice(name="🎮 Epic Games (PC/Mobile/Switch)", value="epic"),
    app_commands.Choice(name="🎮 PlayStation Network (PSN)", value="psn"),
    app_commands.Choice(name="🎮 Xbox Live (XBL)", value="xbl")
])
async def fortnite_cmd(
    interaction: discord.Interaction,
    username: str,
    platform: app_commands.Choice[str]
):
    await interaction.response.defer()
    
    account_type = platform.value
    platform_name = platform.name
    
    data = fortnite.fetch_fortnite_stats(username, account_type, FORTNITE_API_KEY)
    if not data:
        await interaction.followup.send(
            f"❌ Could not connect to Fortnite API. Please try again later."
        )
        return
    
    if data.get("status") == 403:
        await interaction.followup.send(
            f"🔒 The stats for `{username}` on **{platform_name}** are set to private.\n"
            f"💡 To make stats public: Fortnite Settings → Account and Privacy → Show on Career Leaderboard (ON)"
        )
        return
    
    if data.get("status") != 200:
        await interaction.followup.send(
            f"❌ Could not find Fortnite player `{username}` on **{platform_name}**."
        )
        return

    embed = fortnite.build_fortnite_embed(data)
    embed.set_author(name=f"Platform: {platform_name}")
    await interaction.followup.send(embed=embed)


# ============================
# UNIVERSAL COMPARE COMMAND
# ============================
@bot.tree.command(name="compare", description="Compare two players (choose game first)")
@app_commands.describe(
    game="Which game to compare",
    player1="First player",
    player2="Second player"
)
@app_commands.choices(game=[
    app_commands.Choice(name="👑 Clash Royale", value="clashroyale"),
    app_commands.Choice(name="⭐ Brawl Stars", value="brawlstars"),
    app_commands.Choice(name="🎮 Fortnite", value="fortnite")
])
async def compare_cmd(
    interaction: discord.Interaction,
    game: app_commands.Choice[str],
    player1: str,
    player2: str
):
    await interaction.response.defer()
    
    if game.value == "clashroyale":
        # Clash Royale comparison
        # Check for registered usernames
        tag1 = clash_royale.get_player_tag(player1)
        if not tag1:
            tag1 = player1
            if not tag1.startswith("#"):
                tag1 = "#" + tag1
        
        tag2 = clash_royale.get_player_tag(player2)
        if not tag2:
            tag2 = player2
            if not tag2.startswith("#"):
                tag2 = "#" + tag2
        
        # Fetch both players
        data1 = clash_royale.fetch_clash_royale_stats(tag1, CLASH_ROYALE_API_KEY)
        data2 = clash_royale.fetch_clash_royale_stats(tag2, CLASH_ROYALE_API_KEY)
        
        if not data1:
            await interaction.followup.send(f"❌ Could not find player: `{player1}`")
            return
        if not data2:
            await interaction.followup.send(f"❌ Could not find player: `{player2}`")
            return
        
        embed = clash_royale.build_clash_comparison_embed(data1, data2)
        await interaction.followup.send(embed=embed)
    
    elif game.value == "brawlstars":
        # Brawl Stars comparison
        # Check for registered usernames
        tag1 = brawl_stars.get_player_tag(player1)
        if not tag1:
            tag1 = player1
            if not tag1.startswith("#"):
                tag1 = "#" + tag1
        
        tag2 = brawl_stars.get_player_tag(player2)
        if not tag2:
            tag2 = player2
            if not tag2.startswith("#"):
                tag2 = "#" + tag2
        
        # Fetch both players
        data1 = brawl_stars.fetch_brawl_stars_stats(tag1, BRAWL_STARS_API_KEY)
        data2 = brawl_stars.fetch_brawl_stars_stats(tag2, BRAWL_STARS_API_KEY)
        
        if not data1:
            await interaction.followup.send(f"❌ Could not find player: `{player1}`")
            return
        if not data2:
            await interaction.followup.send(f"❌ Could not find player: `{player2}`")
            return
        
        embed = brawl_stars.build_brawl_stars_comparison_embed(data1, data2)
        await interaction.followup.send(embed=embed)
    
    elif game.value == "fortnite":
        # Show platform selection message
        await interaction.followup.send(
            f"❌ For Fortnite comparisons, please use `/fncompare` to specify platforms for each player."
        )


@bot.tree.command(name="fncompare", description="Compare two Fortnite players")
@app_commands.describe(
    player1="First player's username",
    platform1="First player's platform",
    player2="Second player's username",
    platform2="Second player's platform"
)
@app_commands.choices(
    platform1=[
        app_commands.Choice(name="🎮 Epic Games", value="epic"),
        app_commands.Choice(name="🎮 PlayStation (PSN)", value="psn"),
        app_commands.Choice(name="🎮 Xbox (XBL)", value="xbl")
    ],
    platform2=[
        app_commands.Choice(name="🎮 Epic Games", value="epic"),
        app_commands.Choice(name="🎮 PlayStation (PSN)", value="psn"),
        app_commands.Choice(name="🎮 Xbox (XBL)", value="xbl")
    ]
)
async def fn_compare(
    interaction: discord.Interaction,
    player1: str,
    platform1: app_commands.Choice[str],
    player2: str,
    platform2: app_commands.Choice[str]
):
    await interaction.response.defer()
    
    # Fetch both players' stats
    data1 = fortnite.fetch_fortnite_stats(player1, platform1.value, FORTNITE_API_KEY)
    data2 = fortnite.fetch_fortnite_stats(player2, platform2.value, FORTNITE_API_KEY)
    
    # Error handling for player 1
    if not data1 or data1.get("status") != 200:
        await interaction.followup.send(f"❌ Could not find Fortnite player `{player1}` on {platform1.name}")
        return
    
    # Error handling for player 2
    if not data2 or data2.get("status") != 200:
        await interaction.followup.send(f"❌ Could not find Fortnite player `{player2}` on {platform2.name}")
        return
    
    # Build and send comparison embed
    embed = fortnite.build_fortnite_comparison_embed(data1, data2, platform1.name, platform2.name)
    await interaction.followup.send(embed=embed)


# ============================
# READY EVENT
# ============================
@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Commands synced: {len(synced)}")
        print("\n📋 Available commands:")
        for cmd in synced:
            print(f"  /{cmd.name}")
        print()
    except Exception as e:
        print("❌ SYNC ERROR:", e)


# ============================
# RUN BOT
# ============================
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)