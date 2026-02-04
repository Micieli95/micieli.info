import json
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

PROFILE_URL = "https://stadtrat.bern.ch/de/mitglieder/detail.php?gid=6b765a1f5faa4237a53ae99411f6ef04"
BASE = "https://stadtrat.bern.ch/"

def main():
    html = requests.get(PROFILE_URL, timeout=30).text
    soup = BeautifulSoup(html, "lxml")

    # Try to locate heading 'Vorstösse'
    heading = soup.find(lambda t: t.name in ("h2", "h3") and t.get_text(strip=True) == "Vorstösse")
    if heading:
        links = []
        # collect all anchor tags after heading until another heading of the same or higher level
        for sibling in heading.find_all_next():
            if sibling.name in ("h2", "h3") and sibling is not heading:
                break
            if sibling.name == 'a' and sibling.has_attr('href'):
                links.append(sibling)
    else:
        # fallback: gather all anchors on page
        links = soup.find_all("a", href=True)

    items = []
    for a in links:
        title = a.get_text(" ", strip=True)
        href = a['href'].strip()
        if not title:
            continue
        # heuristics: pick titles referencing SR (Vorstoss)
        if 'SR.' in title or re.search(r"\d{4}\.SR\.", title):
            items.append({
                "title": title,
                "url": urljoin(BASE, href)
            })

    # remove duplicates while preserving order
    seen = set()
    uniq = []
    for it in items:
        if it['url'] not in seen:
            uniq.append(it)
            seen.add(it['url'])

    with open('data/vorstoesse.json', 'w', encoding='utf-8') as f:
        json.dump(uniq, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
