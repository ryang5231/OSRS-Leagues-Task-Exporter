import requests
from bs4 import BeautifulSoup
import pandas as pd

TASK_DIFFICULTY_IDX = 0

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                   (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}

url = 'https://oldschool.runescape.wiki/w/Shattered_Relics_League/Tasks'
response = requests.get(url, headers=headers)

# print(response.status_code)
# print(response.content)

soup = BeautifulSoup(response.content, 'html.parser')

# full div with point info and task descr
rows = soup.find_all("tr", attrs={"data-taskid": True})

# point info: span title
# text within td
for r in rows[:1]:
    task_wording = r.find_all("td", attrs={"data-sort-value": True})
    if task_wording:
        # Access nested span
        task_difficulty = task_wording[TASK_DIFFICULTY_IDX].find("span", title=True)["title"]
    verbose_description = r.find("td", attrs={}).get_text(" ", strip=True)

# print(soup.prettify())

