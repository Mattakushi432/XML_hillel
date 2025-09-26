import os
from typing import Optional, List, Set

from bs4 import BeautifulSoup
import requests
import json
from pydantic import BaseModel, HttpUrl, ValidationError


class Publication(BaseModel):
    title: str
    link: str
    summary: Optional[str] = None

    def model_dump(self, **kwargs):
        return super().model_dump(**kwargs)


def parse_publication(url: str) -> List[Publication]:
    print(f"[*] Getting data from {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"[+] Data successfully received.")
    except requests.RequestException as e:
        print(f"[!] Error fetching data: {e}")
        raise

    print(f"[*] Let's start parsing XML using BeautifulSoup...")
    soup = BeautifulSoup(response.content, 'xml')
    publications: List[Publication]
    entries: soup.find_all('entry')
    for entry in entries:
        try:
            title = entry.find('title').get_text(strip=True)
            link_tag = entry.find('link', {'rel': 'alternate'})
            link = link_tag['href'] if link_tag else None
            summary_tag = entry.find('summary')
            summary = summary_tag.get_text(strip=True) if summary_tag else 'No text available.'
            publication_data = {'title': title, 'link': link, 'summary': summary}
            publications.append(Publication(**publication_data))
        except (AttributeError, ValidationError) as e:
            print(f"[!] Error parsing entry: {e}")
        print(f"[+] Parsing completed. Publications found: {len(publications)}.")
            continue