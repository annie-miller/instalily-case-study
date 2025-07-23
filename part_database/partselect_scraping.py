import requests
from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = "https://www.partselect.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/"
}

session = requests.Session()
response = session.get(BASE_URL, headers=HEADERS)
print(response.status_code)
print(response.text[:500])  # Print first 500 chars for debugging

def get_soup(url):
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def get_category_links():
    soup = get_soup(BASE_URL)
    # Find links to main appliance categories (e.g., Refrigerator, Dishwasher)
    links = []
    for a in soup.select("a[href^='/']"):
        href = a.get("href")
        if href and ("/Refrigerator-" in href or "/Dishwasher-" in href):
            full_url = BASE_URL + href
            if full_url not in links:
                links.append(full_url)
    return links

def get_part_links(category_url):
    soup = get_soup(category_url)
    links = []
    # Find links to part pages (may need to adjust selector for real site)
    for a in soup.select("a[href^='/PS']"):
        href = a.get("href")
        if href and href.startswith("/PS"):
            full_url = BASE_URL + href
            if full_url not in links:
                links.append(full_url)
    return links

def scrape_part_page(part_url):
    soup = get_soup(part_url)
    # Example selectors, adjust as needed for real site structure
    part_number = soup.select_one(".ps-part-number")
    name = soup.select_one("h1")
    description = soup.select_one(".ps-part-description")
    price = soup.select_one(".ps-part-price")
    # Add more fields as needed

    return {
        "url": part_url,
        "part_number": part_number.text.strip() if part_number else "",
        "name": name.text.strip() if name else "",
        "description": description.text.strip() if description else "",
        "price": price.text.strip() if price else "",
    }

def main():
    all_parts = []
    category_links = get_category_links()
    print(f"Found {len(category_links)} category links.")

    for cat_url in category_links:
        print(f"Scraping category: {cat_url}")
        part_links = get_part_links(cat_url)
        print(f"  Found {len(part_links)} part links.")
        for part_url in part_links:
            print(f"    Scraping part: {part_url}")
            try:
                part_data = scrape_part_page(part_url)
                all_parts.append(part_data)
                time.sleep(1)  # Be polite!
            except Exception as e:
                print(f"      Error scraping {part_url}: {e}")

    # Save to JSON
    with open("partselect_parts.json", "w", encoding="utf-8") as f:
        json.dump(all_parts, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_parts)} parts to partselect_parts.json")

if __name__ == "__main__":
    options = Options()
    # Do NOT add --headless
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com")
    print(driver.title)
    driver.quit()

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.partselect.com/")
    time.sleep(3)  # Wait for JS to load, adjust as needed

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Now you can use soup to extract links, text, etc.
    print(soup.get_text()[:500])  # Print first 500 chars for debugging

    driver.quit()