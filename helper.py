import requests
from openpyxl.styles import Alignment, numbers, NamedStyle
from requests import RequestException
import re

REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/",
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
        (' ]', ']')
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


def format_columns(worksheet, custom_cols):
    columns = worksheet.columns
    for col in columns:
        col_letter = col[0].column_letter
        if col_letter in custom_cols:
            if "wrap" in custom_cols[col_letter]:
                for cell in col:
                    try:
                        if cell.value:
                            cell.alignment = Alignment(
                                        wrap_text=True,
                                        horizontal="left",
                                        vertical="top"
                                    )
                    except:
                        pass
            if "col_width" in custom_cols[col_letter]:
                worksheet.column_dimensions[col_letter].width = custom_cols[col_letter]["col_width"]
            # if "format" in custom_cols[col_letter]:
            #     for cell in col:
            #         try:
            #             if cell.value:
            #                 cell.style = NamedStyle(name="text_style")
            #                 cell.number_format = '@'
            #         except:
            #             print("no")
            #             pass
        else:
            for cell in col:
                try:
                    if cell.value:
                        cell.alignment = Alignment(
                                    wrap_text=True,
                                    horizontal="left",
                                    vertical="center"
                                )
                except:
                    pass
    return worksheet

