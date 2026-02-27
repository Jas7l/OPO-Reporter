import calendar
from datetime import date
from typing import Dict

import gspread
from loguru import logger


class GoogleSheetsService:
    def __init__(self, service_account_path: str, spreadsheet_id: str):
        try:
            self.gc = gspread.service_account(filename='service_account.json')
            self.sh = self.gc.open_by_key(spreadsheet_id)
            logger.info(f'Connected to Spreadsheet: {self.sh.title}')
        except Exception as e:
            logger.error(f'Failed to connect to Google Sheets: {e}')
            raise e

    def get_or_create_worksheet(self, report_date: date) -> gspread.Worksheet:
        month_names = {
            1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май',
            6: 'Июнь', 7: 'Июль', 8: 'Август', 9: 'Сентябрь', 10: 'Октябрь',
            11: 'Ноябрь', 12: 'Декабрь'
        }
        sheet_name = f'{month_names[report_date.month]} {report_date.year}'

        try:
            ws = self.sh.worksheet(sheet_name)
            logger.info(f'Found existing worksheet: {sheet_name}')
            return ws
        except gspread.WorksheetNotFound:
            try:
                template = self.sh.worksheet('Template')
                new_ws = template.duplicate(new_sheet_name=sheet_name)
                new_ws.update_index(0)
                logger.info(
                    f"Created new worksheet '{sheet_name}' from Template"
                )
                return new_ws
            except gspread.WorksheetNotFound:
                logger.error(
                    'Template worksheet not found! Cannot create new report.'
                )
                raise ValueError(
                    "Sheet 'Template' is missing in the document."
                )

    def sync_report_data(
            self, report_date: date, data_map: Dict[str, Dict[int, dict]]
    ):
        """
        Заполняет скопированный шаблон данными: даты, нумерация, ФИО, коды.
        Затем обрезает лишние строки и скрывает лишние дни месяца.
        """

        ws = self.get_or_create_worksheet(report_date)

        # Определяем количество дней в месяце
        _, num_days = calendar.monthrange(report_date.year, report_date.month)

        requests = []

        # Заполнение дат (Строка 6, Колонки C - AG)
        date_values = []
        for day in range(1, 32):
            if day <= num_days:
                # Генерируем дату в формате ДД.ММ.ГГГГ
                date_str = (
                    f'{day:02d}.{report_date.month:02d}'
                    f'.{report_date.year}'
                )
                date_values.append(
                    {'userEnteredValue': {'stringValue': date_str}}
                )
            else:
                date_values.append(
                    {'userEnteredValue': {'stringValue': ''}}
                )  # Пусто для 29, 30, 31 (если их нет)

        requests.append({
            'updateCells': {
                'range': {
                    'sheetId': ws.id,
                    'startRowIndex': 5,
                    'endRowIndex': 6,
                    'startColumnIndex': 2,
                    'endColumnIndex': 33,
                },
                'rows': [{'values': date_values}],
                'fields': 'userEnteredValue',
            }
        })

        # Заполнение сотрудников и кодов
        # Стартовая строка для сотрудников: 7-я (индекс 6)
        current_row_idx = 6

        for index, (fio, days_data) in enumerate(data_map.items()):
            row_cells = []

            # Колонка A: Порядковый номер
            row_cells.append({'userEnteredValue': {'numberValue': index + 1}})

            # Колонка B: ФИО
            row_cells.append({'userEnteredValue': {'stringValue': fio}})

            # Колонки C - AG: Коды и примечания по дням
            for day in range(1, 32):
                if day <= num_days:
                    cell_data = days_data.get(day, {})
                    code = cell_data.get('code', '')
                    note = cell_data.get('note', '')

                    row_cells.append({
                        'userEnteredValue': {'stringValue': code},
                        'note': note if note else '',
                    })
                else:
                    # Для дней, которых нет в месяце
                    row_cells.append(
                        {'userEnteredValue': {'stringValue': ''}, 'note': ''}
                    )

            requests.append({
                'updateCells': {
                    'range': {
                        'sheetId': ws.id,
                        'startRowIndex': current_row_idx,
                        'endRowIndex': current_row_idx + 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': 33,
                    },
                    'rows': [{'values': row_cells}],
                    'fields': 'userEnteredValue,note',
                }
            })
            current_row_idx += 1

        # Отправляем весь массив данных одним пакетом
        if requests:
            logger.info(f'Writing data for {len(data_map)} employees...')
            self.sh.batch_update({'requests': requests})

            # Скрытие и раскрытие строк
            total_employees = len(data_map)
            start_row_idx = 6  #
            start_hide_row_idx = 6 + total_employees
            end_hide_row_idx = 56

            visibility_requests = []

            # Сначала принудительно раскрываем
            if total_employees > 0:
                visibility_requests.append({
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': ws.id,
                            'dimension': 'ROWS',
                            'startIndex': start_row_idx,
                            'endIndex': start_hide_row_idx,
                        },
                        'properties': {
                            'hiddenByUser': False,
                        },
                        'fields': 'hiddenByUser',
                    }
                })

            # Скрываем пустые строки до пояснения
            if start_hide_row_idx < end_hide_row_idx:
                visibility_requests.append({
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': ws.id,
                            'dimension': 'ROWS',
                            'startIndex': start_hide_row_idx,
                            'endIndex': end_hide_row_idx,
                        },
                        'properties': {
                            'hiddenByUser': True,
                        },
                        'fields': 'hiddenByUser',
                    }
                })

            if visibility_requests:
                logger.info(
                    f'Updating row visibility (Unhide {total_employees}'
                    f' rows, Hide rest)...'
                )
                self.sh.batch_update({'requests': visibility_requests})

        # Скрываем лишние колонки
        if num_days < 31:
            logger.info(f'Hiding unused columns for a {num_days}-day month...')
            self.sh.batch_update({
                'requests': [{
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': ws.id,
                            'dimension': 'COLUMNS',
                            'startIndex': 2 + num_days,
                            'endIndex': 33,
                        },
                        'properties': {
                            'hiddenByUser': True,
                        },
                        'fields': 'hiddenByUser',
                    }
                }]
            })

        logger.success('Worksheet customized and filled successfully.')
