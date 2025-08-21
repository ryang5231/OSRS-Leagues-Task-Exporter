import requests
from requests import RequestException
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    result = re.sub(r',( {0,})$', '', result)
    replacements = [
        (" .", "."),
        ("\n", ""),
        ("( ", "("),
        (" )", ")"),
        (" ,", ","),
        (" ;", ";"),
        ('[ ', '['),
        (' ]', ']'),
        ('✓',''),
        (',)', ')'),
    ]
    for old, new in replacements:
        result = result.replace(old, new)
    return result.strip()

def seconds(s):
    try:
        float(s)
        return s * 1000
    except:
        print("Non-float input detected! returning 0...")
        return 0


def fetch_html(task_url):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        print("1")
        page = browser.new_page()
        print("2")
        page.goto(task_url, wait_until="domcontentloaded", timeout=seconds(30))
        print("3")
        page.fill('input[placeholder="Display name"]', 'urtrun')
        print('4')
        page.click('button:has-text("Look up")')
        print('5')
        try:
            page.wait_for_selector('img.wikisync-success', timeout=seconds(3))
        except TimeoutError:
            if page.is_visible('label:has-text("No data found. To use this, enable the WikiSync plugin in RuneLite.")'):
                return "Failed to retrieve tasks: Invalid username"
        html = page.content()
        print("4")
        browser.close()
        return html
    # response = None
    # try: 
    #     response = requests.get(task_url, headers=REQUEST_HEADERS)
    #     response.raise_for_status()
    # except RequestException as e:
    #     print(f"Link is not accessible due to: {e}")
    # finally:
    #     if response is not None:
    #         print(f"Status Code returned: {response.status_code}")
    #     else:
    #         print("No response received.")

    # return response

def parse_requirements(data):
    for scp in data.select("span.scp"):
        lvl = scp.get("data-level", "").strip()
        skill = scp.get("data-skill", "").strip()
        scp.replace_with(f"{lvl} {skill}")

    for tbz in data.select("span.tbz-region"):
        region_text = tbz.get_text("")
        tbz.replace_with(region_text)

    for span in data.select("span"):
        classlist = span.get('class')
        if classlist and len(classlist) > 3 and 'coins' in classlist:
            coin_amt = span.get_text("")
            span.replace_with(" " + coin_amt + " coin(s)")

    # if 'Leather' in data.get_text(""):
    #     print(data.prettify())
        # print(repr(data.get_text("\n", strip=True)))

    return text_cleaner(data.get_text(" ", strip=True))

# re.sub(r'(\d+)( {1,2})([a-z|\(])', r'\1 coin(s) \3', requirements)

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

fetch_html('https://oldschool.runescape.wiki/w/Raging_Echoes_League/Tasks')