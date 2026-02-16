import dataclasses as dc
import typing
from datetime import date, datetime

import sqlalchemy as sa
from base_module.models import BaseOrmMappedModel, ValuedEnum

SCHEMA_NAME = 'employee_system'


class DayStatusCode(ValuedEnum):
    """Коды статусов дня """

    WORK = 'Я'      # Работа (Явка)
    DAY_OFF = 'В'   # Выходной
    VACATION = 'О'  # Отпуск
    SICK_LEAVE = 'Б'  # Больничный
    BUSINESS_TRIP = 'К'  # Командировка
    STUDY_LEAVE = 'У'  # Учебный отпуск


@dc.dataclass
class ScheduleBase(BaseOrmMappedModel):
    """Плановый график"""

    __tablename__ = 'schedule_base'
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
                name='fk_schedule_base_employee',
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

    base_code: DayStatusCode = dc.field(
        default=DayStatusCode.WORK,
        metadata={'sa': sa.Column(
            sa.Enum(
                DayStatusCode,
                name='day_status_code_enum',
                create_constraint=True,
                create_type=True,
                validate_strings=True,
                native_enum=True,
                values_callable=lambda x: [e.value for e in x],
            ),
            nullable=False,
            server_default=DayStatusCode.WORK.value,
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


BaseOrmMappedModel.REGISTRY.mapped(ScheduleBase)
