import os
from datetime import date
from services import GoogleSheetsService

# 1. НАСТРОЙКИ (Заполни своими данными)
SERVICE_ACCOUNT_FILE = 'service_account.json' # Файл должен лежать рядом
SPREADSHEET_ID = '11vqxoSohZHkS9i47VI3sdkkSGBNpR7LDl3ZYt0_THA4'
# ID - это длинная строка из URL: d/1BxiMVs0XRA5nFMdKvBdBZjgmUW8/edit

def main():
    print("--- Запуск теста Google Integration ---")

    # 2. Инициализация сервиса
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Ошибка: Файл {SERVICE_ACCOUNT_FILE} не найден!")
        return

    try:
        gs = GoogleSheetsService(SERVICE_ACCOUNT_FILE, SPREADSHEET_ID)
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return

    # 3. Подготовка тестовых данных
    # Эмулируем, что мы хотим записать данные за Февраль 2026
    report_date = date(2026, 2, 1)

    # Эмулируем данные "калькулятора"
    # Важно: Имя "Тестовый Сотрудник" ДОЛЖНО быть в колонке B листа Template!
    fake_data = {
        "Тестовый Сотрудник": {
            1: {"code": "Я", "note": ""},               # 1 февраля: Офис
            2: {"code": "Б", "note": "Работа из дома"}, # 2 февраля: Удаленка + примечание
            3: {"code": "ЯД", "note": "Больничный"},     # 3 февраля: Больничный
            5: {"code": "Д", "note": "До обеда в офисе"}                # 5 февраля: До обеда в офисе
        }
    }

    print(f"Начинаем синхронизацию за {report_date.strftime('%B %Y')}...")

    # 4. Запуск синхронизации
    try:
        gs.sync_report_data(report_date, fake_data)
        print("✅ Успешно! Проверь Google Таблицу.")
    except Exception as e:
        print(f"❌ Произошла ошибка при записи: {e}")

if __name__ == "__main__":
    main()