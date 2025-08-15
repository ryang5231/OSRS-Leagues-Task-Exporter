from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.worksheet.table import Table
import re
from openpyxl.utils import get_column_letter
import helper

IDX_TASK_DIFFICULTY = 0
IDX_VERBOSE_DESCRIPTION = 1
IDX_SKILL_REQUIREMENTS = 2
IDX_PERCENT_COMPL = 3
WRAP_COL_LETTERS = ["A", "B", "E"]
CUSTOM_COL_SETTINGS = {
                        "A": {"wrap": True, "col_width": 20},
                        "B": {"wrap": True, "col_width": 20},
                        "E": {"wrap": True, "col_width": 30}
                    }
TASKS_URL = 'https://oldschool.runescape.wiki/w/Shattered_Relics_League/Tasks'
TABLE_HEADERS = ["Task", "Description", "Difficulty", "Points", "Requirement(s)", "% Completed"]
FILE_NAME = "OSRS_Shattered_League_Tasks.xlsx"
SHEET_NAME = "Tasks"

def get_task_excel():

    response = helper.fetch_html(TASKS_URL)

    soup = BeautifulSoup(response.content, 'html.parser')

    # full div with point info and task descr
    points_reference = {
                        "Beginner": 5,
                        "Easy": 5,
                        "Medium": 25,
                        "Hard": 50,
                        "Elite": 125,
                        "Master": 250
                        }

    wb = Workbook()
    ws = wb.active
    ws.title = SHEET_NAME
    ws.append(TABLE_HEADERS)

    rows = soup.find_all("tr", attrs={"data-taskid": True})
    # point info: span title
    # text within td
    for r in rows:
        cols = r.find_all("td")
        if cols:
            task_difficulty = cols[IDX_TASK_DIFFICULTY].find("span", title=True)["title"]
            task_title = cols[IDX_TASK_DIFFICULTY].get_text(" ", strip=True)
            points = points_reference[task_difficulty]
            verbose = helper.text_cleaner(cols[IDX_VERBOSE_DESCRIPTION].get_text(" ", strip=False))
            skill_req = helper.text_cleaner(cols[IDX_SKILL_REQUIREMENTS].get_text(" ", strip=True))
            percent_compl = cols[IDX_PERCENT_COMPL].get_text(" ", strip=True)

            if not '<' in percent_compl:
                percent_compl = percent_compl.replace("%", "")
                try:
                    percent_compl = int(percent_compl)
                except ValueError:
                    try:
                        percent_compl = float(percent_compl)
                    except:
                        percent_compl = -1
                        print("Invalid Value!")

            ws.append([task_title, verbose, task_difficulty, points, skill_req, percent_compl])

    num_rows = ws.max_row       # number of rows with data (includes header)
    num_cols = ws.max_column    # number of columns with data

    start_cell = "A1"
    end_cell = f"{get_column_letter(num_cols)}{num_rows}"
    table_ref = f"{start_cell}:{end_cell}"

    table = Table(displayName=SHEET_NAME, ref=table_ref)
    ws.add_table(table)

    ws = helper.format_columns(ws, CUSTOM_COL_SETTINGS)

    wb.save(FILE_NAME)
