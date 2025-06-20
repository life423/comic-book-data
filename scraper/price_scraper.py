# price_scraper.py
"""
PriceCharting.com scraper for Amazing Spider-Man comics
Uses proven working logic from the root scraper.py test file
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.issue_url_map = {}  # Cache for issue URLs
    
    def scrape_all_issues_list(self) -> List[Dict]:
        """
        Scrape the main Amazing Spider-Man page using proven working selectors
        """
        list_url = f"{self.base_url}/console/comic-books-amazing-spider-man"
        all_issues = []
        
        try:
            print("🕷️ Fetching Amazing Spider-Man list from PriceCharting...")
            response = self.session.get(list_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Use the proven working selector: td.title a
            title_links = soup.select('td.title a')
            
            if title_links:
                print(f"✅ Found {len(title_links)} comics using td.title a selector")
                
                for link in title_links:
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
            
            else:
                # Fallback to alternative working selector
                print("🔄 Trying alternative selector: a[href*='spider-man-']")
                spider_links = soup.select('a[href*="spider-man-"]')
                
                for link in spider_links[:100]:  # Limit to avoid duplicates
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if title and '#' in title:
                        issue_match = re.search(r'#(\d+)', title)
                        if issue_match:
                            issue_num = int(issue_match.group(1))
                            full_url = self.base_url + href if href.startswith('/') else href
                            
                            if issue_num not in self.issue_url_map:
                                issue_data = {
                                    'issue_number': issue_num,
                                    'title': title,
                                    'url': full_url
                                }
                                all_issues.append(issue_data)
                                self.issue_url_map[issue_num] = full_url
            
            print(f"📊 Found {len(all_issues)} issues total")
            
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
            
            # Look for price elements (your test showed this works)
            price_elements = soup.select('.price')
            
            if price_elements:
                print(f"    📊 Found {len(price_elements)} price elements")
                
                # Extract the first few prices as different grades
                extracted_prices = []
                for elem in price_elements[:10]:  # Look at first 10 prices
                    price_text = elem.get_text(strip=True)
                    price_val = self._extract_price(price_text)
                    if price_val and price_val > 0:
                        extracted_prices.append(price_val)
                
                # Assign based on pattern - lowest is usually ungraded, higher grades cost more
                if extracted_prices:
                    extracted_prices.sort()  # Sort low to high
                    
                    if len(extracted_prices) >= 3:
                        prices['ungraded'] = extracted_prices[0]
                        prices['grade_6_0'] = extracted_prices[1]
                        prices['grade_8_0'] = extracted_prices[2]
                    elif len(extracted_prices) >= 2:
                        prices['ungraded'] = extracted_prices[0]
                        prices['grade_8_0'] = extracted_prices[1]
                    else:
                        prices['ungraded'] = extracted_prices[0]
            
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
