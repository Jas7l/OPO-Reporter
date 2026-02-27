import dataclasses as dc
import typing
from datetime import time, datetime

import sqlalchemy as sa
from base_module.models import BaseOrmMappedModel, ValuedEnum

SCHEMA_NAME = 'employee_system'


class EmployeeType(ValuedEnum):
    """Тип занятости сотрудника"""

    ALWAYS_REMOTE = 'ALWAYS_REMOTE'
    REMOTE_BY_SCHEDULE = 'REMOTE_BY_SCHEDULE'
    OFFICE_FIXED = 'OFFICE_FIXED'
    OFFICE_FLEX = 'OFFICE_FLEX'


class RoleType(ValuedEnum):
    """Роль в боте"""

    ADMIN = 'admin'
    USER = 'user'


@dc.dataclass
class User(BaseOrmMappedModel):
    """Справочник сотрудников"""

    __tablename__ = 'users'
    __table_args__ = {'schema': SCHEMA_NAME}

    id: int = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Integer, autoincrement=True, primary_key=True
        )},
    )

    fio: str = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.String(255), nullable=False
        )},
    )

    tg_user_id: typing.Optional[int] = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.BigInteger, nullable=True, unique=True
        )},
    )

    employee_type: EmployeeType = dc.field(
        default=EmployeeType.OFFICE_FIXED,
        metadata={'sa': sa.Column(
            sa.Enum(
                EmployeeType,
                name='employee_type_enum',
                create_constraint=True,
                create_type=True,
                validate_strings=True,
                native_enum=True,
                values_callable=lambda x: [e.value for e in x],
            ),
            nullable=False,
            server_default=EmployeeType.OFFICE_FIXED.value,
        )},
    )

    role: RoleType = dc.field(
        default=RoleType.USER,
        metadata={'sa': sa.Column(
            sa.Enum(
                RoleType,
                name='role_type_enum',
                create_constraint=True,
                create_type=True,
                validate_strings=True,
                native_enum=True,
                values_callable=lambda x: [e.value for e in x],
            ),
            nullable=False,
            server_default=RoleType.USER.value,
        )},
    )

    is_active: bool = dc.field(
        default=True,
        metadata={'sa': sa.Column(
            sa.Boolean, nullable=False, default=True, server_default=sa.true()
        )},
    )

    team: str = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.String(100), nullable=False
        )},
    )

    start_time: typing.Optional[time] = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Time, nullable=True
        )},
    )

    end_time: typing.Optional[time] = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Time, nullable=True
        )},
    )

    lunch_start: typing.Optional[time] = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Time, nullable=True
        )},
    )

    lunch_duration: typing.Optional[int] = dc.field(
        default=60,
        metadata={'sa': sa.Column(
            sa.Integer, nullable=True, default=60, server_default=sa.text('60')
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


BaseOrmMappedModel.REGISTRY.mapped(User)
