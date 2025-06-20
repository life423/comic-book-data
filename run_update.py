# run_update.py
"""
Main script to update comic prices from PriceCharting
Run this to update your JSON file with current prices
"""

import os
from scraper.json_updater import update_json_with_prices

def main():
    # Single source of truth - one JSON file
    json_file = "data/spiderman_comics_data.json"
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Check if file exists
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        print("Please place your spiderman_comics_data.json in the data/ folder")
        return
    
    print("🕷️ Spider-Man Comic Price Updater")
    print("=" * 50)
    print(f"Processing: {json_file}")
    print("This will enhance your JSON with PriceCharting data")
    print("=" * 50)
    
    # Run the update (transforms and updates the same file)
    update_json_with_prices(json_file)
    
    print("\n🎉 Done! Your JSON has been enhanced.")
    print("The file now includes:")
    print("  📚 Your original collector data in 'ManualData'")
    print("  💰 Live PriceCharting prices in 'PriceChartingData'")
    print("  🏷️  Issue numbers, series, and years extracted")

if __name__ == "__main__":
    main()
