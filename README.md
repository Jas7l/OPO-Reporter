# Сервис формирования отчётности

## Установка

### docker-compose.yml

```yml
services:
  db:
    image: postgres:15
    container_name: my_postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
      TZ: Europe/Moscow
      PGTZ: Europe/Moscow
    ports:
      - "5442:5432"
    volumes:
      - ./pgdata:/var/lib/postgresql/data
    networks:
      - backend-network

  opo_reporter:
    image: reporting-service:1.0.0
    command: python -m reporter
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./service_account.json:/app/src/service_account.json
    environment:
      - TZ=Europe/Moscow
      - GOOGLE_SHEETS_ID=${GOOGLE_SHEETS_ID}
      - YAML_PATH=/app/config.yaml
    networks:
      - backend-network
    restart: always


  opo_api:
    build: .
    container_name: opo_api_server
    command: python -m app
    ports:
      - "8000:8000"
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./src:/app/src
    environment:
      - TZ=Europe/Moscow
      - YAML_PATH=/app/config.yaml
    networks:
      - backend-network

  frontend:
    image: node:20-alpine
    container_name: opo_frontend
    working_dir: /app
    command: sh -c "npm install && npm run dev -- --host"
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - backend-network
    depends_on:
      - op

```

### config.yaml
```yaml
pg:
  host: db
  port: 5432
  user: postgres
  password: postgres
  database: my_db

sync_interval: 60
debug: True

```

### .env
```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=my_db

GOOGLE_SHEETS_ID=your_sheet_id
```

## Запуск

Ввести в терминал следующие команды:
`make build`
`make run`

## Подключение Google API

Для работы сервиса необходим **Service Account**.

