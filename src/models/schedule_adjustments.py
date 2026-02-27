import dataclasses as dc
import typing
from datetime import date, time, datetime

import sqlalchemy as sa
from base_module.models import BaseOrmMappedModel, ValuedEnum
from sqlalchemy.dialects.postgresql import JSONB

SCHEMA_NAME = 'employee_system'


class EmployeeStatusCode(ValuedEnum):
    """Статус сотрудника"""

    WORK = 'Я'               # Работа (Явка)
    DAY_OFF = 'В'            # Выходной
    VACATION = 'О'           # Отпуск
    SICK_LEAVE = 'Б'         # Больничный
    BUSINESS_TRIP = 'К'      # Командировка
    STUDY_LEAVE = 'У'        # Учебный отпуск
    REMOTE_FULL = 'Д'        # Удаленно (полный день)
    OFFICE_TO_REMOTE = 'ЯД'  # Офис до обеда → удаленно
    REMOTE_TO_OFFICE = 'ДЯ'  # Удаленно до обеда → офис


@dc.dataclass
class ScheduleAdjustment(BaseOrmMappedModel):
    """Ручные правки, сделанные пользователем"""

    __tablename__ = 'schedule_adjustments'
    __table_args__ = {'schema': SCHEMA_NAME}

    id: int = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Integer, autoincrement=True, primary_key=True
        )},
    )

    employee_id: int = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Integer,
            sa.ForeignKey(
                'employee_system.users.id',
                ondelete='CASCADE',
                name='fk_schedule_adjustment_employee',
            ),
            nullable=False,
        )},
    )

    date: date = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Date, nullable=False
        )},
    )

    start_time_override: typing.Optional[time] = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Time, nullable=True
        )},
    )

    end_time_override: typing.Optional[time] = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Time, nullable=True
        )},
    )

    lunch_start_override: typing.Optional[time] = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Time, nullable=True
        )},
    )

    status_override: typing.Optional[EmployeeStatusCode] = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Enum(
                EmployeeStatusCode,
                name='employee_status_code_enum',
                create_type=False,
                validate_strings=True,
                native_enum=True,
                values_callable=lambda x: [e.value for e in x],
            ),
            nullable=True,
        )},
    )

    absences: typing.Optional[typing.List[dict]] = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            JSONB, nullable=True
        )},
    )

    created_at: datetime = dc.field(
        default_factory=datetime.utcnow,
        metadata={'sa': sa.Column(
            sa.DateTime, server_default=sa.func.now()
        )},
    )

    updated_at: typing.Optional[datetime] = dc.field(
        default_factory=datetime.utcnow,
        metadata={'sa': sa.Column(
            sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()
        )},
    )


BaseOrmMappedModel.REGISTRY.mapped(ScheduleAdjustment)
