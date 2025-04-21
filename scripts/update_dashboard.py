import feedparser
import requests
import re

# URLs for RSS feeds
CVE_FEED_URL = "https://cve.mitre.org/data/downloads/allitems.xml"
NEWS_FEED_URL = "https://www.cisa.gov/news.xml"

def fetch_feed_entries(feed_url, max_entries=5):
    feed = feedparser.parse(feed_url)
    entries = []
    for entry in feed.entries[:max_entries]:
        title = entry.title
        link = entry.link
        entries.append(f"- [{title}]({link})")
    return entries

def update_section(content, marker_start, marker_end, new_lines):
    pattern = f"{marker_start}.*?{marker_end}"
    replacement = f"{marker_start}\n" + "\n".join(new_lines) + f"\n{marker_end}"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def main():
    # Fetch latest CVEs and news
    cve_entries = fetch_feed_entries(CVE_FEED_URL)
    news_entries = fetch_feed_entries(NEWS_FEED_URL)

    # Read the existing index.md
    with open("index.md", "r", encoding="utf-8") as file:
        content = file.read()

    # Update the CVE and news sections
    content = update_section(content, "<!-- CVE_LIST_START -->", "<!-- CVE_LIST_END -->", cve_entries)
    content = update_section(content, "<!-- NEWS_LIST_START -->", "<!-- NEWS_LIST_END -->", news_entries)

    # Write the updated content back to index.md
    with open("index.md", "w", encoding="utf-8") as file:
        file.write(content)

if __name__ == "__main__":
    main()
