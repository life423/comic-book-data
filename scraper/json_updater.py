# json_updater.py
"""
Updates the comic JSON file with live pricing data from PriceCharting
Keeps original structure simple and adds PriceData section
"""

import json
import re
import time
from typing import Dict, List, Optional
from .price_scraper import PriceChartingScraper

def update_json_with_prices(json_path: str):
    """
    Read JSON, add PriceData section, update EstValue from scraper
    """
    print("📖 Loading comic data...")
    
    # Load original data with UTF-8 encoding
    with open(json_path, 'r', encoding='utf-8') as f:
        comics_data = json.load(f)
    
    print(f"Found {len(comics_data)} comics to process")
    
    # Start scraper
    print(f"\n🕷️ Starting PriceCharting scraper...")
    scraper = PriceChartingScraper()
    
    # Get all available issues from PriceCharting
    available_issues = scraper.scrape_all_issues_list()
    available_map = {issue['issue_number']: issue for issue in available_issues}
    
    print(f"📊 Found {len(available_issues)} issues on PriceCharting")
    
    # Update each comic with price data
    for i, comic in enumerate(comics_data):
        print(f"\n🔄 Processing {i+1}/{len(comics_data)}: {comic['Title']}")
        
        # Extract issue number from title
        issue_number = extract_issue_number(comic['Title'])
        series = extract_series(comic['Title'])
        
        # Set grade to "Ungraded" since user said all comics are ungraded
        comic['Grade'] = 'Ungraded'
        
        # Add empty PriceData section
        comic['PriceData'] = {
            'ungraded': None,
            'grade_6_0': None,
            'grade_8_0': None,
            'source': 'PriceCharting.com',
            'updated': time.strftime('%Y-%m-%d'),
            'status': 'pending'
        }
        
        # Try to scrape prices if it's Amazing Spider-Man
        if series == 'Amazing Spider-Man' and issue_number and issue_number in available_map:
            print(f"  💰 Scraping prices for Amazing Spider-Man #{issue_number}...")
            
            # Scrape prices for this issue
            prices = scraper.scrape_comic_prices(issue_number)
            
            # Update PriceData
            comic['PriceData'].update({
                'ungraded': prices.get('ungraded'),
                'grade_6_0': prices.get('grade_6_0'),
                'grade_8_0': prices.get('grade_8_0'),
                'status': 'found' if prices.get('ungraded') else 'no_prices'
            })
            
            # Update EstValue with ungraded price from scraper
            ungraded_price = prices.get('ungraded')
            if ungraded_price:
                comic['EstValue'] = f"${ungraded_price:.2f}"
                print(f"    ✅ Updated EstValue to ${ungraded_price:.2f}")
            
            print(f"    ✅ Ungraded: ${prices.get('ungraded', 'N/A')}")
            print(f"    ✅ Grade 6.0: ${prices.get('grade_6_0', 'N/A')}")
            print(f"    ✅ Grade 8.0: ${prices.get('grade_8_0', 'N/A')}")
            
        elif series == 'Amazing Spider-Man' and issue_number:
            print(f"  ⚠️  Amazing Spider-Man #{issue_number} not found on PriceCharting")
            comic['PriceData']['status'] = 'not_found'
            
        elif series.startswith('Peter Parker'):
            print(f"  ℹ️  Skipping {series} #{issue_number} (not on Amazing Spider-Man page)")
            comic['PriceData']['status'] = 'different_series'
            
        else:
            print(f"  ℹ️  Skipping {comic['Title']} (unable to identify series/issue)")
            comic['PriceData']['status'] = 'unable_to_parse'
    
    # Save enhanced data back to same file with UTF-8 encoding
    print(f"\n💾 Saving enhanced data to {json_path}...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(comics_data, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ Enhanced data saved!")
    print(f"   📚 Preserved original collector data")
    print(f"   💰 Added live prices in 'PriceData' section")
    print(f"   🏷️  Updated EstValue from ungraded prices")

def extract_issue_number(title: str) -> Optional[int]:
    """Extract issue number from title like 'Amazing Spider-Man #315'"""
    match = re.search(r'#(\d+)', title)
    return int(match.group(1)) if match else None

def extract_series(title: str) -> str:
    """Extract series name from title"""
    if 'Peter Parker, The Spectacular Spider-Man' in title:
        return 'Peter Parker, The Spectacular Spider-Man'
    elif 'Amazing Spider-Man' in title:
        return 'Amazing Spider-Man'
    elif 'Spectacular Spider-Man' in title:
        return 'Spectacular Spider-Man'
    elif 'Spider-Man' in title:
        return 'Spider-Man'
    else:
        # Extract everything before the #
        match = re.match(r'^([^#]+)', title)
        return match.group(1).strip() if match else 'Unknown Series'
