from services.schedule_adjustments_service import ScheduleAdjustmentService
from services.schedule_base_service import ScheduleBaseService
from services.users_service import UsersService

from . import connections


def users_service() -> UsersService:
    """Сервис работы с пользователями"""

    return UsersService(pg_connection=connections.pg.acquire_session())


def schedule_base_service() -> ScheduleBaseService:
    """Сервис работы с плановым графиком"""

    return ScheduleBaseService(pg_connection=connections.pg.acquire_session())


def schedule_adjustments_service() -> ScheduleAdjustmentService:
    """Сервис работы с ручными правками"""

    return ScheduleAdjustmentService(
        pg_connection=connections.pg.acquire_session(),
    )
