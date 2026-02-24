from flask import Blueprint, jsonify
from injectors import services

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('', methods=['GET'])
def get_users():
    """Получение списка пользователей"""

    us = services.users_service()
    users = us.get_users()
    return jsonify(users)


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    """Получение пользователя по ID"""

    us = services.users_service()
    user = us.get_users(user_id=user_id)
    return jsonify(user)


@users_bp.route('', methods=['POST'])
def create_user():
    """Создание пользователя"""

    us = services.users_service()
    user = us.create_user()
    return jsonify(user)


@users_bp.route('/<int:user_id>', methods=['PATCH'])
def update_user(user_id: int):
    """Обновление пользователя"""

    us = services.users_service()
    user = us.update_user(user_id)
    return jsonify(user)


@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id: int):
    """Удаление пользователя"""

    us = services.users_service()
    user = us.delete_user(user_id)
    return jsonify(user)
