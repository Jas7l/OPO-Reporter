from flask import Blueprint, jsonify
from injectors import services

schedule_base_bp = Blueprint(
    'schedule_base',
    __name__,
    url_prefix='/api/schedule-base'
)


@schedule_base_bp.route('', methods=['GET'])
def get_schedule_base():
    """Получение списка плановых записей"""

    sbs = services.schedule_base_service()
    schedules = sbs.get_schedule()

    if not schedules:
        return jsonify(status_code=404, detail='No schedule records found')

    return jsonify(schedules)


@schedule_base_bp.route('/<int:record_id>', methods=['GET'])
def get_schedule_base_record(record_id: int):
    """Получение плановой записи по ID"""

    sbs = services.schedule_base_service()
    record = sbs.get_schedule(schedule_id=record_id)

    return jsonify(record)


@schedule_base_bp.route('', methods=['POST'])
def create_schedule_base():
    """Создание плановой записи"""

    sbs = services.schedule_base_service()
    record = sbs.create_schedule()

    return jsonify(record)


@schedule_base_bp.route('/<int:record_id>', methods=['PATCH'])
def update_schedule_base(record_id: int):
    """Обновление плановой записи"""

    sbs = services.schedule_base_service()
    record = sbs.update_schedule(record_id)

    return jsonify(record)


@schedule_base_bp.route('/<int:record_id>', methods=['DELETE'])
def delete_schedule_base(record_id: int):
    """Удаление плановой записи"""

    sbs = services.schedule_base_service()
    record = sbs.delete_schedule(record_id)

    return jsonify(record)