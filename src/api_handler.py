import requests
import os
from typing import List, Dict
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def search_google(queries: List[str], related_name: str) -> List[Dict]:
    """Execute Google searches using SerpAPI"""
    results = []
    serpapi_key = os.getenv("SERPAPI_KEY")
    
    for query in queries[:10]:  # Limit to 10 searches
        search_url = "https://serpapi.com/search"
        params = {
            "q": f"Get me the {related_name} of {query}",
            "api_key": serpapi_key
        }
        
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'organic_results' in data:
                for result in data['organic_results']:
                    results.append([
                        result['title'],
                        result['link'],
                        result['snippet']
                    ])
        except Exception as e:
            print(f"Error searching for {query}: {e}")
            
    return results

def connect_google_sheets(sheet_name: str):
    """Connect to Google Sheets"""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1
