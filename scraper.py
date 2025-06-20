# test_pricecharting.py
"""
Test script to explore PriceCharting's actual HTML structure
This helps debug and find the right selectors
"""

import requests
from bs4 import BeautifulSoup
import json

def explore_pricecharting_structure():
    """Explore the structure of PriceCharting pages"""
    
    # Test the main list page
    print("=" * 60)
    print("TESTING MAIN LIST PAGE")
    print("=" * 60)
    
    list_url = "https://www.pricecharting.com/console/comic-books-amazing-spider-man"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    response = session.get(list_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print(f"Page Title: {soup.title.string if soup.title else 'No title'}")
    print(f"Status Code: {response.status_code}\n")
    
    # Look for tables
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables on the page")
    for i, table in enumerate(tables[:3]):
        print(f"\nTable {i+1} classes: {table.get('class', [])}")
        print(f"Table {i+1} id: {table.get('id', 'No ID')}")
        
        # Show first row structure
        first_row = table.find('tr')
        if first_row:
            cells = first_row.find_all(['td', 'th'])
            print(f"First row has {len(cells)} cells")
            for j, cell in enumerate(cells[:5]):
                print(f"  Cell {j+1}: {cell.get_text(strip=True)[:30]}...")
    
    # Look for links with comic titles
    print("\n" + "=" * 60)
    print("LOOKING FOR COMIC LINKS")
    print("=" * 60)
    
    # Try various selectors
    selectors_to_try = [
        ('a[href*="spider-man-"]', 'Links containing "spider-man-"'),
        ('td.title a', 'Links in td.title'),
        ('div.game a', 'Links in div.game'),
        ('tr td:first-child a', 'Links in first td of rows'),
        ('a[href*="/game/"]', 'Links containing "/game/"')
    ]
    
    for selector, description in selectors_to_try:
        links = soup.select(selector)
        if links:
            print(f"\n✅ Found {len(links)} matches for: {description}")
            print(f"   Selector: {selector}")
            for link in links[:3]:
                print(f"   - Text: {link.get_text(strip=True)[:40]}...")
                print(f"     Href: {link.get('href', 'No href')}")
    
    # Test a specific issue page
    print("\n" + "=" * 60)
    print("TESTING SPECIFIC ISSUE PAGE (Spider-Man #1)")
    print("=" * 60)
    
    issue_url = "https://www.pricecharting.com/game/comic-books-amazing-spider-man/amazing-spider-man-1"
    response = session.get(issue_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"Page Title: {soup.title.string if soup.title else 'No title'}")
        
        # Look for prices
        price_selectors = [
            ('span.price', 'span.price'),
            ('.price', 'class="price"'),
            ('td:contains("$")', 'td containing $'),
            ('.buybox .price', 'buybox prices'),
            ('div.price', 'div.price')
        ]
        
        for selector, description in price_selectors:
            if ':contains' in selector:
                # BeautifulSoup doesn't support :contains, use different approach
                elements = soup.find_all('td', string=lambda text: '$' in str(text))
            else:
                elements = soup.select(selector)
            
            if elements:
                print(f"\n✅ Found {len(elements)} prices with: {description}")
                for elem in elements[:3]:
                    print(f"   - {elem.get_text(strip=True)}")
        
        # Look for condition/grade information
        print("\n" + "=" * 40)
        print("LOOKING FOR CONDITIONS/GRADES")
        print("=" * 40)
        
        # Find any text mentioning grades
        grade_texts = []
        for text in soup.stripped_strings:
            if any(grade in text.lower() for grade in ['6.0', '8.0', 'ungraded', 'fine', 'very fine']):
                grade_texts.append(text)
        
        if grade_texts:
            print("Found grade-related text:")
            for text in grade_texts[:10]:
                print(f"  - {text}")
    else:
        print(f"❌ Could not load issue page. Status: {response.status_code}")

if __name__ == "__main__":
    explore_pricecharting_structure()