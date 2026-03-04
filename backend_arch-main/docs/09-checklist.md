# Чеклист при создании нового модуля

[← Назад к оглавлению](README.md)

---

## Модель

- [ ] Файл `{entity}_model.py` в `model/{group}/`
- [ ] Класс `{Entity}Model` наследует `Base, BaseModel`
- [ ] Docstring с бизнес-контекстом и описанием полей
- [ ] Добавлен Enum если нужен статус (в `model/enums.py`)
- [ ] Экспорт в `model/{group}/__init__.py`
- [ ] Экспорт в `model/__init__.py`
- [ ] Создана миграция Alembic

## Схема

- [ ] Файл `{entity}_schema.py` в `schema/{group}/`
- [ ] Классы:
  - [ ] `{Entity}BaseSchema` — общие поля
  - [ ] `{Entity}CreateSchema` — для POST
  - [ ] `{Entity}UpdateSchema` — для PUT/PATCH
  - [ ] `{Entity}ResponseSchema` — для ответов
  - [ ] `{Entity}FilterSchema` — для query params (если нужно)
- [ ] Docstring с описанием входных/выходных данных
- [ ] Валидаторы для полей (Field, validator)
- [ ] `from_attributes = True` в ResponseSchema
- [ ] Экспорт в `schema/{group}/__init__.py`
- [ ] Экспорт в `schema/__init__.py`

## Репозиторий

- [ ] Файл `{entity}_repository.py` в `repository/{group}/`
- [ ] Класс `{Entity}Repository` наследует `BaseRepository[{Entity}Model]`
- [ ] Docstring для каждого метода
- [ ] Только CRUD операции, без бизнес-логики
- [ ] Все методы принимают `session: AsyncSession`
- [ ] Экспорт в `repository/{group}/__init__.py`
- [ ] Экспорт в `repository/__init__.py`

## Сервис

- [ ] Файл `{entity}_service.py` в `service/{group}/`
- [ ] Класс `{Entity}Service`
- [ ] Docstring с бизнес-контекстом и зависимостями
- [ ] Инъекция репозиториев через `__init__`
- [ ] Бизнес-логика (валидация, оркестрация)
- [ ] Использование кастомных исключений (не HTTPException)
- [ ] Экспорт в `service/{group}/__init__.py`
- [ ] Экспорт в `service/__init__.py`

## API Endpoint

- [ ] Папка `api/v1/endpoints/{entity}/`
- [ ] Файлы по HTTP методам:
  - [ ] `get.py` — GET endpoints
  - [ ] `post.py` — POST endpoints
  - [ ] `put.py` — PUT/PATCH endpoints (если нужно)
  - [ ] `delete.py` — DELETE endpoints (если нужно)
- [ ] Роутер в `__init__.py`
- [ ] Docstring и `summary`/`description` для OpenAPI
- [ ] Правильные HTTP коды (201 для POST, 204 для DELETE)
- [ ] Подключение в `api/v1/endpoints/__init__.py`
- [ ] Подключение в `api/v1/include_router.py`

## Тесты

- [ ] Директория `tests/{Feature ID}_{name}/` создана
- [ ] Файл `conftest.py` с фикстурами фичи
- [ ] Для каждого сценария из PRD: `test_{Scenario ID}_{desc}.py`
- [ ] В docstring каждого теста — полный BDD (Given/When/Then)
- [ ] Тесты покрывают `then` и `and_postconditions` из PRD
- [ ] Если есть `examples` в PRD — использован `@pytest.mark.parametrize`
- [ ] Запуск: `pytest tests/{Feature ID}_{name}/ -q`

## Финальная проверка

- [ ] Все импорты работают
- [ ] Нет циклических зависимостей
- [ ] API отображается в Swagger (/docs)
- [ ] Endpoints возвращают корректные ответы
- [ ] Все тесты проходят: `pytest -q`
- [ ] Каждый сценарий из PRD покрыт тестом (нет сирот)

---

## Быстрый шаблон

### 1. Создать файлы

```
model/{group}/{entity}_model.py
schema/{group}/{entity}_schema.py
repository/{group}/{entity}_repository.py
service/{group}/{entity}_service.py
api/v1/endpoints/{entity}/__init__.py
api/v1/endpoints/{entity}/get.py
api/v1/endpoints/{entity}/post.py
```

### 2. Обновить __init__.py

```
model/__init__.py
model/{group}/__init__.py
schema/__init__.py
schema/{group}/__init__.py
repository/__init__.py
repository/{group}/__init__.py
service/__init__.py
service/{group}/__init__.py
api/v1/endpoints/__init__.py
api/v1/include_router.py
```

### 3. Создать миграцию

```bash
alembic revision --autogenerate -m "Add {entity} table"
alembic upgrade head
```

---

[Далее: Пример создания сущности →](10-example.md)
