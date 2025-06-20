# price_scraper.py
"""
Targeted PriceCharting.com scraper for specific Amazing Spider-Man comics
Only scrapes the comics you actually own - much more efficient!
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import Dict, List, Optional

class PriceChartingScraper:
    def __init__(self):
        self.base_url = "https://www.pricecharting.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        })
    
    def get_owned_amazing_spider_man_issues(self, comics_data: List[Dict]) -> List[Dict]:
        """
        Extract only the Amazing Spider-Man issues the user owns
        """
        owned_issues = []
        
        for comic in comics_data:
            title = comic.get('Title', '')
            
            # Only process Amazing Spider-Man (skip Spectacular Spider-Man)
            if 'Amazing Spider-Man' in title and 'Peter Parker' not in title:
                issue_match = re.search(r'#(\d+)', title)
                if issue_match:
                    issue_number = int(issue_match.group(1))
                    estimated_year = self._estimate_year(issue_number)
                    
                    owned_issues.append({
                        'comic': comic,
                        'issue_number': issue_number,
                        'estimated_year': estimated_year,
                        'title': title
                    })
                    print(f"📋 Will target: Amazing Spider-Man #{issue_number} ({estimated_year})")
        
        return owned_issues
    
    def scrape_owned_comics_prices(self, comics_data: List[Dict]) -> List[Dict]:
        """
        Scrape prices for only the comics the user owns
        """
        print("🎯 Starting targeted scraping for YOUR comics only...")
        
        # Get the specific issues the user owns
        owned_issues = self.get_owned_amazing_spider_man_issues(comics_data)
        
        print(f"🕷️ Found {len(owned_issues)} Amazing Spider-Man issues to price")
        
        # Scrape each owned issue directly
        for issue_data in owned_issues:
            issue_number = issue_data['issue_number']
            estimated_year = issue_data['estimated_year']
            comic = issue_data['comic']
            
            print(f"\n💰 Scraping Amazing Spider-Man #{issue_number} ({estimated_year})...")
            
            # Try multiple URL patterns that PriceCharting might use
            possible_urls = self._build_possible_urls(issue_number, estimated_year)
            
            prices = None
            working_url = None
            
            for url in possible_urls:
                print(f"  🔍 Trying: {url}")
                prices = self._scrape_single_issue_prices(url)
                
                if prices and any(prices.values()):
                    working_url = url
                    print(f"    ✅ Found prices!")
                    break
                else:
                    print(f"    ❌ No prices found")
                    time.sleep(1)  # Brief pause between attempts
            
            # Update the comic data
            if not hasattr(comic, 'PriceData'):
                comic['PriceData'] = {}
                
            comic['PriceData'].update({
                'ungraded': prices.get('ungraded') if prices else None,
                'grade_6_0': prices.get('grade_6_0') if prices else None,
                'grade_8_0': prices.get('grade_8_0') if prices else None,
                'source': 'PriceCharting.com',
                'updated': time.strftime('%Y-%m-%d'),
                'url': working_url,
                'status': 'found' if (prices and any(prices.values())) else 'not_found'
            })
            
            # Update EstValue if we found an ungraded price
            if prices and prices.get('ungraded'):
                comic['EstValue'] = f"${prices['ungraded']:.2f}"
                print(f"    💲 Updated EstValue to ${prices['ungraded']:.2f}")
            
            if prices:
                print(f"    📊 Prices found:")
                print(f"       Ungraded: ${prices.get('ungraded', 'N/A')}")
                print(f"       Grade 6.0: ${prices.get('grade_6_0', 'N/A')}")
                print(f"       Grade 8.0: ${prices.get('grade_8_0', 'N/A')}")
        
        return comics_data
    
    def _build_possible_urls(self, issue_number: int, estimated_year: int) -> List[str]:
        """
        Build possible URL patterns for a specific issue
        """
        base_pattern = f"{self.base_url}/game/comic-books-amazing-spider-man/amazing-spider-man-{issue_number}"
        
        return [
            f"{base_pattern}-{estimated_year}",
            f"{base_pattern}-{estimated_year - 1}",
            f"{base_pattern}-{estimated_year + 1}",
            f"{base_pattern}",
            f"{self.base_url}/game/comic-books-amazing-spider-man/amazing-spider-man-{issue_number:03d}-{estimated_year}",
        ]
    
    def _scrape_single_issue_prices(self, url: str) -> Optional[Dict[str, float]]:
        """
        Scrape a single issue page for prices
        """
        try:
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 404:
                return None
                
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for price table structure
            prices = self._extract_prices_from_page(soup)
            
            return prices
            
        except Exception as e:
            print(f"      ⚠️ Error accessing {url}: {str(e)}")
            return None
    
    def _extract_prices_from_page(self, soup: BeautifulSoup) -> Dict[str, Optional[float]]:
        """
        Extract ungraded, 6.0, and 8.0 prices from the page
        """
        prices = {
            'ungraded': None,
            'grade_6_0': None,
            'grade_8_0': None
        }
        
        # Method 1: Look for structured pricing table
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            
            # Look for header row to identify columns
            for row in rows:
                headers = row.find_all(['th', 'td'])
                if len(headers) >= 3:
                    header_texts = [h.get_text(strip=True).lower() for h in headers]
                    
                    # Find column indices
                    ungraded_col = None
                    grade_60_col = None
                    grade_80_col = None
                    
                    for i, header in enumerate(header_texts):
                        if 'ungraded' in header or 'loose' in header:
                            ungraded_col = i
                        elif '6.0' in header or '6' in header:
                            grade_60_col = i
                        elif '8.0' in header or '8' in header:
                            grade_80_col = i
                    
                    # Process subsequent rows for price data
                    for data_row in rows[1:]:
                        cells = data_row.find_all(['td', 'th'])
                        if len(cells) > max(filter(None, [ungraded_col, grade_60_col, grade_80_col] or [0])):
                            
                            if ungraded_col is not None and ungraded_col < len(cells):
                                price_text = cells[ungraded_col].get_text(strip=True)
                                prices['ungraded'] = self._extract_price_value(price_text)
                            
                            if grade_60_col is not None and grade_60_col < len(cells):
                                price_text = cells[grade_60_col].get_text(strip=True)
                                prices['grade_6_0'] = self._extract_price_value(price_text)
                            
                            if grade_80_col is not None and grade_80_col < len(cells):
                                price_text = cells[grade_80_col].get_text(strip=True)
                                prices['grade_8_0'] = self._extract_price_value(price_text)
                            
                            # If we found any prices, use this row
                            if any(prices.values()):
                                return prices
        
        # Method 2: Look for price elements with class="price"
        price_elements = soup.find_all(class_='price')
        if price_elements and len(price_elements) >= 1:
            extracted_prices = []
            for elem in price_elements[:5]:  # Look at first 5 price elements
                price_val = self._extract_price_value(elem.get_text(strip=True))
                if price_val and price_val > 0:
                    extracted_prices.append(price_val)
            
            if extracted_prices:
                extracted_prices.sort()  # Sort low to high
                
                # Assign based on assumption: lowest=ungraded, higher=graded
                if len(extracted_prices) >= 3:
                    prices['ungraded'] = extracted_prices[0]
                    prices['grade_6_0'] = extracted_prices[1] 
                    prices['grade_8_0'] = extracted_prices[2]
                elif len(extracted_prices) >= 2:
                    prices['ungraded'] = extracted_prices[0]
                    prices['grade_8_0'] = extracted_prices[1]
                else:
                    prices['ungraded'] = extracted_prices[0]
        
        return prices
    
    def _extract_price_value(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text like '$45.00' or '45'"""
        if not price_text or price_text.lower() in ['n/a', '-', '']:
            return None
        
        # Clean the text and look for price patterns
        price_text = price_text.replace(',', '').replace('$', '').strip()
        
        # Look for decimal numbers
        price_match = re.search(r'(\d+\.?\d*)', price_text)
        if price_match:
            try:
                price = float(price_match.group(1))
                # Sanity check - reject unreasonable prices
                if 0.01 <= price <= 100000:
                    return price
            except ValueError:
                pass
        
        return None
    
    def _estimate_year(self, issue_number: int) -> int:
        """
        Estimate publication year based on issue number for Amazing Spider-Man
        """
        # Amazing Spider-Man publication timeline estimates
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
