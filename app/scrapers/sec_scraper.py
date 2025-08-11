import requests
import re
import asyncio
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urljoin
import time

class SECRealTimeScraper:
    """
    Enhanced SEC scraper for real-time data collection
    Focuses on identifying trading signals from institutional filings
    """
    
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'Trading Signal Analyzer contact@example.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        # Rate limiting to respect SEC servers
        self.request_delay = 0.1  # 100ms between requests
        
    async def get_recent_filings(self, days_back: int = 7, form_types: List[str] = None) -> List[Dict]:
        """
        Get recent filings from SEC EDGAR database
        Focus on 13D/13G forms which indicate large position changes
        """
        if form_types is None:
            form_types = ["13D", "13G", "13G/A"]
            
        all_filings = []
        
        for form_type in form_types:
            try:
                filings = await self._scrape_form_type(form_type, days_back)
                all_filings.extend(filings)
                await asyncio.sleep(self.request_delay)
            except Exception as e:
                print(f"Error scraping {form_type}: {e}")
                continue
                
        return all_filings
    
    async def _scrape_form_type(self, form_type: str, days_back: int) -> List[Dict]:
        """
        Scrape filings for a specific form type
        """
        filings = []
        
        # SEC EDGAR search URL for recent filings
        search_url = f"{self.base_url}/cgi-bin/browse-edgar"
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        params = {
            'action': 'getcompany',
            'type': form_type,
            'dateb': end_date.strftime('%Y%m%d'),
            'datea': start_date.strftime('%Y%m%d'),
            'owner': 'include',
            'count': '100',
            'output': 'xml'
        }
        
        try:
            response = requests.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # Parse the response to extract filing information
            filings = self._parse_edgar_response(response.text, form_type)
            
        except requests.RequestException as e:
            print(f"Error fetching {form_type} filings: {e}")
            
        return filings
    
    def _parse_edgar_response(self, response_text: str, form_type: str) -> List[Dict]:
        """
        Parse SEC EDGAR response to extract filing data
        """
        filings = []
        
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            
            # Look for filing entries
            entries = soup.find_all('entry') if soup.find_all('entry') else []
            
            for entry in entries:
                filing_data = self._extract_filing_data(entry, form_type)
                if filing_data:
                    filings.append(filing_data)
                    
        except Exception as e:
            print(f"Error parsing EDGAR response: {e}")
            
        return filings
    
    def _extract_filing_data(self, entry, form_type: str) -> Optional[Dict]:
        """
        Extract relevant data from a filing entry
        """
        try:
            # Extract basic filing information
            title = entry.find('title')
            company_name = title.text.split(' - ')[0] if title else "Unknown"
            
            # Extract CIK
            cik_match = re.search(r'CIK: (\d+)', entry.text) if entry.text else None
            cik = cik_match.group(1) if cik_match else None
            
            # Extract filing date
            updated = entry.find('updated')
            filing_date = datetime.fromisoformat(updated.text.replace('Z', '+00:00')) if updated else None
            
            # Extract accession number from link
            link = entry.find('link')
            accession_number = None
            filing_url = None
            
            if link and link.get('href'):
                href = link.get('href')
                filing_url = urljoin(self.base_url, href)
                
                # Extract accession number from URL
                acc_match = re.search(r'/(\d{10}-\d{2}-\d{6})/', href)
                accession_number = acc_match.group(1) if acc_match else None
            
            return {
                'form_type': form_type,
                'company_name': company_name,
                'cik': cik,
                'filing_date': filing_date,
                'accession_number': accession_number,
                'url': filing_url,
                'source': 'SEC_EDGAR_REALTIME'
            }
            
        except Exception as e:
            print(f"Error extracting filing data: {e}")
            return None
    
    async def get_company_filings(self, cik: str, form_types: List[str] = None) -> List[Dict]:
        """
        Get all recent filings for a specific company
        """
        if form_types is None:
            form_types = ["13D", "13G", "13G/A"]
            
        all_filings = []
        
        for form_type in form_types:
            try:
                filings = await self._scrape_company_form_type(cik, form_type)
                all_filings.extend(filings)
                await asyncio.sleep(self.request_delay)
            except Exception as e:
                print(f"Error scraping {form_type} for CIK {cik}: {e}")
                continue
                
        return all_filings
    
    async def _scrape_company_form_type(self, cik: str, form_type: str) -> List[Dict]:
        """
        Scrape filings for a specific company and form type
        """
        filings = []
        
        search_url = f"{self.base_url}/cgi-bin/browse-edgar"
        
        params = {
            'action': 'getcompany',
            'CIK': cik,
            'type': form_type,
            'dateb': '',
            'owner': 'include',
            'count': '40'
        }
        
        try:
            response = requests.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            filings = self._parse_company_filings_response(response.text, form_type, cik)
            
        except requests.RequestException as e:
            print(f"Error fetching {form_type} filings for CIK {cik}: {e}")
            
        return filings
    
    def _parse_company_filings_response(self, response_text: str, form_type: str, cik: str) -> List[Dict]:
        """
        Parse company-specific filing response
        """
        filings = []
        
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            
            # Find the filings table
            tables = soup.find_all('table', class_='tableFile2')
            
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    cells = row.find_all('td')
                    
                    if len(cells) >= 5:  # Ensure we have enough columns
                        filing_data = {
                            'form_type': form_type,
                            'cik': cik,
                            'filing_date': self._parse_date(cells[3].text.strip()),
                            'accession_number': cells[4].text.strip(),
                            'description': cells[2].text.strip(),
                            'source': 'SEC_EDGAR_COMPANY_SPECIFIC'
                        }
                        
                        # Extract document link
                        link = cells[1].find('a')
                        if link:
                            filing_data['url'] = urljoin(self.base_url, link.get('href'))
                        
                        filings.append(filing_data)
                        
        except Exception as e:
            print(f"Error parsing company filings response: {e}")
            
        return filings
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string from SEC format
        """
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%m/%d/%Y')
            except ValueError:
                return None
    
    async def analyze_filing_content(self, filing_url: str) -> Dict:
        """
        Download and analyze the content of a specific filing
        Extract ownership details and investment purpose
        """
        try:
            response = requests.get(filing_url, headers=self.headers)
            response.raise_for_status()
            
            # Parse the filing content
            analysis = self._analyze_filing_text(response.text)
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing filing content: {e}")
            return {}
    
    def _analyze_filing_text(self, content: str) -> Dict:
        """
        Analyze filing text to extract key investment signals
        """
        analysis = {
            'ownership_percent': None,
            'shares_owned': None,
            'purpose': None,
            'investment_intent': None,
            'activist_language': False,
            'control_intent': False
        }
        
        # Extract ownership percentage
        percent_patterns = [
            r'(\d+\.?\d*)\s*%',
            r'(\d+\.?\d*)\s*percent'
        ]
        
        for pattern in percent_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                analysis['ownership_percent'] = float(match.group(1))
                break
        
        # Extract share count
        share_patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*shares',
            r'(\d+)\s*shares'
        ]
        
        for pattern in share_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                shares_str = match.group(1).replace(',', '')
                analysis['shares_owned'] = int(shares_str)
                break
        
        # Analyze purpose and intent
        purpose_section = self._extract_purpose_section(content)
        if purpose_section:
            analysis['purpose'] = purpose_section[:500]  # Limit length
            
            # Check for activist language
            activist_keywords = [
                'strategic alternatives', 'board representation', 'governance',
                'maximize value', 'operational improvements', 'management changes'
            ]
            
            analysis['activist_language'] = any(
                keyword in purpose_section.lower() for keyword in activist_keywords
            )
            
            # Check for control intent
            control_keywords = [
                'control', 'acquire', 'merger', 'takeover', 'proxy'
            ]
            
            analysis['control_intent'] = any(
                keyword in purpose_section.lower() for keyword in control_keywords
            )
        
        return analysis
    
    def _extract_purpose_section(self, content: str) -> Optional[str]:
        """
        Extract the purpose section from filing content
        """
        # Look for common purpose section indicators
        purpose_patterns = [
            r'Item\s*4\.?\s*Purpose[^:]*:?\s*([^<]+)',
            r'Purpose[^:]*:?\s*([^<]+)',
            r'Item\s*4[^:]*([^<]+)'
        ]
        
        for pattern in purpose_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return None