#this is a playwright scraper that will scrape linkedin profiles and company pages for metadata and recent posts. 
# It will also save the session cookies to a local folder to bypass login in future runs.
#you just need to provide the linkedin profile url and company url and it will return data in json format.
#This scraper mainly works to collect data from founder profiles and their associated company pages, 
# including metadata, recent posts, and other relevant information.
#The scraper uses Playwright to automate browser interactions and handle dynamic content loading.

import asyncio
import json
import random
import os

try:
    from playwright.async_api import async_playwright
except ImportError as e:
    raise ImportError(
        "playwright is required for linkedin_scrape.py. "
        "Install it with `pip install playwright` and then run "
        "`playwright install chromium`."
    ) from e

class LinkedInPersistentScraper:
    def __init__(self, user_data_dir="./linkedin_profile"):
        # Local folder to save session cookies and bypass logins going forward
        self.user_data_dir = user_data_dir

    async def human_scroll(self, page, scroll_times=4):
        """Simulates variable human scrolling velocity to load content safely."""
        for _ in range(scroll_times):
            scroll_distance = random.randint(300, 600)
            await page.evaluate(f"window.scrollBy(0, {scroll_distance});")
            await asyncio.sleep(random.uniform(1.5, 3.0))

    async def scrape_pipeline(self, founder_url, company_url):
        async with async_playwright() as p:
            print(f"Launching stealth browser session linked to: {self.user_data_dir}...")
            
            # Use persistent context to remember your browser cookies natively
            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            
            page = context.pages[0] if context.pages else await context.new_page()

        # --- STEP 1: RESILIENT SESSION AUTOPASS ---
            print("Verifying session baseline...")
            try:
                await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)
            except Exception:
                print("Initial dashboard ping was sluggish, checking active URL context...")

            # Smart check: If 'feed' OR a profile link ('/in/') is in the current URL, we are authenticated!
            if "linkedin.com/feed" in page.url or "linkedin.com/in/" in page.url:
                print("Active browser profile detected! Skipping login fields entirely.\n")
            else:
                print("\n[ACTION REQUIRED] Active session state not found in local profile.")
                print("Please fill out credentials and log in manually in the browser window now.")
                print("Waiting for you to successfully clear walls and hit the main feed...")
                
                try:
                    # Accepts landing on feed or any profile page after manual login
                    await page.wait_for_function(
                        "() => window.location.href.includes('linkedin.com/feed') || window.location.href.includes('linkedin.com/in/')",
                        timeout=120000
                    )
                    print("Login verified! Caching environment cookies...\n")
                    await asyncio.sleep(3)
                except Exception as e:
                    print(f"Auth verification link check timed out: {e}")
                    
            # --- STEP 2: SCRAPE FOUNDER PROFILE METADATA ---
            print(f"Routing to founder profile: {founder_url}")
            try:
                await page.goto(founder_url.rstrip('/'), wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(random.randint(3, 5))
                await self.human_scroll(page, scroll_times=2)
            except Exception as e:
                print(f"Warning: Founder page loading timed out or was slow: {e}. Attempting extraction anyway.")

            # --- IMPROVED RESILIENT NAME EXTRACTION ---
            name = "Unknown Founder"
            try:
                # Strategy A: Check common profile identity selectors
                # Strategy B: Fall back to the absolute first visible H1 tag inside the main content frame
                # Strategy C: Check the document title as a final safety net
                name_selectors = [
                    "h1.text-heading-xlarge", 
                    "section.profile-card h1",
                    "main h1", 
                    "h1"
                ]
                
                for selector in name_selectors:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        raw_name = await element.inner_text()
                        if raw_name and len(raw_name.strip()) > 0:
                            name = raw_name.strip()
                            break
                
                # Final safety valve: If still unknown, pull from the browser tab title ("Name | LinkedIn")
                if name == "Unknown Founder":
                    page_title = await page.title()
                    if "|" in page_title:
                        name = page_title.split("|")[0].strip()
            except Exception as e:
                print(f"Name extraction adjustment notice: {e}")
            
            # --- IMPROVED RESILIENT HEADLINE EXTRACTION ---
            headline = "No Headline"
            try:
                headline_selectors = [
                    ".text-body-medium[data-generated-headline-text]", # Modern standard desktop layout
                    ".text-body-medium",                               # Generic fallback variant
                    "div.ph5.pb5 div.text-body-medium",                # Specific top-card hierarchy container
                    "[data-generated-headline-text]",
                    "section.profile-card p",                          # Minimal view layout variant
                ]
                
                for selector in headline_selectors:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        raw_headline = await element.inner_text()
                        if raw_headline and len(raw_headline.strip()) > 0:
                            headline = raw_headline.strip()
                            break
            except Exception as e:
                print(f"Headline extraction adjustment notice: {e}")
            
            # --- IMPROVED RESILIENT ABOUT EXTRACTION ---
            about_text = ""
            try:
                about_selectors = [
                    # Strategy A: Target the structural companion text box anchored directly next to the ID marker
                    "#about ~ div .inline-show-more-text span[aria-hidden='true']",
                    "#about ~ div .inline-show-more-text",
                    # Strategy B: Legacy layout specific class wrappers
                    ".pv-about__summary-text span",
                    ".pv-about__summary-text",
                    # Strategy C: Top semantic block wrappers fallback
                    "section#about-section div.display-flex span",
                    "section.bany-about-card div span"
                ]
                
                for selector in about_selectors:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        raw_about = await element.inner_text()
                        if raw_about and len(raw_about.strip()) > 0:
                            # Clean up read-more truncation anchors
                            about_text = raw_about.replace("…see more", "").replace("...see more", "").strip()
                            break
            except Exception as e:
                print(f"About section extraction adjustment notice: {e}")

            founder_meta = {
                "name": name,
                "headline": headline,
                "about": about_text,
                "background_signals": []
            }
            print(f"[+] Profile Extraction Complete -> Name: {name}")

            # --- STEP 3: SCRAPE FOUNDER RECENT POSTS ---
            founder_posts_url = f"{founder_url.rstrip('/')}/recent-activity/all/"
            print(f"Routing to founder posts stream: {founder_posts_url}")
            try:
                await page.goto(founder_posts_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(random.randint(3, 5))
                await self.human_scroll(page, scroll_times=4)
            except Exception as e:
                print(f"Warning: Posts page took too long loading assets: {e}. Moving to parsing content.")

            founder_posts = []
            try:
                post_locators = page.locator(".update-v2-social-activity .break-words, .feed-shared-update-v2 .break-words, [id^='ember'] .break-words, .occludable-update .break-words")
                count = await post_locators.count()
                print(f"Identified {count} visible layout text containers.")
                
                for i in range(min(count, 15)): 
                    raw_text = await post_locators.nth(i).inner_text()
                    clean_text = raw_text.replace("…see more", "").strip()
                    if len(clean_text) > 30 and clean_text not in [p["content"] for p in founder_posts]:
                        founder_posts.append({
                            "post_idx": len(founder_posts) + 1,
                            "content": clean_text
                        })
            except Exception as e:
                print(f"Error parsing founder updates: {e}")

            # --- STEP 4: SCRAPE CORPORATE COMPANY POSTS ---
            company_posts_url = f"{company_url.rstrip('/')}/posts/?feedView=all"
            print(f"Routing to company posts stream: {company_posts_url}")
            try:
                await page.goto(company_posts_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(random.randint(3, 5))
                await self.human_scroll(page, scroll_times=4)
            except Exception as e:
                print(f"Warning: Corporate updates stream loading context delayed: {e}.")

            company_posts = []
            try:
                comp_locators = page.locator(".feed-shared-update-v2 .break-words, .update-v2-social-activity .break-words")
                comp_count = await comp_locators.count()
                print(f"Identified {comp_count} corporate update text blocks.")

                for i in range(min(comp_count, 15)):
                    raw_text = await comp_locators.nth(i).inner_text()
                    clean_text = raw_text.replace("…see more", "").strip()
                    if len(clean_text) > 30 and clean_text not in [p["content"] for p in company_posts]:
                        company_posts.append({
                            "post_idx": len(company_posts) + 1,
                            "content": clean_text
                        })
            except Exception as e:
                print(f"Error parsing corporate profile: {e}")

            # Shutdown context cleanly saving the current session
            await context.close()

            return {
                "founder_metadata": founder_meta,
                "founder_posts": founder_posts,
                "company_posts": company_posts
            }

# ==================== RUN VEHICLE ====================
if __name__ == "__main__":
    print("\n==============================================")
    print(" NARRATIVE DATA COLLECTION UTILITY ")
    print("==============================================\n")
    
    TARGET_FOUNDER = input("Enter Target Founder Profile URL: ").strip()
    TARGET_COMPANY = input("Enter Target Company LinkedIn URL: ").strip()

    if not TARGET_FOUNDER or not TARGET_COMPANY:
        print("\n[!] Execution Terminated: Fields cannot be submitted blank.")
    else:
        # Spawns local directory to track your authenticated profile state natively
        scraper = LinkedInPersistentScraper(user_data_dir="./linkedin_profile")
        try:
            final_payload = asyncio.run(scraper.scrape_pipeline(TARGET_FOUNDER, TARGET_COMPANY))
            
            output_filename = "linkedin_data_hand_off.json"
            with open(output_filename, "w", encoding="utf-8") as file:
                json.dump(final_payload, file, indent=2, ensure_ascii=False)
                
            print(f"\n[+] Production Capture Finished! File Exported: '{output_filename}'")
            
        except Exception as err:
            print(f"\n[!] Critical infrastructure error: {err}")

# Update this path string to target your desktop Shared Drive mount location
DRIVE_SYNC_FOLDER = "YOUR_STORAGE_PATH"  