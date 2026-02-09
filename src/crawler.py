import asyncio
import os
from crawl4ai import AsyncWebCrawler
from urllib.parse import urljoin, urlparse
import argparse
import httpx
import xml.etree.ElementTree as ET

# Configuration
BASE_URL = "https://docs.langchain.com/oss/python/langchain/overview"
SITEMAP_URL = "https://docs.langchain.com/sitemap.xml"
OUTPUT_DIR = os.path.join("data", "docs")

async def get_sitemap_urls(sitemap_url):
    try:
        print(f"Fetching sitemap from {sitemap_url}...")
        async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
            response = await client.get(sitemap_url)
            if response.status_code == 200:
                # Mintlify specific: sometimes sitemap is an index of other sitemaps
                # But usually it lists pages directly.
                root = ET.fromstring(response.content)
                # Namespace handling
                namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                urls = []
                for url in root.findall('ns:url', namespace):
                    loc = url.find('ns:loc', namespace).text
                    # Filter for Python docs specifically
                    if loc and "/oss/python/" in loc:
                         urls.append(loc)
                print(f"Found {len(urls)} URLs in sitemap.")
                return urls
            else:
                print(f"Failed to fetch sitemap: {response.status_code}")
                return []
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []

async def crawl_langchain_docs(max_pages):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    visited = set()
    
    # Strategy 1: Sitemap
    sitemap_urls = await get_sitemap_urls(SITEMAP_URL)
    if sitemap_urls:
         # Prioritize sitemap URLs but respect limit
         queue = sitemap_urls[:max_pages]
         # Use set for quick lookup
         queue_set = set(queue)
    else:
         # Fallback Strategy 2: BFS from Base URL
         queue = [BASE_URL]
         queue_set = {BASE_URL}
    
    print(f"Starting crawl with {len(queue)} initial URLs...")
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        while queue and len(visited) < max_pages:
            current_url = queue.pop(0)
            
            # Normalization
            clean_url = current_url.split('#')[0]
            if clean_url.endswith("/"):
                clean_url = clean_url[:-1]
                
            if clean_url in visited:
                continue
            
            visited.add(clean_url)
            print(f"[{len(visited)}/{max_pages}] Crawling: {current_url}")
            
            try:
                # Mintlify specific JS to ensure sidebar is loaded
                js_wait_sidebar = """
                await new Promise(r => setTimeout(r, 2000));
                """
                
                result = await crawler.arun(
                    url=current_url,
                    js_code=js_wait_sidebar,
                    # Remove css_selector to ensure we get all links (sidebar, etc.)
                    # We will filter content via regex/parsing later
                    bypass_cache=False
                )
                
                if not result.success:
                    print(f"Failed: {result.error_message}")
                    continue
                
                # Post-processing to remove Mintlify noise that selectors missed
                cleaned_markdown = result.markdown
                
                # Remove "Copy page" artifacts
                cleaned_markdown = cleaned_markdown.replace("Copy page\n", "")
                
                # Remove "Skip to main content"
                if "Skip to main content" in cleaned_markdown:
                    cleaned_markdown = cleaned_markdown.split("Skip to main content")[-1]

                # Remove Footer (Heuristic: "Was this page helpful?")
                if "Was this page helpful?" in cleaned_markdown:
                    cleaned_markdown = cleaned_markdown.split("Was this page helpful?")[0]
                    
                # Save Markdown
                path = urlparse(current_url).path.strip("/")
                if not path:
                    filename = "index.md"
                else:
                    filename = path.replace("/", "_") + ".md"
                
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                # Add Metadata
                title = result.metadata.get('title', 'No Title')
                content = f"---\nurl: {current_url}\ntitle: {title}\n---\n\n{cleaned_markdown.strip()}"
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                    
                # Extract Links (Only if we are in BFS mode or want to expand beyond sitemap)
                # If we have a massive queue from sitemap, skipping this might be faster?
                # But sitemaps can be stale. Let's keep extraction but be smart.
                if result.links:
                    # print(f"Found {len(result.links)} links on {current_url}")
                    for link in result.links:
                        # Handle link structure safely
                        if isinstance(link, str):
                            href = link
                        elif isinstance(link, dict):
                            href = link.get('href')
                        else:
                            continue
                            
                        if not href:
                            continue
                        
                        full_url = urljoin(current_url, href)
                        parsed = urlparse(full_url)
                        
                        # Updated filter for docs.langchain.com/oss/python/
                        if (parsed.netloc == "docs.langchain.com" and 
                            "/oss/python/" in parsed.path):
                            
                            clean_link = full_url.split('#')[0]
                            if clean_link.endswith("/"):
                                clean_link = clean_link[:-1]
                                
                            if clean_link not in visited and clean_link not in queue_set:
                                 queue.append(clean_link)
                                 queue_set.add(clean_link)
                else:
                    pass # Silence noisy output

            except Exception as e:
                print(f"Error processing {current_url}: {e}")

    print(f"Crawl complete. {len(visited)} pages saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangChain Docs Crawler")
    parser.add_argument("--limit", type=int, default=300, help="Max pages to crawl (default: 300)")
    parser.add_argument("--all", action="store_true", help="Crawl all pages (overrides --limit)")
    
    args = parser.parse_args()
    
    if args.all:
        max_p = 10000 
        print("Crawling ALL pages (limit set to 10000)")
    else:
        max_p = args.limit
        print(f"Crawling with limit: {max_p}")
        
    asyncio.run(crawl_langchain_docs(max_p))
