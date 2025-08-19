from bs4 import BeautifulSoup
import xlsxwriter
import helper
import io

IDX_TASK_TITLE = 1
IDX_VERBOSE_DESCRIPTION = 2
IDX_SKILL_REQUIREMENTS = 3
IDX_POINTS = 4
IDX_PERCENT_COMPL = 5

CUSTOM_COL_SETTINGS = {
    "A": {"col_width": 10},
    "B": {"wrap": True, "col_width": 20},
    "C": {"wrap": True, "col_width": 30},
    "D": {"wrap": True, "col_width": 30},
}

REGION_ATTRIBUTE = "data-tbz-area-for-filtering"
SHEET_NAME = "Tasks"
TASKS_URL = 'https://oldschool.runescape.wiki/w/Trailblazer_Reloaded_League/Tasks'
TABLE_HEADERS = ["Area", "Task", "Description", "Requirement(s)", "Difficulty", "Points", "% Completed", "Done?"]

COL_NUM_PERCENT_COMPL = len(TABLE_HEADERS) - 2
COL_NUM_COMPLETION_TICK = len(TABLE_HEADERS) - 1
ROW_NUM_FIRST_DATA = 1

def get_task_excel(test_mode_enabled=False):
    response = helper.fetch_html(TASKS_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    difficulty_reference = {
        10 : "Easy",
        40 : "Medium",
        80 : "Hard",
        200 : "Elite",
        400 : "Master",
    }

    if test_mode_enabled:
        workbook = xlsxwriter.Workbook("OSRS_4_Trailblazer_Reloaded_Tasks.xlsx")
    else:
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet(SHEET_NAME)

    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D7E4BC',
        'border': 1
    })
    
    wrap_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'top'
    })
    
    
    center_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
    })

    for col, header in enumerate(TABLE_HEADERS):
        worksheet.write(0, col, header, header_format)
    
    worksheet.ignore_errors({'number_stored_as_text': 'G:G'})

    # Get data rows
    rows = soup.find_all("tr", attrs={"data-taskid": True})
    
    row_num = 1
    # print(type(rows[1221].find_all("td")[4]))
    for r in rows:
        cols = r.find_all("td")
        if cols:
            area = r[REGION_ATTRIBUTE]
            task_title = cols[IDX_TASK_TITLE].get_text(" ", strip=True)
            verbose = helper.text_cleaner(cols[IDX_VERBOSE_DESCRIPTION].get_text(" ", strip=True))
            skill_req = helper.text_cleaner(cols[IDX_SKILL_REQUIREMENTS].get_text(" ", strip=True))
            points = int(cols[IDX_POINTS].get_text(" ", strip=True))
            task_difficulty = difficulty_reference[points]
            percent_str = cols[IDX_PERCENT_COMPL].get_text(" ", strip=True)

            area = area.title()
            percent_val = helper.parse_percent(percent_str)

            row_data = [area, task_title, verbose, skill_req, points, task_difficulty, percent_val]
            percent_format = workbook.add_format(helper.construct_percent_fill_format(percent_str))
            row_format = {
                area: wrap_format, 
                task_title: wrap_format, 
                verbose: wrap_format, 
                skill_req: wrap_format, 
                points: center_format, 
                task_difficulty: center_format, 
                percent_val: percent_format,
            }

            for i, rd in enumerate(row_data):
                if i == COL_NUM_PERCENT_COMPL:
                    worksheet.write_number(row_num, i, row_data[i], row_format[rd])
                else:
                    worksheet.write(row_num, i, row_data[i], row_format[rd])

            worksheet.insert_checkbox(row_num, COL_NUM_COMPLETION_TICK, False, center_format)
            
            row_num += 1

    last_data_row_num = row_num - 1

    # Apply column settings
    for col_letter, settings in CUSTOM_COL_SETTINGS.items():
        col_index = ord(col_letter) - ord('A')  # Convert letter to index

        if "col_width" in settings:
            worksheet.set_column(col_index, col_index, settings["col_width"])

    # Add data validation for the "Completed?" column (column G, index 6)
    worksheet.data_validation(ROW_NUM_FIRST_DATA, COL_NUM_COMPLETION_TICK,
                               last_data_row_num, COL_NUM_COMPLETION_TICK, {
        'validate': 'list',
        'source': ['TRUE', 'FALSE'],
    })

    column_header_names = []
    for col in TABLE_HEADERS:
        column_header_names.append({'header': col})
    worksheet.add_table(0, 0, last_data_row_num, COL_NUM_COMPLETION_TICK, {
        'name': SHEET_NAME,
        'style': 'Table Style Medium 2',
        'columns': column_header_names
    })

    # Freeze the header row
    worksheet.freeze_panes(1, 0)

    workbook.close()
    
    if not test_mode_enabled:
        output.seek(0)
        return output.read()

if __name__ == "__main__":
    get_task_excel(test_mode_enabled=True)