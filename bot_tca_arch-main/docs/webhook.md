# 🔗 Пакет `webhook`

## 📋 Оглавление

1. [Архитектура](#-архитектура)
2. [Нейминги](#-нейминги)
3. [Структура модулей](#-структура-модулей)
4. [Чек-лист интеграции](#-чек-лист-интеграции-search_service)
5. [Интеграция с архитектурой](#-интеграция-с-существующей-архитектурой)
6. [Логирование](#-логирование)
7. [Запуск](#-запуск)
8. [Документация](#-документация)

---

## 🏗️ Архитектура

### Назначение
Пакет `webhook/` - отдельный **FastAPI сервер** для приема HTTP уведомлений от внешних сервисов (search_service, payment providers, etc.).

### Принцип работы

```
Внешний сервис (search_service)
    ↓ HTTP POST
FastAPI Webhook Server
    ↓ Pydantic валидация
Webhook Handler
    ↓ Вызов service/ (бизнес-логика)
    ↓ Обновление БД
    ↓ BackgroundTasks (уведомления)
Telegram Notifier → Бот → Пользователь
    ↓
HTTP 202 Accepted (подтверждение)
```

### Компоненты

| Компонент | Ответственность |
|-----------|----------------|
| **app.py** | FastAPI приложение, точка входа |
| **router.py** | Объединяет все webhook роутеры |
| **{tag}_webhook.py** | Обработчик конкретного webhook |
| **schema/{tag}_webhook_schema.py** | Pydantic схемы для валидации |
| **notifier/telegram_notifier.py** | Отправка уведомлений пользователям |

### Запуск

**Два отдельных процесса:**
- Процесс 1: Telegram бот (`python app.py`)
- Процесс 2: Webhook сервер (`python webhook/app.py`)

---

## 🎨 Нейминги

### Файлы

| Тип | Формат | Пример |
|-----|--------|--------|
| Webhook модуль | `{tag}_webhook.py` | `search_webhook.py` |
| Схемы | `{tag}_webhook_schema.py` | `search_webhook_schema.py` |
| Нотификатор | `{type}_notifier.py` | `telegram_notifier.py` |

### Классы

| Тип | Формат | Пример |
|-----|--------|--------|
| Payload схема | `{Event}WebhookPayload` | `SearchCompletionWebhookPayload` |
| Response схема | `{Event}WebhookResponse` | `SearchCompletionWebhookResponse` |
| Нотификатор | `{Type}Notifier` | `TelegramNotifier` |

### Функции и методы

| Тип | Формат | Пример |
|-----|--------|--------|
| Handler функция | `handle_{event}_webhook` | `handle_search_completion_webhook` |
| Notifier метод | `notify_{event}_completed` | `notify_search_completed` |

### Endpoints

| Формат | Пример |
|--------|--------|
| `/api/webhook/{tag}/{event}` | `/api/webhook/search/completion` |

### HTTP статусы

| Код | Использование |
|-----|---------------|
| **202** | Webhook принят (основной) |
| **400** | Ошибка валидации |
| **404** | Ресурс не найден |
| **500** | Внутренняя ошибка |

---

## 📦 Структура модулей

### Базовая структура

```
bot_refactor/
└── webhook/
    ├── __init__.py
    ├── app.py                    # FastAPI приложение
    ├── router.py                 # Главный роутер
    │
    ├── search_webhook.py         # Обработчик search_service
    ├── {tag}_webhook.py          # Другие обработчики
    │
    ├── schema/
    │   ├── __init__.py
    │   └── search_webhook_schema.py
    │
    └── notifier/
        ├── __init__.py
        ├── base_notifier.py
        └── telegram_notifier.py
```

### Шаблон webhook модуля (`search_webhook.py`)

```python
"""
Webhook обработчик: {Название}.

Endpoints:
- POST /api/webhook/{tag}/{event} - описание

Интеграция:
- Сервис: service/{domain}/{service}.py
- Уведомления: webhook/notifier/telegram_notifier.py
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks

router = APIRouter(prefix="/api/webhook/{tag}", tags=["webhook_{tag}"])

@router.post("/{event}")
async def handle_{event}_webhook(
    payload: WebhookPayload,
    background_tasks: BackgroundTasks,
):
    """Обработать webhook."""
    
    # 1. Получить данные из БД
    resource = await service.get_by_id(payload.resource_id)
    
    # 2. Обработать бизнес-логику
    await service.process(...)
    
    # 3. Отправить уведомление (в фоне)
    background_tasks.add_task(notifier.notify_completed, ...)
    
    # 4. Вернуть подтверждение
    return {"status": "accepted"}
```

### Шаблон схемы (`search_webhook_schema.py`)

```python
"""Pydantic схемы для webhook."""

from pydantic import BaseModel, Field

class SearchCompletionWebhookPayload(BaseModel):
    """Входящие данные webhook."""
    vacancy_id: int = Field(..., description="ID вакансии")
    status: str = Field(..., description="OK или ERROR")
    description: str = Field(..., description="Описание")

class SearchCompletionWebhookResponse(BaseModel):
    """Ответ на webhook."""
    status: str = Field(..., description="accepted/error")
    message: str = Field(..., description="Сообщение")
```

### Шаблон нотификатора (`telegram_notifier.py`)

```python
"""Отправка Telegram уведомлений."""

from core.loader import bot
from service.db.user_service import UserService

class TelegramNotifier:
    """Отправка уведомлений через Telegram."""
    
    def __init__(self):
        self.bot = bot
        self.user_service = UserService()
    
    async def notify_search_completed(
        self,
        user_id: int,
        vacancy_id: int,
        status: str,
        candidates_count: int,
    ):
        """Уведомить о завершении поиска."""
        
        # 1. Получить Telegram ID
        user = await self.user_service.get_by_id(user_id)
        
        # 2. Сформировать сообщение
        text = f"✅ Поиск завершен! Найдено {candidates_count} кандидатов"
        
        # 3. Отправить
        await self.bot.send_message(
            chat_id=user.telegram_id,
            text=text,
        )
```

### FastAPI приложение (`app.py`)

```python
"""FastAPI приложение для webhook."""

from fastapi import FastAPI
from webhook.router import webhook_router

app = FastAPI(title="HR Bot Webhook API")
app.include_router(webhook_router)

@app.get("/")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("webhook.app:app", host="0.0.0.0", port=8080)
```

### Главный роутер (`router.py`)

```python
"""Главный роутер для всех webhook."""

from fastapi import APIRouter
from webhook.search_webhook import router as search_router

webhook_router = APIRouter()
webhook_router.include_router(search_router)
```

---

## ✅ Чек-лист интеграции search_service

### Минимальная реализация

1. **Создать структуру**
   - [ ] `webhook/` директория
   - [ ] `webhook/schema/` директория
   - [ ] `webhook/notifier/` директория

2. **Создать файлы**
   - [ ] `webhook/app.py` - FastAPI приложение
   - [ ] `webhook/router.py` - главный роутер
   - [ ] `webhook/search_webhook.py` - обработчик
   - [ ] `webhook/schema/search_webhook_schema.py` - схемы
   - [ ] `webhook/notifier/telegram_notifier.py` - уведомления

3. **Реализовать логику**
   - [ ] Endpoint: `/api/webhook/search/completion`
   - [ ] Валидация: `SearchCompletionWebhookPayload`
   - [ ] Обработка: получить вакансию → обновить статус
   - [ ] Уведомление: `notify_search_completed()`
   - [ ] Ответ: `HTTP 202 Accepted`

4. **Протестировать**
   - [ ] Запустить webhook сервер
   - [ ] Отправить тестовый POST запрос
   - [ ] Проверить Swagger UI: `http://localhost:8080/docs`
   - [ ] Проверить уведомление в Telegram
   - [ ] Проверить обновление БД

---

## 🔗 Интеграция с существующей архитектурой

### Используемые компоненты

| Откуда | Что используем |
|--------|----------------|
| `service/db/` | `VacancyService`, `CandidateService`, `UserService` |
| `core/loader.py` | `bot` instance |
| `callback/` | Классы колбеков для кнопок |

### Зависимости

```
webhook/
    ↓
service/db/  (бизнес-логика)
    ↓
repository/  (работа с БД)
    ↓
database     (БД)
```

---

## 📊 Логирование

### Обязательные точки

```python
# Получение webhook
logger.info(f"📬 Получен webhook", extra={"payload": payload.model_dump()})

# Успешные операции
logger.info(f"✅ Вакансия найдена: {vacancy.id}")
logger.info(f"✅ Статус обновлен")
logger.info(f"📤 Уведомление отправлено")

# Ошибки
logger.error(f"❌ Вакансия не найдена: {vacancy_id}")
logger.exception(f"❌ Непредвиденная ошибка: {e}")
```

---

## 🚀 Запуск

### Локально

```bash
# Терминал 1: Бот
cd bot_refactor
python app.py

# Терминал 2: Webhook сервер
cd bot_refactor
python webhook/app.py
```

**Доступ:**
- API: `http://localhost:8080`
- Swagger UI: `http://localhost:8080/docs`

### Docker Compose

```yaml
services:
  bot:
    command: python app.py
  
  webhook:
    command: uvicorn webhook.app:app --host 0.0.0.0 --port 8080
    ports:
      - "8080:8080"
```

---

## 📝 Документация

### Обязательные docstring

**Модуль webhook:**
```python
"""
Webhook обработчик: {Название}.

Endpoints:
- POST /api/webhook/{tag}/{event} - описание

Интеграция:
- Сервис: service/...
- Уведомления: webhook/notifier/...
"""
```

**Endpoint функция:**
```python
async def handle_webhook(...):
    """
    Обработать webhook.
    
    Args: ...
    Returns: ...
    Raises: ...
    """
```

**Pydantic схема:**
```python
class WebhookPayload(BaseModel):
    """
    Описание схемы.
    
    Attributes:
        field: Описание поля
    """
    field: Type = Field(..., description="...")
```

---

## 🎯 Ключевые принципы

1. **Отдельный процесс** - FastAPI сервер независим от бота
2. **HTTP 202** - webhook принят, обработка в фоне
3. **BackgroundTasks** - уведомления не блокируют ответ
4. **Pydantic** - автоматическая валидация входящих данных
5. **Переиспользование** - используем существующие `service/`
6. **Система тегов** - такая же как в остальном боте
7. **Логирование** - всех этапов обработки

