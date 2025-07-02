# json_updater.py
"""
Updates the comic JSON file with live pricing data from PriceCharting
Uses targeted scraping - only scrapes the comics you actually own
"""

import json
import re
import time
from typing import Dict, List, Optional
from .price_scraper import PriceChartingScraper

def update_json_with_prices(json_path: str):
    """
    Read JSON, add PriceData section, update EstValue from scraper
    Uses targeted approach - only scrapes your owned comics
    """
    print("📖 Loading your comic collection...")
    
    # Load original data with UTF-8 encoding
    with open(json_path, 'r', encoding='utf-8') as f:
        comics_data = json.load(f)
    
    print(f"Found {len(comics_data)} comics in your collection")
    
    # Set grade to "Ungraded" for all comics and add empty PriceData section
    for comic in comics_data:
        comic['Grade'] = 'Ungraded'
        comic['PriceData'] = {
            'ungraded': None,
            'grade_6_0': None,
            'grade_8_0': None,
            'source': 'PriceCharting.com',
            'updated': time.strftime('%Y-%m-%d'),
            'status': 'pending'
        }
    
    # Use targeted scraper to get prices for only your comics
    scraper = PriceChartingScraper()
    updated_comics = scraper.scrape_owned_comics_prices(comics_data)
    
    # Handle Spectacular Spider-Man comics (mark as different series)
    for comic in updated_comics:
        title = comic.get('Title', '')
        if 'Peter Parker, The Spectacular Spider-Man' in title:
            issue_number = extract_issue_number(title)
            print(f"\n🔄 Processing {title}")
            print(f"  ℹ️  Skipping Spectacular Spider-Man #{issue_number} (different series from Amazing Spider-Man)")
            comic['PriceData']['status'] = 'different_series'
    
    # Save enhanced data back to same file with UTF-8 encoding
    print(f"\n💾 Saving enhanced data to {json_path}...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(updated_comics, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ Enhanced data saved!")
    print(f"   📚 Preserved original collector data")
    print(f"   💰 Added live prices in 'PriceData' section")
    print(f"   🏷️  Updated EstValue from ungraded prices where found")
    
    # Show summary of what was found
    amazing_count = 0
    found_count = 0
    spectacular_count = 0
    
    # Process comics to generate summary
    for comic in updated_comics:
        title = comic.get('Title', '')
        status = comic.get('PriceData', {}).get('status', 'unknown')
        
        if 'Amazing Spider-Man' in title and 'Peter Parker' not in title:
            amazing_count += 1
            if status == 'found':
                found_count += 1
        elif 'Peter Parker, The Spectacular Spider-Man' in title:
            spectacular_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   🕷️  {amazing_count} Amazing Spider-Man comics targeted")
    print(f"   💰 {found_count} prices found")
    print(f"   ❌ {amazing_count - found_count} Amazing Spider-Man issues not found on PriceCharting")
    print(f"   📖 {spectacular_count} Spectacular Spider-Man comics skipped (different series)")

def extract_issue_number(title: str) -> Optional[int]:
    """Extract issue number from title like 'Amazing Spider-Man #315'"""
    match = re.search(r'#(\d+)', title)
    return int(match.group(1)) if match else None
