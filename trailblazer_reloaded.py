from bs4 import BeautifulSoup
import xlsxwriter
import helper
import io

IDX_TASK_TITLE = 1
IDX_VERBOSE_DESCRIPTION = 2
IDX_POINTS = 3
IDX_SKILL_REQUIREMENTS = 2
IDX_PERCENT_COMPL = 5

CUSTOM_COL_SETTINGS = {
    "A": {"wrap": True, "col_width": 20},
    "B": {"wrap": True, "col_width": 20},
    "E": {"wrap": True, "col_width": 30},
    "F": {"col_width": 15},
    "G": {"col_width": 15},
}

TASKS_URL = 'https://oldschool.runescape.wiki/w/Trailblazer_Reloaded_League/Tasks'
TABLE_HEADERS = ["Area", "Task", "Description", "Difficulty", "Points", "Requirement(s)", "% Completed", "Completed?"]
SHEET_NAME = "Tasks"

def get_task_excel():
    response = helper.fetch_html(TASKS_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    points_reference = {
        "Easy": 10,
        "Medium": 40,
        "Hard": 80,
        "Elite": 250,
        "Master": 400
    }

    # Create workbook and worksheet
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
    
    text_format = workbook.add_format({
        'num_format': '@',  # Text format
        'text_wrap': True,
        'valign': 'top'
    })
    
    center_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter'
    })

    # Write headers
    for col, header in enumerate(TABLE_HEADERS):
        worksheet.write(0, col, header, header_format)
    
    worksheet.ignore_errors({'number_stored_as_text': 'G:G'})

    # Get data rows
    rows = soup.find_all("tr", attrs={"data-taskid": True})
    
    row_num = 1
    print(helper.text_cleaner(cols[IDX_VERBOSE_DESCRIPTION].get_text(" ", strip=False)))
    for r in rows:
        cols = r.find_all("td")
        if cols:
            area = r["data-tbz-area-for-filtering"]
            task_title = cols[IDX_TASK_TITLE].get_text(" ", strip=True)
            verbose = helper.text_cleaner(cols[IDX_VERBOSE_DESCRIPTION].get_text(" ", strip=False))
            points = cols[IDX_POINTS].get_text(" ", strip=True)
            percent_compl = cols[IDX_PERCENT_COMPL].get_text(" ", strip=True)

            # task_difficulty = cols[IDX_TASK_DIFFICULTY].find("span", title=True)["title"]

            
            # points = points_reference[task_difficulty]
            # skill_req = helper.text_cleaner(cols[IDX_SKILL_REQUIREMENTS].get_text(" ", strip=True))
            

            # Write data with appropriate formatting
            worksheet.write(row_num, 0, area, wrap_format)
            worksheet.write(row_num, 1, task_title, wrap_format)
            # worksheet.write(row_num, 1, verbose, wrap_format)     # Description
            # worksheet.write(row_num, 2, task_difficulty, center_format)  # Difficulty
            # worksheet.write(row_num, 3, points, center_format)    # Points
            # worksheet.write(row_num, 4, skill_req, wrap_format)   # Requirements
            # worksheet.write_string(row_num, 5, percent_compl, text_format)  # % Completed as text
            # worksheet.write(row_num, 6, False)                    # Completed checkbox
            
            row_num += 1

    # Apply column settings
    for col_letter, settings in CUSTOM_COL_SETTINGS.items():
        col_index = ord(col_letter) - ord('A')  # Convert letter to index
        
        # Set column width
        if "col_width" in settings:
            worksheet.set_column(col_index, col_index, settings["col_width"])

    # Add data validation for the "Completed?" column (column G, index 6)
    worksheet.data_validation(1, 6, row_num - 1, 6, {
        'validate': 'list',
        'source': ['TRUE', 'FALSE'],
        'input_title': 'Select completion status',
        'input_message': 'Choose TRUE or FALSE'
    })

    worksheet.add_table(0, 0, row_num - 1, 6, {
        'name': SHEET_NAME,
        'style': 'Table Style Medium 2',
        'columns': [
            {'header': 'Task'},
            {'header': 'Description'},
            {'header': 'Difficulty'},
            {'header': 'Points'},
            {'header': 'Requirement(s)'},
            {'header': '% Completed'},
            {'header': 'Completed?'}
        ]
    })

    # Freeze the header row
    worksheet.freeze_panes(1, 0)

    workbook.close()
    
    output.seek(0)
    return output.read()

if __name__ == "__main__":
    get_task_excel()