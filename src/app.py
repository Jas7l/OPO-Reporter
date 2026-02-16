import logging
from datetime import date, time

import sqlalchemy as sa

from base_module.models.logger import setup_logging, LoggerConfig
from config import config
from injectors.connections import pg
from models.schedule_adjustments import (
    ScheduleAdjustment,
    LocationOverrideCode,
    DayStatusOverride,
)
from models.schedule_base import ScheduleBase, DayStatusCode
from models.users import User, EmployeeType, RoleType

setup_logging(LoggerConfig(root_log_level='DEBUG' if config.debug else 'INFO'))
log = logging.getLogger(__name__)


def run_test():
    log.info('Запуск теста БД')

    session = pg.acquire_session()

    log.info('Очистка таблиц перед тестом')

    session.execute(sa.text('''
        TRUNCATE TABLE
            employee_system.schedule_adjustments,
            employee_system.schedule_base,
            employee_system.users
        RESTART IDENTITY CASCADE
    '''))
    session.commit()

    log.info('--------------------------')
    log.info('Добавление в Users')

    user1 = User(
        fio='Иван Иванов Иванович',
        tg_user_id=111111,
        employee_type=EmployeeType.OFFICE_FIXED,
        role=RoleType.ADMIN,
        team='Backend',
        start_time=time(9, 0),
        end_time=time(18, 0),
        lunch_start=time(13, 0),
    )

    user2 = User(
        fio='Петр Петров Петрович',
        tg_user_id=222222,
        employee_type=EmployeeType.REMOTE_BY_SCHEDULE,
        role=RoleType.USER,
        team='Frontend',
        start_time=time(10, 0),
        end_time=time(19, 0),
        lunch_start=time(14, 0),
    )

    session.add_all([user1, user2])
    session.commit()

    log.info('--------------------------')
    log.info('Users из БД:')
    for u in session.query(User).all():
        log.info(u)

    log.info('--------------------------')
    log.info('Добавление в ScheduleBase')

    base1 = ScheduleBase(
        employee_id=user1.id,
        date=date(2025, 1, 10),
        base_code=DayStatusCode.WORK,
    )

    base2 = ScheduleBase(
        employee_id=user2.id,
        date=date(2025, 1, 10),
        base_code=DayStatusCode.DAY_OFF,
    )

    session.add_all([base1, base2])
    session.commit()

    log.info('--------------------------')
    log.info('ScheduleBase из БД:')
    for s in session.query(ScheduleBase).all():
        log.info(s)

    log.info('--------------------------')
    log.info('Добавление в ScheduleAdjustment')

    adj1 = ScheduleAdjustment(
        employee_id=user1.id,
        date=date(2025, 1, 10),
        start_time_override=time(10, 0),
        end_time_override=time(17, 0),
        location_override=LocationOverrideCode.REMOTE_FULL,
        day_status_override=None,
        absences=[{'type': 'doctor', 'hours': 2}],
    )

    adj2 = ScheduleAdjustment(
        employee_id=user2.id,
        date=date(2025, 1, 11),
        day_status_override=DayStatusOverride.SICK_LEAVE,
        absences=None,
    )

    session.add_all([adj1, adj2])
    session.commit()

    log.info('--------------------------')
    log.info('ScheduleAdjustment из БД:')
    for a in session.query(ScheduleAdjustment).all():
        log.info(a)

    log.info('Тест завершён успешно')


if __name__ == '__main__':
    log.info('Запуск инициализации БД')

    try:
        log.info('Создание таблиц...')
        pg.init_db()
        log.info('Таблицы созданы')

        run_test()

    except Exception as e:
        log.exception(f'Ошибка: {e}')
        exit(1)
