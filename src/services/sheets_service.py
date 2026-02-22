import gspread
from gspread.utils import rowcol_to_a1
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import date


class GoogleSheetsService:
    def __init__(self, service_account_path: str, spreadsheet_id: str):
        """ Инициализация подключения к Google API """
        try:
            self.gc = gspread.service_account(filename='service_account.json')
            self.sh = self.gc.open_by_key(spreadsheet_id)
            logger.info(f"Connected to Spreadsheet: {self.sh.title}")
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise e

    def get_or_create_worksheet(self, report_date: date) -> gspread.Worksheet:
        """ Ищет лист по имени, если нет - копирует из Template """
        month_names = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 5: "Май", 6: "Июнь",
            7: "Июль", 8: "Август", 9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }
        sheet_name = f"{month_names[report_date.month]} {report_date.year}"

        try:
            # Пытаемся найти существующий лист
            ws = self.sh.worksheet(sheet_name)
            logger.info(f"Found existing worksheet: {sheet_name}")
            return ws
        except gspread.WorksheetNotFound:
            # Если нет, ищем шаблон
            try:
                template = self.sh.worksheet("Template")
                new_ws = template.duplicate(new_sheet_name=sheet_name)
                new_ws.update_index(0)
                logger.info(f"Created new worksheet '{sheet_name}' from Template")
                return new_ws
            except gspread.WorksheetNotFound:
                logger.error("Template worksheet not found! Cannot create new report.")
                raise ValueError("Sheet 'Template' is missing in the document.")

    def sync_report_data(self, report_date: date, data_map: Dict[str, Dict[int, dict]]):
        """
        Основной метод синхронизации

        data_map имеет вид:
               {
                 "Иванов И.И.": {
                    1: {"code": "Я", "note": None},
                    2: {"code": "Д", "note": "С 14:00 к врачу"},
                    ...
                 },
                 ...
               }
        """
        ws = self.get_or_create_worksheet(report_date)


        fio_column = ws.col_values(2)  # Список всех значений в колонке B

        # Создаем маппинг: Фио: Номер строки (индекс в списке + 1)
        fio_row_map = {fio.strip(): i + 1 for i, fio in enumerate(fio_column) if i > 5 and fio}



        requests = []  # Список запросов для batch_update

        for fio, days_data in data_map.items():
            row_idx = fio_row_map.get(fio)

            if not row_idx:
                logger.warning(f"Employee '{fio}' found in DB but not in Google Sheet rows. Skipping.")
                continue

            for day_num, content in days_data.items():
                # Если 1 число = Колонка C (третья), то: col = day_num + 2
                col_idx = day_num + 2

                cell_code = content.get('code', '')
                cell_note = content.get('note', '')

                # Добавляем обновление значения (Value)
                requests.append({
                    "updateCells": {
                        "range": {
                            "sheetId": ws.id,
                            "startRowIndex": row_idx - 1,  # API использует 0-based index
                            "endRowIndex": row_idx,
                            "startColumnIndex": col_idx - 1,
                            "endColumnIndex": col_idx
                        },
                        "rows": [{
                            "values": [{
                                "userEnteredValue": {"stringValue": cell_code},
                                "note": cell_note if cell_note else ""
                                # Если note пустой, он сотрет старый
                            }]
                        }],
                        "fields": "userEnteredValue,note"
                    }
                })

        # Отправляем всё одним пакетом (Batch Update)
        if requests:
            logger.info(f"Sending {len(requests)} updates to Google Sheets...")
            try:
                self.sh.batch_update({"requests": requests})
                logger.success("Google Sheets updated successfully.")
            except Exception as e:
                logger.error(f"Failed to batch update: {e}")
                raise e
        else:
            logger.info("No data changes to sync.")