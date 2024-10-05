import requests
import sqlite3
from bs4 import BeautifulSoup
from urllib.parse import urljoin

DB_FILE = "search_engine.db"
START_URL = "https://www.startpage.com/"


def create_table():
    """Create the database table if it does not exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            url TEXT,
            title TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()


def fetch_page(session, url):
    """Fetch page content using a session and handle errors."""
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def save_page_to_db(url, title, content):
    """Save page title and content to the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO documents (url, title, content) VALUES (?, ?, ?)",
        (url, title, content),
    )
    conn.commit()
    conn.close()


def parse_and_get_links(content, base_url):
    """Parse HTML content and extract links."""
    soup = BeautifulSoup(content, "html.parser")
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if not (href.startswith("mailto:") or href.startswith("javascript:")):
            full_url = urljoin(base_url, href)
            links.add(full_url)
    return links


def crawl(start_url):
    """Crawl pages starting from the given URL using a session."""
    create_table()
    urls_to_crawl = {start_url}
    crawled_urls = set()

    # Create a session
    with requests.Session() as session:
        while urls_to_crawl:
            url = urls_to_crawl.pop()
            if url in crawled_urls:
                continue
            print(f"Crawling {url}")
            content = fetch_page(session, url)
            if content:
                soup = BeautifulSoup(content, "html.parser")
                title = soup.title.string if soup.title else url
                save_page_to_db(url, title, content)
                links = parse_and_get_links(content, url)
                # Add all new links to the queue
                urls_to_crawl.update(links)
            crawled_urls.add(url)


if __name__ == "__main__":
    crawl(START_URL)
