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

PERCENTAGE_COMPL_FILL_COLOR = {
    "very_rare": {"bg_color": "#FF6262"}, # <0.1%
    "rare": {"bg_color": "FF863C"},         # 0.1 - 0.9%
    "uncommon" : {"bg_color": "FFED4C"},    # 1 - 9.9%
    "common" : {"bg_color": "56E156"},      # 10 - 49.9%
    "always" : {"bg_color": "AFEEEE"},      # >= 50%
}

REGION_ATTRIBUTE = "data-tbz-area-for-filtering"
SHEET_NAME = "Tasks"
TASKS_URL = 'https://oldschool.runescape.wiki/w/Trailblazer_Reloaded_League/Tasks'
TABLE_HEADERS = ["Area", "Task", "Description", "Requirement(s)", "Difficulty", "Points", "% Completed", "Done?"]

def get_task_excel():
    response = helper.fetch_html(TASKS_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    difficulty_reference = {
        10 : "Easy",
        40 : "Medium",
        80 : "Hard",
        200 : "Elite",
        400 : "Master",
    }

    workbook = xlsxwriter.Workbook("OSRS_4_Trailblazer_Reloaded_Tasks.xlsx")
    # output = io.BytesIO()
    # workbook = xlsxwriter.Workbook(output, {"in_memory": True})
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
    
    text_format = workbook.add_format({
        'num_format': '@',  # Text format
        'text_wrap': True,
        'valign': 'top'
    })
    
    center_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter'
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
            percent_compl = cols[IDX_PERCENT_COMPL].get_text(" ", strip=True)

            area = area.title()

            worksheet.write(row_num, 0, area, wrap_format)
            worksheet.write(row_num, 1, task_title, wrap_format)
            worksheet.write(row_num, 2, verbose, wrap_format)
            worksheet.write(row_num, 3, skill_req, wrap_format)
            worksheet.write(row_num, 4, task_difficulty, center_format)
            worksheet.write(row_num, 5, points, center_format)
            worksheet.write_string(row_num, 6, percent_compl, text_format)
            worksheet.write(row_num, 7, False)
            
            row_num += 1

    # Apply column settings
    for col_letter, settings in CUSTOM_COL_SETTINGS.items():
        col_index = ord(col_letter) - ord('A')  # Convert letter to index

        if "col_width" in settings:
            worksheet.set_column(col_index, col_index, settings["col_width"])

    # Add data validation for the "Completed?" column (column G, index 6)
    worksheet.data_validation(1, 7, row_num - 1, 7, {
        'validate': 'list',
        'source': ['TRUE', 'FALSE'],
        'input_title': 'Select completion status',
        'input_message': 'Choose TRUE or FALSE'
    })

    column_header_names = []
    for col in TABLE_HEADERS:
        column_header_names.append({'header': col})
    worksheet.add_table(0, 0, row_num - 1, len(column_header_names) - 1, {
        'name': SHEET_NAME,
        'style': 'Table Style Medium 2',
        'columns': column_header_names
    })

    # Freeze the header row
    worksheet.freeze_panes(1, 0)

    workbook.close()
    
    # output.seek(0)
    # return output.read()



if __name__ == "__main__":
    get_task_excel()