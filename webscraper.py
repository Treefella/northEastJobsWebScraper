import asyncio
import random
import logging
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class CWJobsScraper:
    def __init__(self):
        self.jobs = []  # In-memory storage for testing

    async def scrape_cwjobs(self, role, area, pages=1):
        """Scrape CWJobs for a given role and area; store results in memory."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent="Mozilla/5.0 ...")
            page = await context.new_page()

            try:
                for i in range(1, pages + 1):
                    url = f"https://www.cwjobs.co.uk/jobs/{role.replace(' ', '-')}/in-{area}?page={i}"
                    logging.info(f"Scraping page {i}: {url}")

                    try:
                        await page.goto(url)
                        await asyncio.sleep(random.uniform(2, 4))  # Random jitter
                    except Exception as e:
                        logging.error(f"Failed to load page {i}: {e}")
                        continue

                    soup = BeautifulSoup(await page.content(), "html.parser")
                    cards = soup.select('article[data-testid="job-card"]')

                    for card in cards:
                        link_tag = card.select_one('a')
                        job = {
                            "title": card.select_one('h2').get_text(strip=True) if card.select_one('h2') else "N/A",
                            "company": card.select_one('[data-testid="company-name"]').get_text(strip=True) if card.select_one('[data-testid="company-name"]') else "N/A",
                            "location": card.select_one('[data-testid="job-location"]').get_text(strip=True) if card.select_one('[data-testid="job-location"]') else "N/A",
                            "link": f"https://www.cwjobs.co.uk{link_tag['href']}" if link_tag else "N/A"
                        }
                        self.jobs.append(job)

                    logging.info(f"Page {i} scraped; {len(cards)} jobs found.")
            finally:
                await browser.close()
                logging.info("Browser closed.")

# --- Execution for Testing ---
if __name__ == "__main__":
    async def main():
        scraper = CWJobsScraper()
        await scraper.scrape_cwjobs("Python Developer", "London", pages=2)

        # Print scraped jobs for testing
        for idx, job in enumerate(scraper.jobs, 1):
            print(f"{idx}. {job['title']} | {job['company']} | {job['location']} | {job['link']}")

    asyncio.run(main())
