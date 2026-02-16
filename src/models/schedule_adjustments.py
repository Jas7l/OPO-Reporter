import dataclasses as dc
import typing
from datetime import date, time, datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from base_module.models import BaseOrmMappedModel, ValuedEnum

SCHEMA_NAME = 'employee_system'


class LocationOverrideCode(ValuedEnum):
    """Коды форматов работы"""

    OFFICE_FULL = 'Я'      # Офис (полный день)
    REMOTE_FULL = 'Д'      # Удаленно (полный день)
    OFFICE_TO_REMOTE = 'ЯД'  # Офис до обеда, далее удаленно
    REMOTE_TO_OFFICE = 'ДЯ'  # Удаленно до обеда, далее офис


class DayStatusOverride(ValuedEnum):
    """Статус дня для ручной правки"""

    SICK_LEAVE = 'Б'   # Больничный
    VACATION = 'О'     # Отпуск
    BUSINESS_TRIP = 'К'  # Командировка


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

    location_override: typing.Optional[LocationOverrideCode] = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Enum(
                LocationOverrideCode,
                name='location_override_code_enum',
                create_constraint=True,
                create_type=True,
                validate_strings=True,
                native_enum=True,
                values_callable=lambda x: [e.value for e in x],
            ),
            nullable=True,
        )},
    )

    day_status_override: typing.Optional[DayStatusOverride] = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Enum(
                DayStatusOverride,
                name='day_status_override_enum',
                create_constraint=True,
                create_type=True,
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
