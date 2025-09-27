import sys
from typing import Optional, List

from bs4 import BeautifulSoup
import requests
import json
from pydantic import BaseModel, ValidationError


class Publication(BaseModel):
    title: str
    link: str
    summary: Optional[str] = None

    def model_dump(self, **kwargs):
        return super().model_dump(**kwargs)


def _parse_publications_from_soup(url: str) -> List[Publication]:
    print(f"[*] Processing: {url}")
    if url.startswith('http'):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            content = response.content
            print(f"[+] Data successfully received over the network.")
        except requests.RequestException as e:
            print(f"[!] Network error: {e}")
            return []
    else:
        try:
            with open(url, 'rb') as file:
                content = file.read()
            print(f"[+] Data successfully read from local file.")
        except FileNotFoundError as e:
            print(f"[!] File error: {e}")
            return []

    soup = BeautifulSoup(content, 'lxml-xml')
    publications: List[Publication] = []

    for entry in soup.find_all('entry'):
        try:
            title_tag = entry.select_one('title')
            link_tag = entry.select_one('link[rel="alternate"]')
            summary_tag = entry.select_one('summary')

            if not (title_tag and link_tag and link_tag.has_attr('href')):
                print("[!] Missing entry: no title or link.")
                continue

            publication_data = {
                "title": title_tag.get_text(strip=True),
                "link": link_tag['href'],
                "summary": summary_tag.get_text(strip=True) if summary_tag else 'No text available.'
            }

            publications.append(Publication(**publication_data))
        except ValidationError as ve:
            print(f"[!] Validation error: {ve}")
    print(f"[+] Parsing complete. Publications found: {len(publications)}.")
    return publications


if __name__ == '__main__':
    FEED_URL = "https://scipost.org/atom/publications/comp-ai"
    target = sys.argv[1] if len(sys.argv) > 1 else FEED_URL

    pubs = _parse_publications_from_soup(target)

    if pubs:
        data = [p.model_dump() for p in pubs]
        print("\n--- Results ---")
        print(json.dumps(data, ensure_ascii=False, indent=2))
