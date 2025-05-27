import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import time
import logging

logger = logging.getLogger(__name__)

class LegislationExtractor:
    BASE_URL = "https://www.legislation.gov.uk"
    
    def __init__(self, category: str, start_date: datetime, end_date: datetime):
        self.category = category
        self.start_date = start_date
        self.end_date = end_date
        
    def fetch_legislation_list(self) -> List[Dict]:
        """Fetch list of legislation matching criteria"""
        params = {
            "text": self.category,
            "date.from": self.start_date.strftime("%Y-%m-%d"),
            "date.to": self.end_date.strftime("%Y-%m-%d"),
            "type": "legislation",
            "pageSize": 100
        }
        
        legislation_list = []
        page = 1
        
        while True:
            try:
                params["page"] = page
                response = requests.get(f"{self.BASE_URL}/search", params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                items = soup.select(".search-results .result")
                
                if not items:
                    break
                    
                for item in items:
                    title = item.select_one(".title")
                    if title:
                        legislation_list.append({
                            "title": title.text.strip(),
                            "url": f"{self.BASE_URL}{item.select_one('a')['href']}",
                            "date": item.select_one(".date").text.strip() if item.select_one(".date") else "",
                            "type": item.select_one(".type").text.strip() if item.select_one(".type") else ""
                        })
                
                page += 1
                time.sleep(1)  # Be polite
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {str(e)}")
                break
                
        return legislation_list
    
    def fetch_legislation_text(self, url: str) -> Dict:
        """Fetch full text of a legislation"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.select("img, .watermark, .annotation, .note, header, footer, nav"):
                element.decompose()
                
            # Extract main content
            content = soup.select_one(".Legislation")
            if not content:
                content = soup.select_one("body")
                
            text = content.get_text(separator="\n", strip=True) if content else ""
            
            # Extract metadata
            metadata = {
                "title": soup.select_one("h1").text.strip() if soup.select_one("h1") else "",
                "year": soup.select_one(".year").text.strip() if soup.select_one(".year") else "",
                "number": soup.select_one(".number").text.strip() if soup.select_one(".number") else "",
                "source_url": url
            }
            
            return {
                "text": text,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return {
                "text": "",
                "metadata": {
                    "title": "",
                    "year": "",
                    "number": "",
                    "source_url": url
                }
            }