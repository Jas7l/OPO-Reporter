import calendar
from datetime import date, datetime, timedelta, time
from typing import List, Dict, Optional, Any

# Импорты моделей
from models.users import User, EmployeeType
from models.schedule_base import ScheduleBase, DayStatusCode
from models.schedule_adjustments import (
    ScheduleAdjustment,
    DayStatusOverride,
    LocationOverrideCode
)
from loguru import logger


class ScheduleCalculator:
    """
    Реализация вычисления итогового состояния на день.
    """

    @staticmethod
    def calculate_month_report(
            year: int,
            month: int,
            users: List[User],
            plans: List[ScheduleBase],
            adjustments: List[ScheduleAdjustment]
    ) -> Dict[str, Dict[int, Dict[str, str]]]:
        """
        Вход: Данные из БД
        Выход: Словарь для Google Sheets(data_map)
        """

        # Cписки в словари: (user_id, date) => Объект
        plans_map = {
            (p.employee_id, p.date): p for p in plans
        }
        adjustments_map = {
            (a.employee_id, a.date): a for a in adjustments
        }

        # Количество дней в месяце
        _, num_days = calendar.monthrange(year, month)

        report_data = {}

        for user in users:
            user_report = {}

            for day in range(1, num_days + 1):
                current_date = date(year, month, day)

                # Достаем план и правку для конкретного сотрудника на конкретный день
                plan = plans_map.get((user.id, current_date))
                adj = adjustments_map.get((user.id, current_date))


                # Вычисляем значение для конкретной ячейки
                cell_data = ScheduleCalculator._calculate_day(user, plan, adj, current_date)
                user_report[day] = cell_data

            report_data[user.fio] = user_report

        return report_data

    @staticmethod
    def _calculate_day(
            user: User,
            plan: Optional[ScheduleBase],
            adj: Optional[ScheduleAdjustment],
            current_date: date
    ) -> Dict[str, str]:
        """
        Расчет одной ячейки (один день одного сотрудника).
        """

        notes = []  # Список примечаний

        # ШАГ 1: Определение общего статуса (Рабочий или нет)

        # Ручная правка статуса
        if adj and adj.day_status_override:
            status_code = adj.day_status_override.value
            return {"code": status_code, "note": ""}

        # Плановый график
        if plan:
            base_code = plan.base_code.value
            # Если в плане стоит выходной/отпуск/командировка - берем его
            if base_code in [
                DayStatusCode.DAY_OFF.value,
                DayStatusCode.VACATION.value,
                DayStatusCode.SICK_LEAVE.value, # под вопросом
                DayStatusCode.BUSINESS_TRIP.value
            ]:
                return {"code": base_code, "note": ""}


        # По умолчанию - рабочий(кроме выходных)
        if current_date.weekday() >= 5:
            return {"code": "В", "note": ""}

        # ШАГ 2: Определение формата работы (не понятен 2 пункт план из excel)

        final_code = "Я"  # По умолчанию Офис


        # Ручной выбор в правке
        if adj and adj.location_override:
            final_code = adj.location_override.value
            # Сравниваем с профилем, чтобы добавить пометку(должно быть сравнение с графиком)
            if user.employee_type == EmployeeType.ALWAYS_REMOTE and "Д" not in final_code:
                notes.append("Выход в офис (вне графика)")
            elif user.employee_type == EmployeeType.OFFICE_FIXED and "Д" in final_code:
                notes.append("Удаленка (вне графика)")

        # Тип сотрудника (если нет правки)
        else:
            if user.employee_type == EmployeeType.ALWAYS_REMOTE:
                final_code = "Д"
            elif user.employee_type == EmployeeType.REMOTE_BY_SCHEDULE:
                # Тут надо смотреть план, но в модели ScheduleBase нет поля location.
                # Предполагаем, что если в плане "Я", то для гибридника это может значить "по графику".
                # Для упрощения пока ставим "Я", если не было overrides.
                final_code = "Я"
            else:
                final_code = "Я"

        # ШАГ 3: Определение времени

        # Время начала
        start_t = user.start_time
        if adj and adj.start_time_override:
            start_t = adj.start_time_override
            notes.append(f"Начало: {start_t.strftime('%H:%M')}")

        # Время конца
        end_t = user.end_time
        if adj and adj.end_time_override:
            end_t = adj.end_time_override
            notes.append(f"Конец: {end_t.strftime('%H:%M')}")

        # Обед
        lunch_s = adj.lunch_start_override if (adj and adj.lunch_start_override) else user.lunch_start
        if lunch_s:
           lunch_end_dt = datetime.combine(date.today(), lunch_s) + timedelta(minutes=user.lunch_duration or 60)
           notes.append(f"Обед: {lunch_s.strftime('%H:%M')}-{lunch_end_dt.time().strftime('%H:%M')}")

        # ШАГ 4: Наложение отлучек

        if adj and adj.absences:
            for absence in adj.absences:
                t_from = absence.get('from', '?')
                t_to = absence.get('to', '?')
                reason = absence.get('comment', '')

                note_str = f"Отлучка: {t_from}-{t_to}"
                if reason:
                    note_str += f" ({reason})"
                notes.append(note_str)

        # ШАГ 5: Формирование итога

        # Собираем все заметки в одну строку через перенос строки
        final_note = "\n".join(notes) if notes else ""

        return {
            "code": final_code,
            "note": final_note
        }


