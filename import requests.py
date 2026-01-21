import requests
from bs4 import BeautifulSoup
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://www.northeastjobs.org.uk/alljobs"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

resp = requests.get(url, headers=headers, verify=False)
soup = BeautifulSoup(resp.text, "html.parser")

# Find all job cards
job_cards = soup.select("div.job-card-sub")

print(f"Found {len(job_cards)} jobs\n")
print("=" * 80)

for card in job_cards:
    # Job title and link
    title_elem = card.select_one("h5.card-title a")
    title = title_elem.get_text(strip=True) if title_elem else "N/A"
    link = title_elem["href"] if title_elem else "N/A"

    # Closing date
    closing_date = card.select_one("span.font-weight-bold")
    closing = closing_date.get_text(strip=True) if closing_date else "N/A"

    # Extract details from card body
    details = {}
    card_body = card.select_one("div.card-body")
    if card_body:
        labels = card_body.select("span.item_label")
        for label in labels:
            key = label.get_text(strip=True).rstrip(":")
            value_elem = label.find_next_sibling("span")
            value = value_elem.get_text(strip=True) if value_elem else "N/A"
            details[key] = value

    # Short description
    desc_elem = card.select_one("[id*='lblShortDescription']")
    description = desc_elem.get_text(strip=True) if desc_elem else "N/A"

    print(f"Title: {title}")
    print(f"Closing Date: {closing}")
    print(f"Location: {details.get('Employment Location', 'N/A')}")
    print(f"Salary: {details.get('Salary', 'N/A')}")
    print(f"Working Pattern: {details.get('Working Pattern', 'N/A')}")
    print(f"Contract Type: {details.get('Contract Type', 'N/A')}")
    print(f"Category: {details.get('Job category', 'N/A')}")
    print(f"Description: {description[:150]}...")
    print(f"Link: {link}")
    print("=" * 80)
