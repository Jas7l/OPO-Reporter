import time
import os
import calendar
from datetime import date, datetime
from typing import List, Tuple

import sqlalchemy as sa
from sqlalchemy import select, and_
from loguru import logger

# Импорты конфигурации и БД
from config import config
from injectors.connections import pg
from base_module.models.logger import setup_logging, LoggerConfig

# Импорты моделей
from models.users import User
from models.schedule_base import ScheduleBase
from models.schedule_adjustments import ScheduleAdjustment

# Импорты логики
from domain.calculator import ScheduleCalculator
from services.sheets_service import GoogleSheetsService

# Настройка логгера
setup_logging(LoggerConfig(root_log_level='DEBUG' if config.debug else 'INFO'))


def fetch_month_data(year: int, month: int) -> Tuple[List[User], List[ScheduleBase], List[ScheduleAdjustment]]:
    """
    Забирает из БД все необходимые данные за конкретный месяц.
    """
    # Вычисляем первый и последний день месяца
    _, last_day_num = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day_num)

    logger.debug(f"Fetching data for range: {start_date} - {end_date}")

    # Получаем сессию
    session = pg.acquire_session()

    try:
        # Активные сотрудники
        # Используем session.scalars для получения списка объектов, а не кортежей
        users = session.scalars(
            select(User)
            .where(User.is_active == True)
            .order_by(User.fio)
        ).all()

        # Плановый график (только за этот месяц)
        plans = session.scalars(
            select(ScheduleBase)
            .where(
                and_(
                    ScheduleBase.date >= start_date,
                    ScheduleBase.date <= end_date
                )
            )
        ).all()

        # Ручные правки (только за этот месяц)
        adjustments = session.scalars(
            select(ScheduleAdjustment)
            .where(
                and_(
                    ScheduleAdjustment.date >= start_date,
                    ScheduleAdjustment.date <= end_date
                )
            )
        ).all()

        logger.info(f"Fetched: {len(users)} users, {len(plans)} plans, {len(adjustments)} adjustments.")
        return users, plans, adjustments

    except Exception as e:
        logger.error(f"Database fetch error: {e}")
        raise e
    finally:
        # Важно: закрываем сессию, если она не управляется декоратором
        session.close()


def main():
    logger.info("--- Starting OPO Reporter Service ---")

    # Инициализация БД
    try:
        pg.init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to connect/init DB: {e}")
        return

    # Инициализация Google Service
    # ID таблицы берем из переменных окружения Docker или .env
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    if not spreadsheet_id:
        logger.critical("GOOGLE_SHEETS_ID is not set! Check your .env file.")
        return

    try:
        # Путь к ключу внутри контейнера
        key_path = "service_account.json"
        sheets_service = GoogleSheetsService(key_path, spreadsheet_id)
    except Exception as e:
        logger.critical(f"Failed to initialize Google Service: {e}")
        return

    # Основной цикл работы
    logger.info(f"Service started. Sync interval: {config.sync_interval} seconds.")

    while True:
        try:
            # Определяем, за какой месяц строим отчет(текущий)
            today = date.today()
            target_year, target_month = today.year, today.month

            logger.info(f"Starting sync cycle for {target_month}/{target_year}...")

            # Получение данных
            users, plans, adjustments = fetch_month_data(target_year, target_month)

            if not users:
                logger.warning("No active users found. Skipping sync.")
            else:
                # Calculator вернет data_map
                report_data = ScheduleCalculator.calculate_month_report(
                    target_year, target_month, users, plans, adjustments
                )

                # Отправка в Google
                report_date_marker = date(target_year, target_month, 1)
                sheets_service.sync_report_data(report_date_marker, report_data)

            logger.success("Sync cycle completed.")

        except Exception as e:
            logger.exception(f"Unexpected error in sync cycle: {e}")

        # Шаг Г: Ожидание
        logger.info(f"Sleeping for {config.sync_interval}s...")
        time.sleep(config.sync_interval)


if __name__ == "__main__":
    main()