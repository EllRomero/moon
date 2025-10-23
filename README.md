# moon

<br>

## Содержание
- [Требования](#требования)
- [Установка приложения](#установка-приложения)
- [Документация](#документация)

<br>

## Требования
- Поднята база данных (PostgreSQL) В расширение PostGIS

#### Провести миграции
##### Docker
```bash
docker exec moon /opt/app/.venv/bin/python -m alembic upgrade head
```

##### Python (Необходимо активировать виртуальное окружение)
```bash

# path workspace/src
export $(cat ../.env | xargs) && uv run python -m alembic upgrade head

# create new migration
export $(cat ../.env | xargs) && uv run python -m alembic revision --autogenerate -m "init db"
```

<br>

## Установка приложения

### Docker
#### Собрать контейнер
```bash
docker build -t moon .
```

#### Запустить контейнер с переменными из env файла
```bash
# Укажите какой порт открыть. По умолчанию приложение слушает 8000
docker run -p8000:8000 --env-file .env --name moon moon
```

Примечание: переменная окружения `SERVER_PORT` управляет портом приложения (по умолчанию 8001).

<br>

### Python
Необходимо чтобы был установлен [uv на систему](https://docs.astral.bash/uv/getting-started/installation/#winget):

#### Создание виртуального окружения
```bash
uv venv
```

#### Установка зависимостей
```bash
uv sync
```

#### Активация виртуального окружения
uv установит все зависимости в текущее виртуальное окружение.

##### Windows
```bash
.venv\Scripts\activate
```
##### Linux
```bash
source .venv/bin/activate
```

#### Запуск приложения
```bash
#path workspace/
uv run src/main.py

#path workspace/src/
export $(cat ../.env | xargs) && uv run main.py
```

#### Запуск тестов
```bash
uv run pytest -q
```
<br>

## Точки входа документации API
- Swagger/OpenAPI: `/docs/index.html`
- OpenAPI JSON: `/docs/openapi.json`

<br>
