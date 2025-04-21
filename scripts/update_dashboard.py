import feedparser
import re

# Corrected RSS feeds URLs
CVE_FEED = "https://cve.trendmicro.com/rss"
NEWS_FEED = "https://www.cisa.gov/uscert/ncas/alerts.xml"

def fetch_entries(feed_url, max_entries=5):
    feed = feedparser.parse(feed_url)
    entries = []
    for entry in feed.entries[:max_entries]:
        title = getattr(entry, 'title', 'No Title')
        link = getattr(entry, 'link', '#')
        entries.append(f"- [{title}]({link})")
    return entries

def update_markdown(file_path, start_tag, end_tag, new_content):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    updated_content = re.sub(
        f"{start_tag}[\\s\\S]*?{end_tag}",
        f"{start_tag}\n{new_content}\n{end_tag}",
        content,
        flags=re.MULTILINE
    )

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_content)

if __name__ == "__main__":
    cves = fetch_entries(CVE_FEED)
    news = fetch_entries(NEWS_FEED)

    update_markdown("index.md", "<!-- CVE_LIST_START -->", "<!-- CVE_LIST_END -->", "\n".join(cves))
    update_markdown("index.md", "<!-- NEWS_LIST_START -->", "<!-- NEWS_LIST_END -->", "\n".join(news))
