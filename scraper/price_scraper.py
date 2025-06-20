# price_scraper.py
"""
PriceCharting.com scraper for Amazing Spider-Man comics
Gets ungraded, 6.0, and 8.0 grade prices based on actual site structure
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
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.issue_url_map = {}  # Cache for issue URLs
    
    def scrape_all_issues_list(self) -> List[Dict]:
        """
        Scrape the main Amazing Spider-Man page to get all available issues
        Based on your test output showing table structure
        """
        list_url = f"{self.base_url}/console/comic-books-amazing-spider-man"
        all_issues = []
        
        try:
            print("🕷️ Fetching Amazing Spider-Man list from PriceCharting...")
            response = self.session.get(list_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Based on your test: table with id="games_table"
            main_table = soup.find('table', id='games_table')
            if not main_table:
                # Fallback to other table selectors from your test
                main_table = soup.find('table', class_='js-addable')
                if not main_table:
                    main_table = soup.find('table', class_='hoverable-rows')
            
            if main_table:
                print("✅ Found games table")
                rows = main_table.find_all('tr')
                
                for i, row in enumerate(rows):
                    # Skip header row
                    if i == 0 or row.find('th'):
                        continue
                    
                    # Based on your test: td.title a selector works
                    title_cell = row.find('td', class_='title')
                    if title_cell:
                        link = title_cell.find('a')
                        if link:
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            
                            # Extract issue number from title like "Amazing Spider-Man #1 (1963)"
                            issue_match = re.search(r'#(\d+)', title)
                            if issue_match:
                                issue_num = int(issue_match.group(1))
                                full_url = self.base_url + href if href.startswith('/') else href
                                
                                issue_data = {
                                    'issue_number': issue_num,
                                    'title': title,
                                    'url': full_url
                                }
                                all_issues.append(issue_data)
                                self.issue_url_map[issue_num] = full_url
            
            # Alternative method if table method fails
            if not all_issues:
                print("🔄 Trying alternative link selector...")
                # Based on your test: a[href*="spider-man-"] works
                spider_links = soup.find_all('a', href=re.compile(r'spider-man-'))
                
                for link in spider_links[:50]:  # Limit to avoid duplicates
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if title and '#' in title:  # Only process if it has issue number
                        issue_match = re.search(r'#(\d+)', title)
                        if issue_match:
                            issue_num = int(issue_match.group(1))
                            full_url = self.base_url + href if href.startswith('/') else href
                            
                            # Avoid duplicates
                            if issue_num not in self.issue_url_map:
                                issue_data = {
                                    'issue_number': issue_num,
                                    'title': title,
                                    'url': full_url
                                }
                                all_issues.append(issue_data)
                                self.issue_url_map[issue_num] = full_url
            
            print(f"📊 Found {len(all_issues)} issues on PriceCharting")
            
            # Show sample of what we found
            if all_issues:
                print("📋 Sample issues found:")
                for issue in sorted(all_issues, key=lambda x: x['issue_number'])[:5]:
                    print(f"   #{issue['issue_number']}: {issue['title']}")
            
        except Exception as e:
            print(f"❌ Error fetching issue list: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return all_issues
    
    def scrape_comic_prices(self, issue_number: int) -> Dict[str, Optional[float]]:
        """
        Scrape prices for a specific Amazing Spider-Man issue
        Based on your test showing price structure with ungraded, 6.0, 8.0 columns
        """
        prices = {
            'ungraded': None,
            'grade_6_0': None,
            'grade_8_0': None
        }
        
        # Get the exact URL for this issue
        comic_url = self.issue_url_map.get(issue_number)
        if not comic_url:
            print(f"  ⚠️ No URL found for issue #{issue_number}")
            return prices
        
        try:
            print(f"  🔍 Fetching prices for #{issue_number}...")
            response = self.session.get(comic_url)
            
            if response.status_code == 404:
                print(f"    ❌ Issue #{issue_number} page not found")
                return prices
            
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Method 1: Look for main pricing table
            # Your test showed it finds lots of prices with class="price"
            price_elements = soup.find_all(class_='price')
            
            # Method 2: Try to find structured price data
            # Look for the main pricing table similar to the list page
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                # Look for header row to identify columns
                header_row = None
                for row in rows:
                    if row.find('th'):
                        header_row = row
                        break
                
                if header_row:
                    headers = [th.get_text(strip=True).lower() for th in header_row.find_all('th')]
                    
                    # Find column indices for our target grades
                    ungraded_col = None
                    grade_60_col = None
                    grade_80_col = None
                    
                    for i, header in enumerate(headers):
                        if 'ungraded' in header:
                            ungraded_col = i
                        elif '6.0' in header:
                            grade_60_col = i
                        elif '8.0' in header:
                            grade_80_col = i
                    
                    # Process data rows
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all(['td', 'th'])
                        if len(cells) > max(filter(None, [ungraded_col, grade_60_col, grade_80_col])):
                            
                            if ungraded_col is not None and ungraded_col < len(cells):
                                price_text = cells[ungraded_col].get_text(strip=True)
                                prices['ungraded'] = self._extract_price(price_text)
                            
                            if grade_60_col is not None and grade_60_col < len(cells):
                                price_text = cells[grade_60_col].get_text(strip=True)
                                prices['grade_6_0'] = self._extract_price(price_text)
                            
                            if grade_80_col is not None and grade_80_col < len(cells):
                                price_text = cells[grade_80_col].get_text(strip=True)
                                prices['grade_8_0'] = self._extract_price(price_text)
                            
                            # If we found prices, we can break
                            if any(prices.values()):
                                break
            
            # Method 3: Fallback - look for prominent price display
            if not any(prices.values()):
                # Look for main price display elements
                main_price = soup.find('span', class_='price')
                if main_price:
                    # This might be the "loose" or most common price
                    price_val = self._extract_price(main_price.get_text())
                    if price_val:
                        prices['ungraded'] = price_val
            
            # Rate limiting
            time.sleep(1.5)
            
        except Exception as e:
            print(f"    ❌ Error scraping issue #{issue_number}: {str(e)}")
        
        return prices
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text like '$45.00' or '45'"""
        if not price_text:
            return None
        
        # Clean the text and look for price patterns
        price_text = price_text.replace(',', '').replace('$', '')
        
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
