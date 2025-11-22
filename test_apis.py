import os
from dotenv import load_dotenv
import clash_royale
import fortnite
import json
from datetime import datetime

# Load environment variables
load_dotenv()
CLASH_ROYALE_API_KEY = os.getenv("CLASH_ROYALE_API_KEY")
FORTNITE_API_KEY = os.getenv("FORTNITE_API_KEY")

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

def main():
    print("\n" + "="*60)
    print("🧪 API TESTING SUITE")
    print("="*60)
    
    while True:
        print("\nChoose an option:")
        print("1. Test Clash Royale API")
        print("2. Test Fortnite API")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
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
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()