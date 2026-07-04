#This is a generalized website scraper code, the objective of this code is to scrape the data from the website and store it in a structured format. 
# The code uses BeautifulSoup and requests libraries to scrape the data from the website.
#You just need to save this code in your system and provide the URL of the website you want to scrape and it will return data in json format.

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class GeneralizedWebCrawler:
    def __init__(self, start_url):
        # Normalize the starting URL (remove trailing slashes for consistency)
        self.start_url = start_url.rstrip("/")
        # Extract the core domain network location (e.g., 'kleosly.com') to block external sites
        self.base_domain = urlparse(self.start_url).netloc
        self.visited_urls = set()
        self.scraped_pages_payload = []

    def clean_and_extract_text(self, soup):
        """Strips out visual formatting noise to leave pure strategic text data."""
        # Remove structural and dynamic webpage noise elements
        for tag in soup(["script", "style", "nav", "footer", "header", "svg", "form"]):
            tag.decompose()

        # Pull text with clean spacing
        return soup.get_text(separator=" ", strip=True)

    def scrape_single_page(self, url):
        """Safely fetches a single URL with strict timeouts and error safety nets."""
        try:
            # User-Agent header prevents standard web firewalls from blocking the request
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            }
            # 10-second timeout prevents the pipeline from freezing on broken links
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"  [!] Skipping {url} - Server returned status: {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract basic metadata
            title = soup.title.string.strip() if soup.title else "No Title Found"

            # Isolate primary semantic text headers (H1 and H2 markers)
            headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2"]) if h.get_text(strip=True)]

            # Get the clean body corpus
            body_content = self.clean_and_extract_text(soup)

            return {
                "url": url,
                "title": title,
                "headings": headings,
                "content": body_content
            }
        except Exception as e:
            print(f"  [!] Error reading page contents at {url}: {e}")
            return None

    def get_valid_internal_links(self, url):
        """Scans page HTML and harvests links belonging strictly to the same client domain."""
        internal_links = set()
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()

                # Turn relative sub-paths (like '/about') into full absolute URLs
                full_url = urljoin(self.start_url, href)
                parsed_url = urlparse(full_url)

                # Check 1: Must match client base domain (prevents jumping to LinkedIn/Twitter mid-crawl)
                # Check 2: Skip media file links or download paths that cause crashes
                if parsed_url.netloc == self.base_domain:
                    clean_url = full_url.split('#')[0].rstrip("/") # Strip anchor links
                    if not any(clean_url.lower().endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.jpeg', '.zip']):
                        internal_links.add(clean_url)

            return internal_links
        except Exception:
            return set()

    def run_crawl_loop(self, max_pages=15):
        """Runs an optimized breadth-first crawl loop across the target domain structure."""
        to_visit_queue = {self.start_url}
        print(f"Starting Generalized Crawl Pipeline on: {self.start_url}")
        print(f"Targeting Domain Authority Scope: {self.base_domain}\n")

        while to_visit_queue and len(self.visited_urls) < max_pages:
            current_url = to_visit_queue.pop()

            if current_url in self.visited_urls:
                continue

            print(f" -> Processing Page: {current_url}")
            self.visited_urls.add(current_url)

            # Execute data extraction
            page_data = self.scrape_single_page(current_url)
            if page_data:
                self.scraped_pages_payload.append(page_data)

            # Discover nested pathways
            discovered_links = self.get_valid_internal_links(current_url)

            # Add unexplored paths into the execution loop
            to_visit_queue.update(discovered_links - self.visited_urls)

        print(f"\n[+] Crawl Complete. Successfully mapped {len(self.scraped_pages_payload)} pages.")
        return self.scraped_pages_payload

    def export_to_json(self, company_name, filename="website_data.json"):
        """Compiles standard dictionary payload directly to your workspace folder."""
        output = {
            "company": company_name,
            "website_url": self.start_url,
            "total_pages": len(self.scraped_pages_payload),
            "pages": self.scraped_pages_payload
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"[+] Operational reality state successfully compiled to '{filename}'")

# ==================== PIPELINE LAUNCH VEHICLE ====================
if __name__ == "__main__":
    print("=========================================")
    print("   WEB AUDIT INGESTION ARCHITECTURE   ")
    print("=======================================\n")

    COMPANY_NAME = input("Enter Company Name: ").strip()
    TARGET_WEBSITE = input("Enter Base Website URL (e.g., https://example.com): ").strip()

    if not COMPANY_NAME or not TARGET_WEBSITE:
        print("[!] Initialization Error: Parameters cannot be blank.")
    else:
        crawler = GeneralizedWebCrawler(TARGET_WEBSITE)
        crawler.run_crawl_loop(max_pages=15)


        cloud_filename = "/content/*YOUR_STORAGE_PATH*/"
        crawler.export_to_json(COMPANY_NAME, filename=cloud_filename)