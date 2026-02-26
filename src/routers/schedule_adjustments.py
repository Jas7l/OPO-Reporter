from flask import Blueprint, jsonify
from injectors import services

schedule_adjustments_bp = Blueprint(
    'schedule_adjustments',
    __name__,
    url_prefix='/api/schedule-adjustments'
)


@schedule_adjustments_bp.route('', methods=['GET'])
def get_schedule_adjustments():
    """Получение списка ручных правок"""

    sas = services.schedule_adjustments_service()
    adjustments = sas.get_adjustments()

    if not adjustments:
        return jsonify(status_code=404, detail='No schedule adjustments found')

    return jsonify(adjustments)


@schedule_adjustments_bp.route('/<int:record_id>', methods=['GET'])
def get_schedule_adjustment(record_id: int):
    """Получение ручной правки по ID"""

    sas = services.schedule_adjustments_service()
    record = sas.get_adjustments(adjustment_id=record_id)

    return jsonify(record)


@schedule_adjustments_bp.route('', methods=['POST'])
def create_schedule_adjustment():
    """Создание ручной правки"""

    sas = services.schedule_adjustments_service()
    record = sas.create_adjustment()

    return jsonify(record)


@schedule_adjustments_bp.route('/<int:record_id>', methods=['PATCH'])
def update_schedule_adjustment(record_id: int):
    """Обновление ручной правки"""

    sas = services.schedule_adjustments_service()
    record = sas.update_adjustment(record_id)

    return jsonify(record)


@schedule_adjustments_bp.route('/<int:record_id>', methods=['DELETE'])
def delete_schedule_adjustment(record_id: int):
    """Удаление ручной правки"""

    sas = services.schedule_adjustments_service()
    record = sas.delete_adjustment(record_id)

    return jsonify(record)