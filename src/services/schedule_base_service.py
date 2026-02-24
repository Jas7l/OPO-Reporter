import datetime
from typing import List, Dict, Any, Optional

from flask import request
from sqlalchemy.orm import Session as PGSession

from base_module.models import ModuleException
from base_module.models.logger import ClassesLoggerAdapter
from models.schedule_base import ScheduleBase, EmployeeStatusCode
from models.users import User


class ScheduleBaseService:
    """Сервис работы с плановым графиком"""

    def __init__(self, pg_connection: PGSession):
        self._pg = pg_connection
        self._logger = ClassesLoggerAdapter.create(self)

    def get_schedule(
            self,
            schedule_id: Optional[int] = None,
            employee_id: Optional[int] = None,
    ) -> List[Dict[str, Any]] | Dict[str, Any]:
        """Получение графика"""

        with self._pg.begin():
            if schedule_id:
                schedule = self._pg.query(ScheduleBase).get(schedule_id)
                if not schedule:
                    raise ModuleException(
                        'Schedule not found', {'data': ''}, 404
                    )

                self._logger.debug(
                    'График получен', extra={'id': schedule_id}
                )
                return schedule.dump()

            query = self._pg.query(ScheduleBase)

            if employee_id:
                query = query.filter(
                    ScheduleBase.employee_id == employee_id
                )

            schedules = query.all()

            if not schedules:
                raise ModuleException(
                    'No schedules found', {'data': ''}, 404
                )

            self._logger.debug('Список графиков получен')
            return [s.dump() for s in schedules]

    def create_schedule(self) -> Dict[str, Any]:

        data = request.get_json()
        if not data:
            raise ModuleException(
                'Request body required', {'data': ''}, 400
            )

        employee_id = data.get('employee_id')
        date = data.get('date')
        status = data.get('status')

        if not employee_id or not date:
            raise ModuleException(
                'Missing required fields',
                {'required': ['employee_id', 'date']},
                400,
            )

        try:
            status_enum = (
                EmployeeStatusCode(status)
                if status else EmployeeStatusCode.WORK
            )
        except ValueError:
            raise ModuleException(
                'Invalid status', {'data': ''}, 400
            )

        with self._pg.begin():

            user = self._pg.query(User).get(employee_id)
            if not user:
                raise ModuleException(
                    'Employee not found', {'data': ''}, 404
                )

            existing = (
                self._pg.query(ScheduleBase)
                .filter(
                    ScheduleBase.employee_id == employee_id,
                    ScheduleBase.date == date,
                )
                .first()
            )

            if existing:
                raise ModuleException(
                    'Schedule already exists for this date',
                    {'employee_id': employee_id, 'date': date},
                    409,
                )

            db_schedule = ScheduleBase(
                employee_id=employee_id,
                date=date,
                status=status_enum,
                created_at=datetime.datetime.utcnow(),
                updated_at=None,
            )

            self._pg.add(db_schedule)
            self._pg.flush()
            self._pg.refresh(db_schedule)

            self._logger.debug(
                'График создан',
                extra={'id': db_schedule.id},
            )

            return db_schedule.dump()

    def update_schedule(self, schedule_id: int) -> Dict[str, Any]:


        data = request.get_json()
        if not data:
            raise ModuleException(
                'Request body required', {'data': ''}, 400
            )

        with self._pg.begin():
            schedule = self._pg.query(ScheduleBase).get(schedule_id)
            if not schedule:
                raise ModuleException(
                    'Schedule not found', {'data': ''}, 404
                )

            if 'status' in data:
                try:
                    schedule.status = EmployeeStatusCode(
                        data['status']
                    )
                except ValueError:
                    raise ModuleException(
                        'Invalid status', {'data': ''}, 400
                    )

            if 'date' in data:
                schedule.date = data['date']

            schedule.updated_at = datetime.datetime.utcnow()

            self._pg.add(schedule)
            self._pg.flush()
            self._pg.refresh(schedule)

            self._logger.debug(
                'График обновлён',
                extra={'id': schedule_id},
            )

            return schedule.dump()

    def delete_schedule(self, schedule_id: int) -> Dict[str, Any]:
        """Удаление записи из графика"""

        with self._pg.begin():
            schedule = self._pg.query(ScheduleBase).get(schedule_id)
            if not schedule:
                raise ModuleException(
                    'Schedule not found', {'data': ''}, 404
                )

            self._pg.delete(schedule)

            self._logger.debug(
                'График удалён',
                extra={'id': schedule_id},
            )

            return schedule.dump()
