import httpx
from bs4 import BeautifulSoup
import sys
import asyncio

async def check_site():
    url = 'https://python.langchain.com/docs/introduction/'
    print(f"Checking {url}...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
        try:
            r = await client.get(url, headers=headers)
            print(f"Status Code: {r.status_code}")
            
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else 'No Title'
            print(f"Page Title: {title}")
            
            # Check for SSR content
            article = soup.select_one('article')
            if article:
                print(f"Content found (SSR confirmed). Article length: {len(article.get_text())}")
            else:
                print("No content found (Likely CSR/JS-required).")
                
        except Exception as e:
            print(f"Error fetching: {e}")

if __name__ == "__main__":
    asyncio.run(check_site())
