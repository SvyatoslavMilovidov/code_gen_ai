# 🎯 Пакет `handler`

## 📋 Оглавление
1. [Описание пакета](#описание-пакета)
2. [Внутренняя архитектура](#внутренняя-архитектура)
3. [Виджет-оркестратор](#виджет-оркестратор)
4. [Чек-лист добавления элементов](#чек-лист-добавления-виджета)

---

## Описание пакета

### 🎯 Назначение
Пакет `handler` содержит **виджеты-оркестраторы**, которые собирают UI-компоненты из `node/` и регистрируют обработчики событий Telegram.

### 💡 Ключевая концепция

**Виджет = Оркестратор компонентов**

Виджет в `handler/` НЕ содержит логику напрямую. Вместо этого он:
1. **Импортирует** компоненты из `node/` (Trigger, Code, Answer)
2. **Создает** локальный реестр Answer-ов
3. **Оркестрирует** вызовы: Trigger → Code → Answer
4. **Регистрируется** в роутере через декоратор

```
┌────────────────────────────────────┐
│  handler/start_command_widget.py   │  ← Виджет-оркестратор
├────────────────────────────────────┤
│ from node.control.trigger import   │
│ from node.control.code import      │
│ from node.control.answer import    │
│                                    │
│ ANSWER_REGISTRY = {               │
│   "new_user": NewUserAnswer(),    │
│   "vacancy_list": VacancyListAnswer() │
│ }                                  │
│                                    │
│ @router.message(Command("start")) │
│ async def handle_start(...):      │
│   trigger_data = trigger.run()    │
│   code_result = code.run()        │
│   answer.run()                    │
└────────────────────────────────────┘
```

### 🏷️ Система тегов
Виджеты группируются по **тегам** - логическим блокам функциональности.

**Примеры тегов:**
- `control` - управляющие команды (/start, /settings)
- `vacancy` - работа с вакансиями
- `payment` - обработка платежей
- `interview` - проведение интервью

### 📂 Группировка по Feature ID

Внутри тега виджеты группируются по **Feature ID** из PRD (`prd.json`). Каждая фича = отдельная директория `F{NNN}/`.

```
handler/
└── v1/
    └── user/
        └── notes/                          # тег
            ├── __init__.py
            ├── router.py
            ├── F001/                       # Feature ID: F001 — Управление заметками
            │   ├── __init__.py
            │   ├── create_note_widget.py
            │   ├── list_notes_widget.py
            │   └── delete_note_widget.py
            └── F002/                       # Feature ID: F002 — Шаблоны заметок
                ├── __init__.py
                └── manage_templates_widget.py
```

Правила:
- Директория фичи именуется строго по Feature ID: `F001`, `F002`, ...
- Виджеты внутри именуются `{name}_widget.py` как обычно
- Импорт и регистрация выполняются через `router.py` тега
- В `handler/v1/user/{tag}/__init__.py` импортируйте виджеты из поддиректорий фич
- В документации указывайте **полный путь** до виджета при перечислении связей

### 📁 Что содержит
- **Директории по тегам:** Каждый тег = отдельная директория
- **Виджеты-оркестраторы:** Каждый виджет = отдельный файл `{name}_widget.py`
- **Роутеры:** Файлы `router.py` для регистрации хендлеров

---

## Внутренняя архитектура

### 📂 Структура пакета

```
handler/
├── v1/
│   ├── user/                          # Пользовательские виджеты
│   │   ├── router.py                  # Роутеры по тегам
│   │   ├── control/                   # Тег: control
│   │   │   ├── __init__.py
│   │   │   └── F001/                  # Feature: F001 — Базовые команды
│   │   │       ├── __init__.py
│   │   │       ├── start_command_widget.py
│   │   │       └── help_command_widget.py
│   │   ├── notes/                     # Тег: notes
│   │   │   ├── __init__.py
│   │   │   └── F002/                  # Feature: F002 — Управление заметками
│   │   │       ├── __init__.py
│   │   │       ├── create_note_widget.py
│   │   │       ├── list_notes_widget.py
│   │   │       └── delete_note_widget.py
│   │   └── payment/                   # Тег: payment
│   │       ├── __init__.py
│   │       └── F003/                  # Feature: F003 — Подписки и оплата
│   │           ├── __init__.py
│   │           └── select_package_widget.py
│   │
│   └── admin/                         # Административные виджеты
│       ├── router.py
│       └── management/
│           ├── __init__.py
│           └── user_list_widget.py
│
├── include_router.py                  # Подключение роутеров и middleware
└── middleware/                        # Middleware для хендлеров
    ├── __init__.py
    ├── register_middleware.py
    ├── large_middleware.py
    └── error_middleware.py
```

---

## Виджет-оркестратор

### 🎯 Что такое виджет-оркестратор?

Виджет-оркестратор - это функция-хендлер, которая:
1. **Импортирует** компоненты из `node/{tag}/`
2. **Создает** локальный реестр Answer-ов (маппинг название → класс)
3. **Последовательно вызывает** Trigger → Code → Answer
4. **Регистрируется** в роутере через декоратор (`@router.message()` или `@router.callback_query()`)

### 📝 Структура виджета-оркестратора

```python
"""
Виджет: {Название виджета}.

Feature: {Feature ID} — {Название фичи}
Scenarios: {SC001}, {SC002}

{Описание функциональности виджета}.
{SC001} — {краткое описание сценария 1}
{SC002} — {краткое описание сценария 2}
"""

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from handler.v1.user.router import {tag}_router
from core.vocab import COMMANDS

# Импортируем компоненты из node
from node.{tag}.trigger.{action}_trigger import {Action}Trigger
from node.{tag}.code.{action}_code import {Action}Code
from node.{tag}.answer.{state1}_answer import {State1}Answer
from node.{tag}.answer.{state2}_answer import {State2}Answer

# Реестр Answer-ов для этого виджета
ANSWER_REGISTRY = {
    "state1": {State1}Answer(),  # SC001
    "state2": {State2}Answer()   # SC002
}

@{tag}_router.message(Command(COMMANDS["{command}"]))
async def handle_{widget_name}(
    event: Message | CallbackQuery,
    state: FSMContext,
    user_lang: str,
    **kwargs
):
    """
    Главный хендлер виджета {название}.
    
    Feature: {Feature ID}
    Scenarios: {SC001}, {SC002}
    
    Входные состояния: {список состояний}
    Выходные состояния: {список состояний}
    
    FSM на входе:
    - {field1}: {type} ({required/optional}) - {описание}
    
    FSM на выходе (Code записывает):
    - {field2}: {type} ({required/optional}) - {описание}
    
    FSM на выходе (Answer записывает):
    - {field3}: {type} ({required/optional}) - {описание} ({в каком Answer})
    
    Возможные Answer:
    - {answer_name1} ({AnswerClass1}) - если {условие} → SC001
      Показывает: {что отображает}
      Компонент: node/{tag}/answer/{answer}_answer.py
    
    - {answer_name2} ({AnswerClass2}) - если {условие} → SC002
      Показывает: {что отображает}
      Компонент: node/{tag}/answer/{answer}_answer.py
    
    Архитектура:
    1. {Action}Trigger - {что делает}
    2. {Action}Code - {что делает}
    3. Answer из реестра - {что делает}
    """
    
    # Шаг 1: Trigger (визуальные операции)
    trigger = {Action}Trigger()
    trigger_data = await trigger.run(event, state)
    
    # Шаг 2: Code (бизнес-логика)
    code = {Action}Code()
    code_result = await code.run(trigger_data, state, **kwargs)
    
    # Шаг 3: Answer (отрисовка экрана)
    answer_name = code_result["answer_name"]
    answer = ANSWER_REGISTRY[answer_name]
    await answer.run(
        event=event,
        user_lang=user_lang,
        data=code_result["data"]
    )
```

### 📖 Правила документирования виджета

**Обязательно указать в docstring хендлера:**

1. **Входные состояния** - какие FSM состояния принимает виджет
2. **Выходные состояния** - в какие FSM состояния переводит
3. **FSM на входе** - какие поля FSM нужны (required/optional)
4. **FSM на выходе (Code)** - какие поля записывает Code
5. **FSM на выходе (Answer)** - какие поля записывает каждый Answer
6. **Возможные Answer** - список Answer с описанием:
   - Название Answer в реестре
   - Класс Answer
   - Условие когда показывается
   - Что отображает
   - Путь к компоненту в node/
7. **Архитектура** - краткое описание работы компонентов

#### 🔗 Связи в человекочитаемом виде
В docstring виджета добавляйте блок, фиксирующий входящие и исходящие связи в дополнение к полям `from`/`to` в схеме:

```
Доступен из:
1. widget_name (+ путь до него)
   - Из какого state (+ путь до него)
   - Из какого answer (+ путь до него)
2. ...

Переводит в:
1. widget_name (+ путь до него)
   - В каком state (+ путь до него)
   - Из какого answer (+ путь до него)
2. ...
```

Пояснения:
- «Из какого state» — состояние FSM источника, в котором активируется переход.
- «Из какого answer» — Answer источника, по результату которого выполняется переход.
- «В каком state» — состояние FSM, которое устанавливается целевым Answer текущего виджета.

### 📱 Пример виджета команды /start

**Файл:** `handler/v1/user/control/F001/start_command_widget.py`

```python
"""
Виджет: Команда /start.

Feature: F001 — Базовые команды
Scenarios: SC001, SC002

Точка входа в бота.
SC001 — новый пользователь получает выбор языка.
SC002 — существующий пользователь видит список вакансий.

Доступен из:
1. entry (handler/v1/user/control/F001/start_command_widget.py)
   - Из какого state: любое (*)
   - Из какого answer: — (команда)

Переводит в:
1. registration (handler/v1/user/onboarding/F002/registration_widget.py)
   - В каком state: state/onboarding.py::registration_started
   - Из какого answer: new_user (node/control/answer/new_user_answer.py)
2. vacancy/list (handler/v1/user/vacancy/F003/list_widget.py)
   - В каком state: state/vacancy.py::vacancy_list
   - Из какого answer: vacancy_list (node/control/answer/vacancy_list_answer.py)
"""

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from handler.v1.user.router import control_router
from core.vocab import COMMANDS

# Импортируем компоненты из node
from node.control.trigger.start_command_trigger import StartCommandTrigger
from node.control.code.start_command_code import StartCommandCode
from node.control.answer.new_user_answer import NewUserAnswer
from node.control.answer.vacancy_list_answer import VacancyListAnswer

# Реестр Answer-ов для этого виджета
ANSWER_REGISTRY = {
    "new_user": NewUserAnswer(),
    "vacancy_list": VacancyListAnswer()
}

@control_router.message(Command(COMMANDS["start"]))
async def handle_start_command(
    message: Message,
    state: FSMContext,
    user_lang: str,
    is_new_user: bool
):
    """
    Главный хендлер команды /start.
    
    Входные состояния: любое (*)
    Выходные состояния: None (idle)
    
    FSM на входе:
    - нет обязательных полей
    
    FSM на выходе (Code записывает):
    - нет записей (FSM очищается в Trigger)
    
    FSM на выходе (Answer записывает):
    - нет записей
    
    Возможные Answer:
    - new_user (NewUserAnswer) - если is_new_user=True
      Показывает: выбор языка для нового пользователя
      Компонент: node/control/answer/new_user_answer.py
    
    - vacancy_list (VacancyListAnswer) - если is_new_user=False
      Показывает: список вакансий пользователя с пагинацией
      Компонент: node/control/answer/vacancy_list_answer.py
    
    Архитектура:
    1. StartCommandTrigger - очистка сообщений и FSM
    2. StartCommandCode - проверка is_new_user и получение вакансий
    3. Answer из реестра - отображение экрана
    """
    
    # Шаг 1: Trigger (визуальные операции)
    trigger = StartCommandTrigger()
    trigger_data = await trigger.run(message, state)
    
    # Шаг 2: Code (бизнес-логика)
    code = StartCommandCode()
    code_result = await code.run(trigger_data, state, is_new_user)
    
    # Шаг 3: Answer (отрисовка экрана)
    answer_name = code_result["answer_name"]
    answer = ANSWER_REGISTRY[answer_name]
    await answer.run(
        message=message,
        user_lang=user_lang,
        data=code_result["data"]
    )
```

**Что происходит:**
1. Импортируем компоненты из `node/control/`
2. Создаем локальный реестр Answer-ов
3. В хендлере последовательно вызываем Trigger → Code → Answer
4. Регистрируем через декоратор `@control_router.message()`

**Переиспользование компонентов:**
- `VacancyListAnswer` может использоваться в других виджетах (например, в `/vacancy`)
- `StartCommandTrigger` может использоваться где нужна такая же очистка
- Каждый компонент изолирован и тестируется отдельно

---

## Чек-лист добавления виджета

### ✅ Добавление нового виджета-оркестратора

#### Шаг 0: Трассируемость (PRD)

- [ ] **Определить Feature ID** из `prd.json` (например, `F001`)
- [ ] **Определить Scenario ID** — какие сценарии покрывает виджет (например, `SC001`, `SC002`)
- [ ] **Убедиться**, что сценарии описаны в `prd.json` → `acceptance_criteria`

#### Шаг 1: Создание компонентов в node/

- [ ] **Создать Trigger** в `node/{tag}/trigger/{action}_trigger.py`
  - См. документацию: [node.md](node.md#trigger---визуальные-операции)
  - Следовать шаблону и правилам документирования
  - В docstring указать Feature ID и Scenario ID
  
- [ ] **Создать Code** в `node/{tag}/code/{action}_code.py`
  - См. документацию: [node.md](node.md#code---бизнес-логика)
  - Описать бизнес-логику пошагово
  - Перечислить все сервисы
  - Описать все условия роутинга
  - В docstring указать Feature ID и Scenario ID
  
- [ ] **Создать Answer-ы** в `node/{tag}/answer/{state}_answer.py`
  - См. документацию: [node.md](node.md#answer---отрисовка-экранов)
  - Один Answer = одно состояние экрана
  - Указать где используется
  - В docstring указать Feature ID и Scenario ID

#### Шаг 2: Создание виджета-оркестратора

- [ ] **Определить тег** - к какому тегу относится виджет
- [ ] **Определить Feature ID** — к какой фиче относится виджет
- [ ] **Проверить существование директории** `handler/v1/user/{tag}/{Feature ID}/`
- [ ] **Если директории нет** - создать `handler/v1/user/{tag}/{Feature ID}/`
- [ ] **Создать файл виджета** `{name}_widget.py`
- [ ] **Импортировать компоненты** из `node/{tag}/`
- [ ] **Создать локальный реестр Answer-ов** `ANSWER_REGISTRY = {...}`
- [ ] **Создать функцию-хендлер** `async def handle_{name}(...)`
- [ ] **В docstring хендлера указать:**
  - [ ] **Feature ID** и **Scenario ID** (обязательно!)
  - [ ] Входные состояния FSM
  - [ ] Выходные состояния FSM  
  - [ ] FSM на входе (required/optional)
  - [ ] FSM на выходе (Code)
  - [ ] FSM на выходе (Answer)
  - [ ] **Возможные Answer** с описанием и привязкой к Scenario ID:
    - Название Answer
    - Класс Answer
    - Условие когда показывается
    - Что отображает
    - Путь к компоненту
  - [ ] Архитектура (Trigger → Code → Answer)
- [ ] **Реализовать последовательные вызовы:**
  - [ ] Trigger → получить trigger_data
  - [ ] Code → получить code_result с answer_name
  - [ ] Answer → вызвать нужный Answer из реестра
- [ ] **Зарегистрировать хендлер** через декоратор `@router.message()` или `@router.callback_query()`

#### Шаг 3: Подключение роутера (если тег новый)

- [ ] **Проверить router.py** - есть ли роутер для тега
- [ ] **Если нет** - создать роутер в `handler/v1/user/router.py`:
```python
  {tag}_router = Router()
  ```
- [ ] **Импортировать виджет** в `handler/v1/user/{tag}/__init__.py`
- [ ] **Подключить роутер** в `handler/include_router.py`:
```python
  from handler.v1.user import {tag}_router
  dp.include_router({tag}_router)
  ```

### 📋 Шаблон виджета-оркестратора

См. раздел [Структура виджета-оркестратора](#📝-структура-виджета-оркестратора) выше.

---

## 📡 Подключение роутеров и middleware

### Роутеры

**1. Создаем роутеры в `handler/v1/user/router.py`:**

```python
"""Роутеры для пользовательских виджетов."""
from aiogram import Router

# Создаем роутеры для каждого тега
control_router = Router()
vacancy_router = Router()
payment_router = Router()
interview_router = Router()
```

**2. Импортируем роутер в виджете:**

```python
from handler.v1.user.router import control_router

@control_router.message(Command("start"))
async def handle_start_command(...):
    """Виджет команды /start"""
```

**3. Подключаем роутер в `handler/include_router.py`:**

```python
from handler.v1.user import (
    control_router,
    vacancy_router,
    payment_router,
    interview_router,
)
from core import dp

dp.include_router(control_router)
dp.include_router(vacancy_router)
dp.include_router(payment_router)
dp.include_router(interview_router)
```

### Middleware

**Создаем middleware в `handler/middleware/`:**

Каждый middleware должен содержать документацию с описанием:
- **Назначение** - для чего нужен middleware
- **Что отлавливает** - какие события/данные обрабатывает
- **Что возвращает** - результат обработки

**Пример middleware:**

```python
"""
Middleware для проверки авторизации пользователей.

Назначение: Проверяет авторизован ли пользователь в системе перед 
обработкой его запросов.

Что отлавливает: Все входящие сообщения и колбеки от пользователей

Что возвращает: 
- Продолжает выполнение если пользователь авторизован
- Перенаправляет на регистрацию если пользователь не найден
- Блокирует выполнение если пользователь заблокирован
"""

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

class AuthMiddleware(BaseMiddleware):
    """Middleware для проверки авторизации."""
    
    async def __call__(self, handler, event, data):
        """
        Обработать событие.
        
        Args:
            handler: Следующий обработчик в цепочке
            event: Событие (Message или CallbackQuery)
            data: Данные контекста
            
        Returns:
            Результат выполнения handler или None если заблокировано
        """
        user_id = event.from_user.id
        
        # Проверяем авторизацию
        if not await self._is_user_authorized(user_id):
            await self._handle_unauthorized_user(event)
            return None
        
        # Продолжаем выполнение
        return await handler(event, data)
```

**Подключаем middleware:**

```python
# handler/include_middlewares.py
from .middleware import RegisterMiddleware, LargeMessageMiddleware, ErrorMiddleware
from handler.v1 import dp

dp.message.middleware(ErrorMiddleware())
dp.callback_query.middleware(ErrorMiddleware())
dp.message.middleware(RegisterMiddleware())
dp.callback_query.middleware(RegisterMiddleware())
dp.message.middleware(LargeMessageMiddleware())
```

---

## 🎉 Заключение

Пакет `handler` - это слой оркестрации, который:
- 🎯 **Собирает** компоненты из `node/` в рабочие виджеты
- 📋 **Регистрирует** обработчики событий Telegram
- 🔄 **Не дублирует** логику - переиспользует компоненты
- 📖 **Документирует** все возможные Answer и переходы

**Правило:** Виджет в `handler/` только оркестрирует, вся логика в `node/`.