1. **Создайте проект** в [Google Cloud Console](https://console.cloud.google.com/).
2. **Включите API**: В меню "APIs & Services" -> "Library" найдите и включите:
   - Google Sheets API
   - Google Drive API
3. **Создайте сервисный аккаунт**:
   - Перейдите в "IAM & Admin" -> "Service Accounts" -> "Create Service Account".
   - Заполните имя и нажмите "Done".
4. **Скачайте ключ**:
   - Кликните по созданному аккаунту -> вкладка "Keys" -> "Add Key" -> "Create new key" -> **JSON**.
5. **Подготовьте ключ**:
   - Переименуйте файл в `service_account.json`.
   - Положите его в корень проекта.
6. **Получите доступ к таблице**:
   - Откройте `service_account.json`, скопируйте `client_email`.
   - Откройте Google Таблицу -> Настройки доступа.
   - Вставьте email бота и выдайте права **Редактор**.
7. **Конфигурация**:
   - Скопируйте ID таблицы в файл `.env` в переменную `GOOGLE_SHEETS_ID`.

Для корректной работы необходимо скопировать лист [Template](https://docs.google.com/spreadsheets/d/1_I69DJ6oTu8q4fVZnK7bdw0Duu_TWkgK3qtUeLuGVAw/edit?usp=sharing) в свою Google Таблицу.


## API

## Пользователи

### Создание пользователя

`POST /api/users`

**Запрос** `application/json`:

```json5
{
    // ФИО сотрудника (обязательно)
    "fio": "Иванов Иван Иванович",
    // Команда (обязательно)
    "team": "Разработка",
    // ID пользователя в Telegram (опционально, должен быть уникальным)
    "tg_user_id": 123456789,
    // Тип занятости (опционально, по умолчанию "OFFICE_FIXED")
    // Возможные значения: ALWAYS_REMOTE, REMOTE_BY_SCHEDULE, OFFICE_FIXED, OFFICE_FLEX
    "employee_type": "OFFICE_FIXED",
    // Роль в боте (опционально, по умолчанию "user")
    // Возможные значения: admin, user
    "role": "user",
    // Активен ли сотрудник (опционально, по умолчанию true)
    "is_active": true,
    // Время начала работы (опционально, формат HH:MM:SS)
    "start_time": "09:00:00",
    // Время окончания работы (опционально, формат HH:MM:SS)
    "end_time": "18:00:00",
    // Время начала обеда (опционально, формат HH:MM:SS)
    "lunch_start": "13:00:00",
    // Длительность обеда в минутах (опционально, по умолчанию 60)
    "lunch_duration": 60
}
```

**Ответ** `application/json` `200 OK`

```json5
{
    "id": 1,
    "fio": "Иванов Иван Иванович",
    "team": "Разработка",
    "tg_user_id": 123456789,
    "employee_type": "OFFICE_FIXED",
    "role": "user",
    "is_active": true,
    "start_time": "09:00:00",
    "end_time": "18:00:00",
    "lunch_start": "13:00:00",
    "lunch_duration": 60,
    "created_at": "2025-07-30T08:41:26.006024",
    "updated_at": null
}
```

**Ошибки**:
`400` - отсутствует тело запроса или не указаны обязательные поля (fio, team).
`400` - недопустимое значение employee_type или role.
`409` - пользователь с указанным tg_user_id уже существует.
`500` - прочие ошибки.

### Список пользователей

`GET /api/users`

**Ответ** `application/json` `200 OK`

Возвращает массив пользователей (аналогичен объекту создания)

**Ошибки**:
`404` - пользователи не найдены.
`500` - прочие ошибки.


### Информация о пользователе

`GET /api/users/<int:user_id>`

Где:
* `user_id` - ID пользователя в базе данных

**Ответ** `application/json` `200 OK`

Аналогичен ответу при создании пользователя

**Ошибки**:
`404` - пользователи не найдены
`500` - прочие ошибки

### Обновление пользователя

`PATCH /api/users/<int:user_id>`

Где:
* `user_id` - ID пользователя в базе данных

**Запрос** `application/json`:

Все поля опциональны, обновляются только переданные поля:

```json5
{
    // ФИО сотрудника
    "fio": "Иванов Иван Петрович",
    // Команда
    "team": "Администрирование",
    // ID пользователя в Telegram (должен быть уникальным)
    "tg_user_id": 123456789,
    // Тип занятости
    "employee_type": "REMOTE_BY_SCHEDULE",
    // Роль в боте
    "role": "admin",
    // Активен ли сотрудник
    "is_active": false,
    // Время начала работы
    "start_time": "10:00:00",
    // Время окончания работы
    "end_time": "19:00:00",
    // Время начала обеда
    "lunch_start": "14:00:00",
    // Длительность обеда в минутах
    "lunch_duration": 45
}
```

**Ответ** `application/json` `200 OK`

Возвращает обновленный объект пользователя

**Ошибки**:
`400` - отсутствует тело запроса.
`400` - недопустимое значение employee_type или role.
`404` - пользователь не найден.
`409` - пользователь с указанным tg_user_id уже существует.
`500` - прочие ошибки.

### Удаление пользователя

`DELETE /api/users/<int:user_id>`

Где:
* `user_id` - ID пользователя в базе данных

**Ответ** `application/json` `200 OK`

Возвращает удаленный объект пользователя

**Ошибки**:
`404` - пользователь не найден.
`500` - прочие ошибки.

## Плановый график

### Создание записи в плановом графике

`POST /api/schedule-base`

**Запрос** `application/json`:

```json5
{
    // ID сотрудника (обязательно)
    "employee_id": 1,
    // Дата (обязательно, формат YYYY-MM-DD)
    "date": "2025-08-15",
    // Статус сотрудника (опционально, по умолчанию "Я")
    // Возможные значения: 
    //   Я - Работа (Явка)
    //   В - Выходной
    //   О - Отпуск
    //   Б - Больничный
    //   К - Командировка
    //   У - Учебный отпуск
    //   Д - Удаленно (полный день)
    //   ЯД - Офис до обеда → удаленно
    //   ДЯ - Удаленно до обеда → офис
    "status": "Я"
}
```

**Ответ** `application/json` `200 OK`

```json5
{
    // ID записи в графике
    "id": 1,
    // ID сотрудника
    "employee_id": 1,
    // Дата
    "date": "2025-08-15",
    // Статус сотрудника
    "status": "Я",
    // Дата создания
    "created_at": "2025-07-30T08:41:26.006024",
    // Дата обновления
    "updated_at": null
}
```

**Ошибки**:
`400` - отсутствует тело запроса или не указаны обязательные поля (employee_id, date).
`400` - недопустимое значение status.
`404` - сотрудник с указанным employee_id не найден.
`409` - запись для данного сотрудника и даты уже существует.
`500` - прочие ошибки.

### Список записей планового графика

`GET /api/schedule-base?employee_id=<int:employee_id>`

Где:
* `employee_id` - ID сотрудника для фильтрации (опционально)

**Ответ** `application/json` `200 OK`

Возвращает массив объектов, аналогичных ответу при создании записи

**Ошибки**:
`500` - прочие ошибки.

### Информация о записи в графике

`GET /api/schedule-base/<int:record_id>`

Где:
* `record_id` - ID записи в базе данных

**Ответ** `application/json` `200 OK`

Аналогичен ответу при создании записи

**Ошибки**:
`404` - запись не найдена.
`500` - прочие ошибки.

### Обновление записи в графике

`PATCH /api/schedule-base/<int:record_id>`

Где:
* `record_id` - ID записи в базе данных

**Запрос** `application/json`:
Все поля опциональны, обновляются только переданные поля:

```json5
{
    // Статус сотрудника
    "status": "Б",
    // Дата
    "date": "2025-08-17"
}
```

**Ответ** `application/json` `200 OK`

**Ошибки**:
`400` - отсутствует тело запроса.
`400` - недопустимое значение status.
`404` - запись не найдена.
`500` - прочие ошибки.

### Удаление записи из графика

`DELETE /api/schedule-base/<int:record_id>`

Где:
* `record_id` - ID записи в базе данных

**Ответ** `application/json` `200 OK`

Возвращает удаленный объект записи

**Ошибки**:
`404` - запись не найдена.
`500` - прочие ошибки.

## Ручные правки

### Создание ручной правки

`POST /api/schedule-adjustments`

**Запрос** `application/json`:

```json5
{
    // ID сотрудника (обязательно)
    "employee_id": 1,
    // Дата (обязательно, формат YYYY-MM-DD)
    "date": "2025-08-15",
    // Переопределение статуса (опционально)
    // Возможные значения: Я, В, О, Б, К, У, Д, ЯД, ДЯ
    "status_override": "Б",
    // Переопределение времени начала работы (опционально, формат HH:MM)
    "start_time_override": "10:00",
    // Переопределение времени окончания работы (опционально, формат HH:MM)
    "end_time_override": "19:00",
    // Переопределение времени начала обеда (опционально, формат HH:MM)
    "lunch_start_override": "14:00",
    // Отсутствия сотрудника (опционально, массив объектов)
    "absences": [
        {
            "start_time": "14:00",
            "end_time": "15:00",
            "reason": "Приём у врача"
        }
    ]
}
```

**Ответ** `application/json` `200 OK`

```json5
{
    // ID правки
    "id": 1,
    // ID сотрудника
    "employee_id": 1,
    // Дата
    "date": "2025-08-15",
    // Переопределенный статус
    "status_override": "Б",
    // Переопределенное время начала работы
    "start_time_override": "10:00",
    // Переопределенное время окончания работы
    "end_time_override": "19:00",
    // Переопределенное время начала обеда
    "lunch_start_override": "14:00",
    // Отсутствия сотрудника
    "absences": [
        {
            "start_time": "14:00",
            "end_time": "15:00",
            "reason": "Приём у врача"
        }
    ],
    // Дата создания
    "created_at": "2025-07-30T08:41:26.006024"
}
```

**Ошибки**:
`400` - отсутствует тело запроса или не указаны обязательные поля (employee_id, date).
`400` - недопустимое значение status_override.
`404` - сотрудник с указанным employee_id не найден.
`500` - прочие ошибки.

### Список ручных правок

`GET /api/schedule-adjustments?employee_id=<int:employee_id>`

Где:
* `employee_id` - ID сотрудника для фильтрации (опционально)

**Ответ** `application/json` `200 OK`

Возвращает массив объектов, аналогичных ответу при создании правки

**Ошибки**:
`500` - прочие ошибки.

### Информация о ручной правке

`GET /api/schedule-adjustments/<int:record_id>`

Где:
* `record_id` - ID правки в базе данных

**Ответ** `application/json` `200 OK`

Аналогичен ответу при создании правки

**Ошибки**:
`404` - правка не найдена.
`500` - прочие ошибки.

### Обновление ручной правки

`PATCH /api/schedule-adjustments/<int:record_id>`

Где:
* `record_id` - ID правки в базе данных

**Запрос** `application/json`:

```json5
{
    // Переопределение статуса (можно сбросить передав null)
    "status_override": "О",
    // Переопределение времени начала работы
    "start_time_override": "09:00",
    // Переопределение времени окончания работы
    "end_time_override": "18:00",
    // Переопределение времени начала обеда
    "lunch_start_override": "13:00",
    // Отсутствия сотрудника
    "absences": [
        {
            "start_time": "13:00",
            "end_time": "14:00",
            "reason": "Обед"
        }
    ]
}
```

**Ответ** `application/json` `200 OK`

Возвращает обновленный объект правки

**Ошибки**:
`400` - отсутствует тело запроса.
`400` - недопустимое значение status_override.
`404` - правка не найдена.
`500` - прочие ошибки.

### Удаление ручной правки

`DELETE /api/schedule-adjustments/<int:record_id>`

Где:
* `record_id` - ID правки в базе данных

**Ответ** `application/json` `200 OK`

Возвращает удаленный объект правки

**Ошибки**:
`404` - правка не найдена.
`500` - прочие ошибки.
