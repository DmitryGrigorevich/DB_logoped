import openpyxl

def export_to_exel(name, rows, columns):
    wb = openpyxl.Workbook()
    ws = wb.active

    ws.append(list(columns))

    for row in rows:
        ws.append(list(row))

    wb.save(name)
    messagebox.showinfo('Success')