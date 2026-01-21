import requests
from bs4 import BeautifulSoup

url = "https://www.northeastjobs.org.uk/alljobs"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

resp = requests.get(url, headers=headers, verify=False)
soup = BeautifulSoup(resp.text, "html.parser")

# Example: find job containers
jobs = soup.select("div.jobsearch-result, li.job-listing")  # placeholder selectors
for job in jobs:
    title = job.get_text(strip=True)
    print(title)
