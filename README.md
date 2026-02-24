### docker-compose.yml

```yaml
services:
  db:
    image: postgres:15
    container_name: my_postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5442:5432"
    volumes:
      - ./pgdata:/var/lib/postgresql/data
    networks:
      - backend-network

  opo_reporter:
    image: reporting-service:1.0.0
    command: python -m app
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./service_account.json:/app/src/service_account.json
    environment:
      - GOOGLE_SHEETS_ID=${GOOGLE_SHEETS_ID}
      - YAML_PATH=/app/config.yaml
    networks:
      - backend-network
    restart: always

networks:
  backend-network:
    driver: bridge

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

GOOGLE_SHEETS_ID=11vqxoSohZHkS9i47VI3sdkkSGBNpR7LDl3ZYt0_THA4
```


# API

## Пользователи

### Создание пользователя

`POST /api/users`

**Запрос** `application/json`:

```json
{
    // ФИО сотрудника (обязательно)
    "fio": "Иванов Иван Иванович",

    // Команда (обязательно)
    "team": "Backend",

    // Telegram ID (опционально, уникальный)
    "tg_user_id": 123456789,

    // Тип занятости (опционально)
    // ALWAYS_REMOTE
    // REMOTE_BY_SCHEDULE
    // OFFICE_FIXED
    // OFFICE_FLEX
    "employee_type": "OFFICE_FIXED",

    // Роль (опционально)
    // admin
    // user
    "role": "user",

    // Активен ли сотрудник (опционально)
    "is_active": true,

    // Рабочее время (опционально)
    "start_time": "09:00:00",
    "end_time": "18:00:00",
    "lunch_start": "13:00:00",

    // Длительность обеда в минутах (опционально)
    "lunch_duration": 60
}
```

**Ответ** `application/json` `200 OK`

```json
{
    "id": 1,
    "fio": "Иванов Иван Иванович",
    "team": "Backend",
    "tg_user_id": 123456789,
    "employee_type": "OFFICE_FIXED",
    "role": "user",
    "is_active": true,
    "start_time": "09:00:00",
    "end_time": "18:00:00",
    "lunch_start": "13:00:00",
    "lunch_duration": 60,
    "created_at": "2026-02-23T10:00:00",
    "updated_at": null
}
```

**Ошибки**:
`400` — отсутствуют обязательные поля / неверный enum
`404` — сотрудник не найден (для связанных операций)
`409` — tg_user_id уже существует
`500` — внутренняя ошибка сервера

### Получение списка пользователей

`GET /api/users`

**Ответ** `application/json` `200 OK`

Возвращает массив пользователей (аналогичен объекту создания)

**Ошибки**:
`404` — пользователи не найдены
`500` — прочие ошибки
