import calendar
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional

from models.schedule_adjustments import ScheduleAdjustment
from models.schedule_base import ScheduleBase
from models.users import User, EmployeeType


class ScheduleCalculator:
    """Реализация вычисления итогового состояния на день."""

    @staticmethod
    def calculate_month_report(
            year: int,
            month: int,
            users: List[User],
            plans: List[ScheduleBase],
            adjustments: List[ScheduleAdjustment],
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

                # Достаем план и правку
                # для конкретного сотрудника на конкретный день
                plan = plans_map.get((user.id, current_date))
                adj = adjustments_map.get((user.id, current_date))

                # значение для конкретной ячейки
                cell_data = ScheduleCalculator._calculate_day(
                    user, plan, adj, current_date
                )
                user_report[day] = cell_data

            report_data[user.fio] = user_report

        return report_data

    @staticmethod
    def _calculate_day(
            user: User,
            plan: Optional[ScheduleBase],
            adj: Optional[ScheduleAdjustment],
            current_date: date,
    ) -> Dict[str, str]:
        """
        Расчет одной ячейки с учетом объединенных
        статусов и динамического обеда.
        """

        notes = []
        final_code = 'Я'  # По умолчанию

        # Определение Единого Статуса
        if adj and adj.status_override:
            final_code = adj.status_override.value

            # Если статус рабочий, проверяем, не сменилась
            # ли локация вне графика
            if final_code in ['Я', 'Д', 'ЯД', 'ДЯ']:
                if (user.employee_type == EmployeeType.ALWAYS_REMOTE
                        and 'Д' not in final_code):
                    notes.append('Выход в офис (вне графика)')
                elif (user.employee_type == EmployeeType.OFFICE_FIXED
                      and 'Д' in final_code):
                    notes.append('Удаленка (вне графика)')

        elif plan and plan.status:
            final_code = plan.status.value

        elif current_date.weekday() >= 5:
            final_code = 'В'

        else:
            if user.employee_type == EmployeeType.ALWAYS_REMOTE:
                final_code = 'Д'
            else:
                final_code = 'Я'

        # Фильтрация нерабочих дней
        if final_code in ['В', 'О', 'Б', 'К', 'У']:
            return {'code': final_code, 'note': ''}

        # Определение времени (только для рабочих дней)

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
        # Выводим только если есть ручная правка времени начала обеда
        if adj and adj.lunch_start_override:
            lunch_start = adj.lunch_start_override

            duration_mins = user.lunch_duration or 60

            dummy_dt = datetime.combine(current_date, lunch_start)
            lunch_end_dt = dummy_dt + timedelta(minutes=duration_mins)
            lunch_end = lunch_end_dt.time()

            notes.append(
                f"Обед: {lunch_start.strftime('%H:%M')}-"
                f"{lunch_end.strftime('%H:%M')}"
            )

        # Наложение отлучек
        if adj and adj.absences:
            for absence in adj.absences:
                t_from = absence.get('from', '?')
                t_to = absence.get('to', '?')
                reason = absence.get('comment', '')

                note_str = f'Отлучка: {t_from}-{t_to}'
                if reason:
                    note_str += f' ({reason})'
                notes.append(note_str)

        # Формирование итога
        final_note = '\n'.join(notes) if notes else ''

        return {
            'code': final_code,
            'note': final_note
        }
