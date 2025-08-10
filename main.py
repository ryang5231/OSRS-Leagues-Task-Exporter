import requests
from bs4 import BeautifulSoup
import pandas as pd

TASK_DIFFICULTY_IDX = 0
VERBOSE_IDX = 1
SKILL_REQUIREMENT_IDX = 2

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
points_reference = {
                    "Beginner": 5,
                    "Easy": 5,
                    "Medium": 25,
                    "Hard": 50,
                    "Elite": 125,
                    "Master": 250
                    }

# point info: span title
# text within td
for r in rows[1:2]:
    cols = r.find_all("td")
    # task_info = r.find_all("td", attrs={"data-sort-value": True})
    if cols:
        task_difficulty = cols[TASK_DIFFICULTY_IDX].find("span", title=True)["title"]
        task_title = cols[TASK_DIFFICULTY_IDX].get_text(" ", strip=True)
        points = points_reference[task_difficulty]
        verbose = cols[VERBOSE_IDX].get_text(" ", strip=False)

# print(soup.prettify())

