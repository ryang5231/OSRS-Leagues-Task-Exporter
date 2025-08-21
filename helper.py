import requests
from openpyxl.styles import Alignment
from requests import RequestException
import re

REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/",
    }

PERCENTAGE_COMPL_FILL_COLOR = {
    "very_rare": "#FF6262", # <0.1%
    "rare": "#FF863C",      # 0.1 - 0.9%
    "uncommon": "#FFED4C",  # 1 - 9.9%
    "common": "#56E156",    # 10 - 49.9%
    "always": "#AFEEEE",    # 50 - 100%
    "default": "#FFFFFF",   # for invalid values
}

def text_cleaner(input_text):
    result = input_text
    # Replace multiple spaces with one space
    result = re.sub(r' +', ' ', result)
    replacements = [
        (" .", "."),
        ("\n", ""),
        ("( ", "("),
        (" )", ")"),
        (" ,", ","),
        (" ;", ";"),
        ('[ ', '['),
        (' ]', ']'),
    ]
    for old, new in replacements:
        result = result.replace(old, new)
    return result.strip()


def fetch_html(task_url):
    response = None
    try: 
        response = requests.get(task_url, headers=REQUEST_HEADERS)
        response.raise_for_status()
    except RequestException as e:
        print(f"Link is not accessible due to: {e}")
    finally:
        if response is not None:
            print(f"Status Code returned: {response.status_code}")
        else:
            print("No response received.")

    return response

def parse_requirements(data_block):
    requirements = data_block.get_text(" ", strip=False)
    spans = data_block.find_all("span")
    for s in spans:
        if len(s['class']) > 3:
            altered = re.sub(r'(\d+)( {1,2})([a-z|\(])', r'\1 coin(s) \3', requirements)
            if (altered == requirements):
                requirements.strip()
                requirements += 'coin(s)'
            else:
                requirements = altered
    return text_cleaner(requirements)

def parse_percent(percent_string):
    if percent_string == "<0.1%":
        return 0.0
    try:
        return float(percent_string.replace('%', '')) / 100.0
    except ValueError:
        return None

def construct_percent_fill_format(percent_string):
    choice = "default"
    num_format = '0%'
    if percent_string == "<0.1%":
        choice = "very_rare"
        return {
                'num_format': num_format,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': PERCENTAGE_COMPL_FILL_COLOR[choice]
            }
    else:
        try:
            percent_string = percent_string.replace('%', '')
            percent = float(percent_string)

            if not percent.is_integer():
                num_format = '0.0%'
            if 0.1 <= percent < 10:
                choice = "rare"
            elif 0.1 <= percent < 10:
                choice = "uncommon"
            elif 10 <= percent < 50:
                choice = "common"
            elif 50 <= percent <= 100:
                choice = "always"
        except:
            print('the percentage could not be converted into a float! returning default colour...')
        finally:
            return {
                'num_format': num_format,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': PERCENTAGE_COMPL_FILL_COLOR[choice]
            }

