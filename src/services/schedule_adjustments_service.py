import datetime
from typing import List, Dict, Any, Optional

from flask import request
from sqlalchemy.orm import Session as PGSession

from base_module.models import ModuleException
from base_module.models.logger import ClassesLoggerAdapter
from models.schedule_adjustments import (
    ScheduleAdjustment,
    EmployeeStatusCode,
)
from models.users import User


class ScheduleAdjustmentService:
    """Сервис ручных правок графика"""

    def __init__(self, pg_connection: PGSession):
        self._pg = pg_connection
        self._logger = ClassesLoggerAdapter.create(self)

    def get_adjustments(
            self,
            adjustment_id: Optional[int] = None,
            employee_id: Optional[int] = None,
    ) -> List[Dict[str, Any]] | Dict[str, Any]:
        """Получение списка правок или одной правки"""

        with self._pg.begin():
            if adjustment_id:
                adjustment = (
                    self._pg.query(ScheduleAdjustment)
                    .get(adjustment_id)
                )
                if not adjustment:
                    raise ModuleException(
                        'Adjustment not found', {'data': ''}, 404
                    )

                return adjustment.dump()

            query = self._pg.query(ScheduleAdjustment)

            if employee_id:
                query = query.filter(
                    ScheduleAdjustment.employee_id == employee_id
                )

            adjustments = query.all()

            if not adjustments:
                raise ModuleException(
                    'No adjustments found', {'data': ''}, 404
                )

            return [a.dump() for a in adjustments]

    def create_adjustment(self) -> Dict[str, Any]:
        """Создание правки"""

        data = request.get_json()
        if not data:
            raise ModuleException(
                'Request body required', {'data': ''}, 400
            )

        employee_id = data.get('employee_id')
        date = data.get('date')
        status_override = data.get('status_override')

        if not employee_id or not date:
            raise ModuleException(
                'Missing required fields',
                {'required': ['employee_id', 'date']},
                400,
            )

        try:
            status_enum = (
                EmployeeStatusCode(status_override)
                if status_override else None
            )
        except ValueError:
            raise ModuleException(
                'Invalid status_override', {'data': ''}, 400
            )

        with self._pg.begin():

            user = self._pg.query(User).get(employee_id)
            if not user:
                raise ModuleException(
                    'Employee not found', {'data': ''}, 404
                )

            db_adjustment = ScheduleAdjustment(
                employee_id=employee_id,
                date=date,
                start_time_override=data.get('start_time_override'),
                end_time_override=data.get('end_time_override'),
                lunch_start_override=data.get('lunch_start_override'),
                status_override=status_enum,
                absences=data.get('absences'),
                created_at=datetime.datetime.utcnow(),
                updated_at=None,
            )

            self._pg.add(db_adjustment)
            self._pg.flush()
            self._pg.refresh(db_adjustment)

            self._logger.debug(
                'Правка создана',
                extra={'id': db_adjustment.id},
            )

            return db_adjustment.dump()

    def update_adjustment(self, adjustment_id: int) -> Dict[str, Any]:
        """Обновление правки"""

        data = request.get_json()
        if not data:
            raise ModuleException(
                'Request body required', {'data': ''}, 400
            )

        with self._pg.begin():
            adjustment = (
                self._pg.query(ScheduleAdjustment)
                .get(adjustment_id)
            )
            if not adjustment:
                raise ModuleException(
                    'Adjustment not found', {'data': ''}, 404
                )

            if 'status_override' in data:
                try:
                    adjustment.status_override = (
                        EmployeeStatusCode(
                            data['status_override']
                        )
                        if data['status_override'] else None
                    )
                except ValueError:
                    raise ModuleException(
                        'Invalid status_override',
                        {'data': ''},
                        400,
                    )

            if 'start_time_override' in data:
                adjustment.start_time_override = data[
                    'start_time_override'
                ]

            if 'end_time_override' in data:
                adjustment.end_time_override = data[
                    'end_time_override'
                ]

            if 'lunch_start_override' in data:
                adjustment.lunch_start_override = data[
                    'lunch_start_override'
                ]

            if 'absences' in data:
                adjustment.absences = data['absences']

            adjustment.updated_at = datetime.datetime.utcnow()

            self._pg.add(adjustment)
            self._pg.flush()
            self._pg.refresh(adjustment)

            self._logger.debug(
                'Правка обновлена',
                extra={'id': adjustment_id},
            )

            return adjustment.dump()

    def delete_adjustment(self, adjustment_id: int) -> Dict[str, Any]:
        """Удаление правки"""

        with self._pg.begin():
            adjustment = (
                self._pg.query(ScheduleAdjustment)
                .get(adjustment_id)
            )
            if not adjustment:
                raise ModuleException(
                    'Adjustment not found', {'data': ''}, 404
                )

            self._pg.delete(adjustment)

            self._logger.debug(
                'Правка удалена',
                extra={'id': adjustment_id},
            )

            return adjustment.dump()
