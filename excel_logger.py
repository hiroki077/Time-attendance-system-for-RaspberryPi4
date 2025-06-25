import os
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from datetime import datetime

EXCEL_PATH = "/media/ruki/KIOXIA/attendance_log.xlsx"

def save_attendance_excel(name, card_id):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    if not os.path.exists(os.path.dirname(EXCEL_PATH)):
        print("[WARN] USBメモリがマウントされていません。スキップします。")
        return

    if not name:
        name = "UNKNOWN"

    if not os.path.exists(EXCEL_PATH):
        wb = Workbook()
        ws = wb.active
        ws.append(["name", "card_id", "date", "time1"])
        ws.append([name, card_id, date_str, time_str])
        wb.save(EXCEL_PATH)
        return

    wb = load_workbook(EXCEL_PATH)
    ws = wb.active

    found = False
    for row in ws.iter_rows(min_row=2):  # skip header
        if row[0].value == name and row[1].value == card_id and row[2].value == date_str:
            next_col = len([cell for cell in row if cell.value is not None]) + 1
            col_letter = get_column_letter(next_col)
            ws[f"{col_letter}{row[0].row}"] = time_str
            found = True
            break

    if not found:
        ws.append([name, card_id, date_str, time_str])

    wb.save(EXCEL_PATH)
