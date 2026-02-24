import datetime
from typing import List, Dict, Any, Optional

from flask import request
from sqlalchemy.orm import Session as PGSession

from base_module.models import ModuleException
from base_module.models.logger import ClassesLoggerAdapter
from models.users import User, EmployeeType, RoleType


class UsersService:
    """Сервис работы с пользователями"""

    def __init__(self, pg_connection: PGSession):
        self._pg = pg_connection
        self._logger = ClassesLoggerAdapter.create(self)

    def get_users(
            self, user_id: Optional[int] = None
    ) -> List[Dict[str, Any]] | Dict[str, Any]:
        """Получение списка пользователей или одного пользователя"""

        with self._pg.begin():
            if user_id:
                user = self._pg.query(User).get(user_id)
                if not user:
                    raise ModuleException('User not found', {'data': ''}, 404)

                self._logger.debug(
                    'Пользователь получен', extra={'id': user_id}
                )
                return user.dump()

            users = self._pg.query(User).all()

            if not users:
                raise ModuleException('No users found', {'data': ''}, 404)

            self._logger.debug('Список пользователей получен')
            return [user.dump() for user in users]

    def create_user(self) -> Dict[str, Any]:
        """Создание пользователя"""

        data = request.get_json()
        if not data:
            raise ModuleException('Request body required', {'data': ''}, 400)

        fio = data.get('fio')
        team = data.get('team')
        tg_user_id = data.get('tg_user_id')
        employee_type = data.get('employee_type')
        role = data.get('role')
        is_active = data.get('is_active', True)
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        lunch_start = data.get('lunch_start')
        lunch_duration = data.get('lunch_duration', 60)

        if not fio or not team:
            raise ModuleException(
                'Missing required fields',
                {'required': ['fio', 'team']},
                400,
            )

        try:
            employee_type_enum = (
                EmployeeType(employee_type)
                if employee_type else EmployeeType.OFFICE_FIXED
            )
        except ValueError:
            raise ModuleException('Invalid employee_type', {'data': ''}, 400)

        try:
            role_enum = (
                RoleType(role)
                if role else RoleType.USER
            )
        except ValueError:
            raise ModuleException('Invalid role', {'data': ''}, 400)

        with self._pg.begin():
            if tg_user_id:
                existing = (
                    self._pg.query(User)
                    .filter(User.tg_user_id == tg_user_id)
                    .first()
                )
                if existing:
                    raise ModuleException(
                        'User with this tg_user_id already exists',
                        {'tg_user_id': tg_user_id},
                        409,
                    )

            db_user = User(
                fio=fio,
                team=team,
                tg_user_id=tg_user_id,
                employee_type=employee_type_enum,
                role=role_enum,
                is_active=is_active,
                start_time=start_time,
                end_time=end_time,
                lunch_start=lunch_start,
                lunch_duration=lunch_duration,
                created_at=datetime.datetime.utcnow(),
                updated_at=None,
            )

            self._pg.add(db_user)
            self._pg.flush()
            self._pg.refresh(db_user)

            self._logger.debug(
                'Пользователь создан',
                extra={'id': db_user.id}
            )

            return db_user.dump()

    def update_user(self, user_id: int) -> Dict[str, Any]:
        """Обновление пользователя"""

        data = request.get_json()
        if not data:
            raise ModuleException('Request body required', {'data': ''}, 400)

        with self._pg.begin():
            user = self._pg.query(User).get(user_id)
            if not user:
                raise ModuleException('User not found', {'data': ''}, 404)

            if 'fio' in data:
                user.fio = data['fio']

            if 'team' in data:
                user.team = data['team']

            if 'tg_user_id' in data:
                tg_user_id = data['tg_user_id']

                if tg_user_id:
                    existing = (
                        self._pg.query(User)
                        .filter(
                            User.tg_user_id == tg_user_id, User.id != user_id
                        )
                        .first()
                    )
                    if existing:
                        raise ModuleException(
                            'User with this tg_user_id already exists',
                            {'tg_user_id': tg_user_id},
                            409
                        )

                user.tg_user_id = tg_user_id

            if 'employee_type' in data:
                try:
                    user.employee_type = EmployeeType(data['employee_type'])
                except ValueError:
                    raise ModuleException(
                        'Invalid employee_type', {'data': ''}, 400
                    )

            if 'role' in data:
                try:
                    user.role = RoleType(data['role'])
                except ValueError:
                    raise ModuleException('Invalid role', {'data': ''}, 400)

            if 'is_active' in data:
                user.is_active = data['is_active']

            if 'start_time' in data:
                user.start_time = data['start_time']

            if 'end_time' in data:
                user.end_time = data['end_time']

            if 'lunch_start' in data:
                user.lunch_start = data['lunch_start']

            if 'lunch_duration' in data:
                user.lunch_duration = data['lunch_duration']

            user.updated_at = datetime.datetime.utcnow()

            self._pg.add(user)
            self._pg.flush()
            self._pg.refresh(user)

            self._logger.debug(
                'Пользователь обновлён',
                extra={'id': user_id},
            )

            return user.dump()

    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Удаление пользователя"""

        with self._pg.begin():
            user = self._pg.query(User).get(user_id)
            if not user:
                raise ModuleException('User not found', {'data': ''}, 404)

            self._pg.delete(user)

            self._logger.debug(
                'Пользователь удалён',
                extra={'id': user_id},
            )

            return user.dump()
