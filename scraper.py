#ppp

import json
import time
import random
import sys
import requests
from bs4 import BeautifulSoup

import os
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_times_of_india(url, max_articles=3):
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch {url}. Status Code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    article_links = soup.find_all("a", href=True)

    article_urls = set()
    for link in article_links:
        href = link["href"]
        if "/articleshow/" in href:
            full_url = href if href.startswith("http") else f"https://timesofindia.indiatimes.com{href}"
            article_urls.add(full_url)
        if len(article_urls) >= max_articles:
            break

    print(f"Found {len(article_urls)} articles on {url}.")

    for article_url in article_urls:
        try:
            article_response = requests.get(article_url, headers=HEADERS)
            if article_response.status_code != 200:
                print(f"❌ Failed to fetch {article_url}. Status Code: {article_response.status_code}")
                continue

            article_soup = BeautifulSoup(article_response.text, "html.parser")

            title_element = article_soup.find("h1")
            title = title_element.get_text(strip=True) if title_element else "Title Not Found"

            content_element = article_soup.find("div", class_="_s30J")
            content = content_element.get_text(" ", strip=True) if content_element else "Content Not Found"

            articles.append({
                "title": title,
                "url": article_url,
                "content": content
            })

            time.sleep(random.uniform(1, 3))  # Mimic human behavior

        except Exception as e:
            print(f"❌ Error scraping {article_url}: {e}")

    return articles

if __name__ == "__main__":
    try:
        with open("urls.json", "r", encoding="utf-8") as f:
            urls = json.load(f)
    except FileNotFoundError:
        print("❌ Error: 'urls.json' file not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON format in 'urls.json'.")
        sys.exit(1)

    all_articles = []
    for url in urls:
        articles = scrape_times_of_india(url)
        all_articles.extend(articles)

    if all_articles:
        with open("toi_articles.json", "w", encoding="utf-8") as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=4)
        print("✅ Scraping completed. Data saved to 'toi_articles.json'.")
    else:
        print("❌ No articles found.")


