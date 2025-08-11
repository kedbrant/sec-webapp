import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, Optional

class SECFilingDownloader:
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'SEC Analysis Bot contact@example.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
    
    def download_filing(self, accession_number: str) -> Optional[Dict]:
        """
        Download a filing by accession number
        Format: 0000123456-21-000001
        """
        try:
            # Clean accession number
            accession_clean = accession_number.replace('-', '')
            
            # Build URL for the filing
            url = f"{self.base_url}/Archives/edgar/data/{accession_clean[:10]}/{accession_clean}/{accession_number}.txt"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return self.parse_filing_content(response.text, accession_number)
            
        except requests.RequestException as e:
            print(f"Error downloading filing {accession_number}: {e}")
            return None
    
    def parse_filing_content(self, content: str, accession_number: str) -> Dict:
        """Parse the raw filing content and extract key information"""
        lines = content.split('\n')
        
        filing_info = {
            'accession_number': accession_number,
            'raw_content': content,
            'form_type': None,
            'company_name': None,
            'filing_date': None,
            'owner_name': None,
            'shares_owned': None,
            'ownership_percent': None,
            'purpose': None
        }
        
        # Extract basic info from header
        for line in lines[:50]:
            if 'FORM TYPE:' in line:
                filing_info['form_type'] = line.split('FORM TYPE:')[1].strip()
            elif 'COMPANY CONFORMED NAME:' in line:
                filing_info['company_name'] = line.split('COMPANY CONFORMED NAME:')[1].strip()
            elif 'FILED AS OF DATE:' in line:
                date_str = line.split('FILED AS OF DATE:')[1].strip()
                try:
                    filing_info['filing_date'] = datetime.strptime(date_str, '%Y%m%d')
                except:
                    pass
        
        # Look for ownership information in the document body
        full_text = ' '.join(lines)
        
        # Find ownership percentage
        percent_match = re.search(r'(\d+\.?\d*)\s*%', full_text)
        if percent_match:
            filing_info['ownership_percent'] = float(percent_match.group(1))
        
        # Find number of shares
        shares_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*shares?', full_text, re.IGNORECASE)
        if shares_match:
            shares_str = shares_match.group(1).replace(',', '')
            filing_info['shares_owned'] = int(shares_str)
        
        return filing_info
    
    def search_recent_13d_filings(self, limit: int = 10) -> list:
        """Search for recent 13D filings"""
        search_url = f"{self.base_url}/cgi-bin/browse-edgar"
        
        params = {
            'action': 'getcompany',
            'type': '13D',
            'dateb': '',
            'owner': 'include',
            'count': limit
        }
        
        try:
            response = requests.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            filings = []
            
            # This is a simplified parser - actual implementation would be more robust
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        filing = {
                            'company': cells[0].text.strip(),
                            'form_type': cells[1].text.strip(),
                            'filing_date': cells[2].text.strip(),
                            'accession_number': cells[3].find('a')['href'].split('/')[-1] if cells[3].find('a') else None
                        }
                        filings.append(filing)
            
            return filings
            
        except requests.RequestException as e:
            print(f"Error searching for filings: {e}")
            return []