# json_updater.py
"""
Updates the comic JSON file with new pricing data from PriceCharting
Transforms to enhanced hybrid structure with ManualData and PriceChartingData
"""

import json
import re
import time
from typing import Dict, List, Optional
from .price_scraper import PriceChartingScraper

def update_json_with_prices(json_path: str):
    """
    Read JSON, transform to enhanced hybrid structure, add price data, save back to same file
    """
    print("📖 Loading comic data...")
    
    # Load original data with UTF-8 encoding
    with open(json_path, 'r', encoding='utf-8') as f:
        comics_data = json.load(f)
    
    print(f"Found {len(comics_data)} comics to process")
    
    # Transform to enhanced hybrid structure
    enhanced_comics = []
    
    for i, comic in enumerate(comics_data):
        print(f"\n🔄 Processing {i+1}/{len(comics_data)}: {comic.get('Title', 'Unknown')}")
        
        # Extract issue info from title
        title = comic.get('Title', '')
        issue_number = extract_issue_number(title)
        series = extract_series(title)
        year = estimate_year(series, issue_number) if issue_number else None
        
        # Create enhanced structure
        enhanced_comic = {
            'Title': title,
            'IssueNumber': issue_number,
            'Series': series,
            'Year': year,
            'ManualData': {
                'Grade': comic.get('Grade'),
                'EstValue': comic.get('EstValue'),
                'KeyNotes': comic.get('KeyNotes'),
                'Event': comic.get('Event'),
                'Creator': comic.get('Creator')
            },
            'PriceChartingData': {
                'ungraded': None,
                'grade_6_0': None,
                'grade_8_0': None,
                'url': None,
                'source': 'PriceCharting.com',
                'lastUpdated': time.strftime('%Y-%m-%d'),
                'status': 'pending'
            }
        }
        
        enhanced_comics.append(enhanced_comic)
        print(f"  📋 Structured: {series} #{issue_number} ({year})")
    
    # Now scrape prices for Amazing Spider-Man issues
    print(f"\n🕷️ Starting PriceCharting scraper...")
    scraper = PriceChartingScraper()
    
    # Get all available issues from PriceCharting
    available_issues = scraper.scrape_all_issues_list()
    available_map = {issue['issue_number']: issue for issue in available_issues}
    
    print(f"📊 Found {len(available_issues)} issues on PriceCharting")
    
    # Update each comic with price data
    for comic in enhanced_comics:
        if comic['Series'] == 'Amazing Spider-Man' and comic['IssueNumber']:
            issue_num = comic['IssueNumber']
            
            if issue_num in available_map:
                print(f"  💰 Scraping prices for Amazing Spider-Man #{issue_num}...")
                
                # Scrape prices for this issue
                prices = scraper.scrape_comic_prices(issue_num)
                
                # Update PriceCharting data
                comic['PriceChartingData'].update({
                    'ungraded': prices.get('ungraded'),
                    'grade_6_0': prices.get('grade_6_0'),
                    'grade_8_0': prices.get('grade_8_0'),
                    'url': available_map[issue_num].get('url'),
                    'status': 'found' if any(prices.values()) else 'no_prices'
                })
                
                print(f"    ✅ Ungraded: ${prices.get('ungraded', 'N/A')}")
                print(f"    ✅ Grade 6.0: ${prices.get('grade_6_0', 'N/A')}")
                print(f"    ✅ Grade 8.0: ${prices.get('grade_8_0', 'N/A')}")
                
            else:
                print(f"  ⚠️  Amazing Spider-Man #{issue_num} not found on PriceCharting")
                comic['PriceChartingData']['status'] = 'not_found'
        
        elif comic['Series'].startswith('Peter Parker'):
            print(f"  ℹ️  Skipping {comic['Series']} #{comic['IssueNumber']} (not on Amazing Spider-Man page)")
            comic['PriceChartingData']['status'] = 'different_series'
        
        else:
            print(f"  ℹ️  Skipping {comic['Title']} (unable to identify series/issue)")
            comic['PriceChartingData']['status'] = 'unable_to_parse'
    
    # Save enhanced data back to same file with UTF-8 encoding
    print(f"\n💾 Saving enhanced data to {json_path}...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced_comics, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ Enhanced data saved! Your JSON now has:")
    print(f"   📚 Original collector data in 'ManualData'")
    print(f"   💰 Live prices in 'PriceChartingData'")
    print(f"   🏷️  Issue numbers, series, and years extracted")

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

def estimate_year(series: str, issue_number: Optional[int]) -> Optional[int]:
    """Estimate publication year based on series and issue number"""
    if not issue_number:
        return None
    
    # Rough estimates based on publication history
    if series == 'Amazing Spider-Man':
        if issue_number <= 100:
            return 1963 + ((issue_number - 1) // 12)
        elif issue_number <= 200:
            return 1971 + ((issue_number - 101) // 12)
        elif issue_number <= 300:
            return 1979 + ((issue_number - 201) // 12)
        elif issue_number <= 400:
            return 1987 + ((issue_number - 301) // 12)
        else:
            return 1995 + ((issue_number - 401) // 12)
    
    elif series.startswith('Peter Parker'):
        # Spectacular Spider-Man started in 1976
        return 1976 + ((issue_number - 1) // 12)
    
    return None
