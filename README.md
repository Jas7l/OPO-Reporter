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
      - ./config.yaml:/config.yaml
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

sync_interval: 3600
debug: True

```

### .env
```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=my_db
```