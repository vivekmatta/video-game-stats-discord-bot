import os
from dotenv import load_dotenv
import clash_royale
import fortnite
import json
from datetime import datetime
import requests
import urllib.parse

# Load environment variables
load_dotenv()
CLASH_ROYALE_API_KEY = os.getenv("CLASH_ROYALE_API_KEY")
FORTNITE_API_KEY = os.getenv("FORTNITE_API_KEY")
BRAWL_STARS_API_KEY = os.getenv("BRAWL_STARS_API_KEY")

def save_json_to_file(data, game_name, player_identifier):
    """Save API response to a JSON file"""
    # Create a timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create a safe filename
    safe_identifier = player_identifier.replace("#", "").replace("/", "_").replace("\\", "_")
    filename = f"{game_name}_{safe_identifier}_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved to: {filename}")
        print(f"📁 Location: {os.path.abspath(filename)}")
        return True
    except Exception as e:
        print(f"\n❌ Error saving file: {e}")
        return False


def test_brawl_stars_api(player_tag):
    """Test the Brawl Stars API and print JSON response"""
    print(f"\n{'='*60}")
    print(f"Testing Brawl Stars API for: {player_tag}")
    print(f"{'='*60}\n")
    
    if not BRAWL_STARS_API_KEY:
        print("❌ No BRAWL_STARS_API_KEY found in .env file")
        return False
    
    try:
        # Ensure tag starts with #
        if not player_tag.startswith("#"):
            player_tag = "#" + player_tag
        
        # URL encode the player tag
        encoded_tag = urllib.parse.quote(player_tag)
        url = f"https://api.brawlstars.com/v1/players/{encoded_tag}"
        
        headers = {
            "Authorization": f"Bearer {BRAWL_STARS_API_KEY}",
            "Accept": "application/json"
        }
        
        print(f"📡 Making request to: {url}")
        print(f"🔑 Using API Key: {BRAWL_STARS_API_KEY[:20]}...\n")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Data retrieved.\n")
            
            # Pretty print the JSON response
            print("📄 Full API Response:")
            print(json.dumps(data, indent=2))
            
            # Extract and display key stats
            print(f"\n{'='*60}")
            print("📈 EXTRACTED STATS SUMMARY")
            print(f"{'='*60}\n")
            
            print(f"👤 Name: {data.get('name', 'Unknown')}")
            print(f"🆔 Tag: {data.get('tag', 'Unknown')}")
            print(f"🏆 Trophies: {data.get('trophies', 0):,}")
            print(f"⭐ Best Trophies: {data.get('highestTrophies', 0):,}")
            print(f"📊 Experience Level: {data.get('expLevel', 0)}")
            
            if 'club' in data and data['club']:
                print(f"🏰 Club: {data['club'].get('name', 'Unknown')}")
            
            if 'brawlers' in data:
                print(f"\n🎮 Brawlers Unlocked: {len(data['brawlers'])}")
                # Show top 3 brawlers by trophies
                sorted_brawlers = sorted(data['brawlers'], key=lambda x: x.get('trophies', 0), reverse=True)
                print("\n🌟 Top 3 Brawlers:")
                for i, brawler in enumerate(sorted_brawlers[:3], 1):
                    print(f"  {i}. {brawler.get('name', 'Unknown')} - {brawler.get('trophies', 0)} 🏆")
            
            return data
            
        elif response.status_code == 404:
            print(f"❌ Player not found: {player_tag}")
            print(f"Response: {response.text}")
            return False
        elif response.status_code == 403:
            print(f"❌ API Key invalid or unauthorized")
            print(f"💡 Check your IP whitelist settings at developer.brawlstars.com")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("🧪 API TESTING SUITE")
    print("="*60)
    
    while True:
        print("\nChoose an option:")
        print("1. Test Clash Royale API")
        print("2. Test Fortnite API")
        print("3. Test Brawl Stars API")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            print("\n--- CLASH ROYALE API TEST ---")
            player_tag = input("Enter player tag (include #): ").strip()
            
            if not CLASH_ROYALE_API_KEY:
                print("❌ No CLASH_ROYALE_API_KEY found in .env file")
                continue
            
            # Ensure tag starts with #
            if not player_tag.startswith("#"):
                player_tag = "#" + player_tag
            
            # Fetch the data
            data = clash_royale.fetch_clash_royale_stats(player_tag, CLASH_ROYALE_API_KEY)
            
            if data:
                print("✅ Success! Data retrieved.\n")
                print("📄 Full API Response:")
                print(json.dumps(data, indent=2))
                
                # Ask if user wants to save
                save_choice = input("\n💾 Save this response to a JSON file? (y/n): ").strip().lower()
                if save_choice == 'y':
                    save_json_to_file(data, "clash_royale", player_tag)
            else:
                print("❌ Failed to retrieve data")
            
        elif choice == "2":
            print("\n--- FORTNITE API TEST ---")
            username = input("Enter Fortnite username: ").strip()
            print("\nPlatform options:")
            print("1. Epic Games")
            print("2. PlayStation (PSN)")
            print("3. Xbox (XBL)")
            platform_choice = input("Enter platform (1-3): ").strip()
            
            platform_map = {"1": "epic", "2": "psn", "3": "xbl"}
            platform = platform_map.get(platform_choice, "epic")
            
            if not FORTNITE_API_KEY:
                print("❌ No FORTNITE_API_KEY found in .env file")
                continue
            
            # Fetch the data
            data = fortnite.fetch_fortnite_stats(username, platform, FORTNITE_API_KEY)
            
            if data and data.get("status") == 200:
                print("✅ Success! Data retrieved.\n")
                print("📄 Full API Response:")
                print(json.dumps(data, indent=2))
                
                # Ask if user wants to save
                save_choice = input("\n💾 Save this response to a JSON file? (y/n): ").strip().lower()
                if save_choice == 'y':
                    save_json_to_file(data, "fortnite", f"{username}_{platform}")
            elif data and data.get("status") == 403:
                print("🔒 Player stats are private")
            else:
                print("❌ Failed to retrieve data")
        
        elif choice == "3":
            print("\n--- BRAWL STARS API TEST ---")
            player_tag = input("Enter player tag (include #): ").strip()
            
            if not BRAWL_STARS_API_KEY:
                print("❌ No BRAWL_STARS_API_KEY found in .env file")
                print("💡 Add BRAWL_STARS_API_KEY to your .env file")
                continue
            
            # Test the API
            data = test_brawl_stars_api(player_tag)
            
            if data:
                # Ask if user wants to save
                save_choice = input("\n💾 Save this response to a JSON file? (y/n): ").strip().lower()
                if save_choice == 'y':
                    save_json_to_file(data, "brawl_stars", player_tag)
            
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()