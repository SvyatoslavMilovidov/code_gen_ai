# 🧩 Пакет `node`

## 📋 Оглавление
1. [Описание пакета](#описание-пакета)
2. [Внутренняя архитектура](#внутренняя-архитектура)
3. [Типы компонентов](#типы-компонентов)
   - [Trigger](#trigger---визуальные-операции)
   - [Code](#code---бизнес-логика)
   - [Answer](#answer---отрисовка-экранов)
   - [Работа с FSM состояниями](#-работа-с-fsm-состояниями---полный-пример)
4. [Переиспользование компонентов](#переиспользование-компонентов)
5. [Чек-листы](#чек-листы)

---

## Описание пакета

### 🎯 Назначение
Пакет `node` содержит **переиспользуемые UI-компоненты** для построения виджетов. Компоненты организованы по **тегам** (функциональным областям) и представляют собой независимые строительные блоки для создания пользовательских интерфейсов.

### 🏷️ Система тегов
Компоненты группируются по **тегам** - логическим блокам функциональности.

**Примеры тегов:**
- `control` - управляющие команды (/start, /settings)
- `vacancy` - работа с вакансиями
- `payment` - обработка платежей
- `interview` - проведение интервью

### 💡 Ключевая идея

**Виджет = Оркестратор компонентов**

Виджет в `handler/` не содержит логики напрямую, а собирается из готовых кирпичиков:
- **Trigger** из `node/{tag}/trigger/` - визуальные операции
- **Code** из `node/{tag}/code/` - бизнес-логика
- **Answer** из `node/{tag}/answer/` - отрисовка экранов

```
┌─────────────────────────────────────────────┐
│         handler/start_command_widget.py     │
│                (Оркестратор)                │
├─────────────────────────────────────────────┤
│  1. Импортирует компоненты из node/         │
│  2. Создает реестр Answer-ов                │
│  3. Вызывает: Trigger → Code → Answer       │
│  4. Регистрируется в роутере                │
└─────────────────────────────────────────────┘
         ↓              ↓              ↓
    ┌─────────┐   ┌─────────┐   ┌─────────┐
    │ Trigger │   │  Code   │   │ Answer  │
    │ (node/) │   │ (node/) │   │ (node/) │
    └─────────┘   └─────────┘   └─────────┘
```

### ✨ Преимущества

- ✅ **Полное переиспользование** - один Answer используется в разных виджетах
- ✅ **Изменения в одном месте** - поменял логику в компоненте → изменения везде
- ✅ **LEGO-подход** - собираем виджеты из готовых блоков
- ✅ **Легко тестировать** - каждый компонент тестируется изолированно
- ✅ **Четкое разделение** - визуал, логика и UI разделены
- ✅ **Масштабируемость** - добавляем компоненты, а не копируем код

---

## Внутренняя архитектура

### 📂 Структура пакета

```
node/
├── {tag_name}/                    # Тег (функциональная область)
│   ├── trigger/                   # Trigger-компоненты тега
│   │   ├── __init__.py
│   │   ├── {action}_trigger.py   # Конкретный Trigger
│   │   └── ...
│   ├── code/                      # Code-компоненты тега
│   │   ├── __init__.py
│   │   ├── {action}_code.py      # Конкретный Code
│   │   └── ...
│   └── answer/                    # Answer-компоненты тега
│       ├── __init__.py
│       ├── {state}_answer.py     # Конкретный Answer
│       └── ...
└── {another_tag}/
    └── ...
```

### 📱 Пример структуры

```
node/
├── control/                           # Тег: control
│   ├── trigger/
│   │   ├── __init__.py
│   │   ├── start_command_trigger.py   # StartCommandTrigger
│   │   └── settings_command_trigger.py
│   ├── code/
│   │   ├── __init__.py
│   │   ├── start_command_code.py      # StartCommandCode
│   │   └── settings_command_code.py
│   └── answer/
│       ├── __init__.py
│       ├── new_user_answer.py         # NewUserAnswer
│       ├── vacancy_list_answer.py     # VacancyListAnswer (общий!)
│       └── profile_answer.py
│
├── vacancy/                           # Тег: vacancy
│   ├── trigger/
│   │   ├── __init__.py
│   │   ├── list_vacancies_trigger.py
│   │   └── select_vacancy_trigger.py
│   ├── code/
│   │   ├── __init__.py
│   │   ├── list_vacancies_code.py
│   │   └── select_vacancy_code.py
│   └── answer/
│       ├── __init__.py
│       ├── vacancy_detail_answer.py
│       ├── vacancy_empty_answer.py
│       └── vacancy_deleted_answer.py
│
└── payment/                           # Тег: payment
    ├── trigger/
    │   ├── __init__.py
    │   └── select_package_trigger.py
    ├── code/
    │   ├── __init__.py
    │   └── select_package_code.py
    └── answer/
        ├── __init__.py
        ├── package_list_answer.py
        └── payment_success_answer.py
```

### 🎯 Именование файлов и классов

**Правило:** `{название}_{тип}.py` → `{Название}{Тип}`

| Тип | Файл | Класс |
|-----|------|-------|
| **Trigger** | `start_command_trigger.py` | `StartCommandTrigger` |
| **Code** | `start_command_code.py` | `StartCommandCode` |
| **Answer** | `vacancy_list_answer.py` | `VacancyListAnswer` |

---

## Типы компонентов

### Trigger - Визуальные операции

#### 🎯 Назначение
Trigger отвечает **только за визуальные операции**. Это первый этап обработки события, который подготавливает UI к показу нового экрана.

#### ✅ Обязанности Trigger

- **Удаление предыдущих сообщений** пользователя
- **Отправка стикеров/анимаций загрузки**
- **Сброс FSM состояния** (если нужно): `await state.set_state(None)`
- **Очистка FSM данных** (если нужно): `await state.set_data({})`
- **Извлечение базовых данных** из события (user_id, callback_data)

> **Важно:** Trigger только **сбрасывает** состояния, но НЕ устанавливает новые!

#### ❌ Что НЕ делает Trigger

- ❌ Запросы к БД
- ❌ Вызовы сервисов
- ❌ Бизнес-логика
- ❌ Валидация данных
- ❌ Вычисления

#### 📝 Структура Trigger

```python
class SomeTrigger:
    async def run(self, event, state) -> dict:
        """
        Выполнить визуальные операции.
        
        Args:
            event: Message или CallbackQuery от Telegram
            state: FSM контекст
            
        Returns:
            dict: Данные для передачи в Code
        """
        # Визуальные операции
        # ...
        
        return {
            "telegram_id": int,
            "event": event,
            # ... другие базовые данные
        }
```

#### 📋 Шаблон Trigger

```python
"""
Trigger для {описание действия}.

Feature: {Feature ID} — {Название фичи}
Scenarios: {SC001}, {SC002}

Используется в виджетах:
- handler/v1/user/{tag}/{Feature ID}/{widget}_widget.py
"""

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import service

class {Name}Trigger:
    """
    Trigger для {описание}.
    
    Выполняет визуальные операции:
    - {операция 1}
    - {операция 2}
    - {операция 3}
    """
    
    async def run(self, event: Message | CallbackQuery, state: FSMContext):
        """
        Выполнить визуальные операции.
        
        Args:
            event: Message или CallbackQuery событие от Telegram
            state: FSM контекст
            
        Returns:
            dict: Данные для передачи в Code
            {
                "telegram_id": int,
                "event": Message | CallbackQuery,
                # ... другие поля
            }
        """
        # Удаляем предыдущие сообщения
        telegram_id = event.from_user.id
        msgs_ids = await service.db_serv.get_user_messages(telegram_id)
        await service.message_serv.delete_messages(msgs_ids, telegram_id)
        await service.db_serv.delete_user_messages(telegram_id)
        
        # Сбрасываем FSM (если нужно)
        await state.set_state(None)
        await state.set_data({})
        
        return {
            "telegram_id": telegram_id,
            "event": event
        }
```

#### 📖 Правила документирования Trigger

**Обязательно указать:**
1. **В docstring модуля:**
   - Описание действия Trigger
   - Список виджетов где используется
2. **В docstring класса:**
   - Список выполняемых визуальных операций
3. **В docstring метода run():**
   - Args с типами
   - Returns с описанием всех полей

---

### Code - Бизнес-логика

#### 🎯 Назначение
Code отвечает за **выполнение бизнес-логики** и **определение какой Answer показать**. Это сердце виджета, содержащее всю логику обработки.

#### ✅ Обязанности Code

- **Извлечение данных** из trigger_data и FSM
- **Валидация входных данных**
- **Вызовы сервисов** (БД, API, ML, email и т.д.)
- **Вычисления и обработка данных**
- **Проверка бизнес-правил**
- **Установка FSM состояний**: `await state.set_state(SomeState.waiting_input)`
- **Запись данных в FSM**: `await state.update_data(...)`
- **Определение результата** (какой Answer показать)

> **Важно:** Установка нового FSM состояния — это **бизнес-решение**, поэтому делается в Code!

#### 📝 Структура Code

```python
class SomeCode:
    async def run(self, trigger_data, state, **kwargs) -> dict:
        """Главный метод."""
        result = await self._execute_business_logic(...)
        return await self._route_to_answer(result)
    
    async def _execute_business_logic(self, ...) -> dict:
        """Выполнить всю бизнес-логику."""
        # Вся логика здесь
        pass
    
    async def _route_to_answer(self, result: dict) -> dict:
        """Определить какой Answer использовать."""
        if condition1:
            return {"answer_name": "state1", "data": result}
        if condition2:
            return {"answer_name": "state2", "data": result}
        return {"answer_name": "default", "data": result}
```

#### 📋 Шаблон Code

```python
"""
Code для {описание действия}.

Feature: {Feature ID} — {Название фичи}
Scenarios: {SC001}, {SC002}

Задача: {подробное описание бизнес-логики}.
{SC001} — {условие} → answer: {answer_name_1}
{SC002} — {условие} → answer: {answer_name_2}

Используется в виджетах:
- handler/v1/user/{tag}/{Feature ID}/{widget}_widget.py
"""

from aiogram.fsm.context import FSMContext
import service

class {Name}Code:
    """
    Класс для бизнес-логики {описание}.
    
    ⚠️ ВАЖНО: {краткое описание что делает эта бизнес-логика}
    
    Бизнес-логика:
    1. {шаг 1}
    2. {шаг 2}
    3. {шаг 3}
    4. {шаг 4}
    5. {шаг 5}
    
    Используемые сервисы:
    - service.{service_name}.{method}() - {описание}
    - service.{service_name}.{method}() - {описание}
    
    Условия роутинга к Answer:
    - {условие 1} → "{answer_name_1}" ({AnswerClassName1})
    - {условие 2} → "{answer_name_2}" ({AnswerClassName2})
    - иначе → "{default}" ({DefaultAnswerClass})
    """
    
    async def run(self, trigger_data: dict, state: FSMContext, **kwargs):
        """
        Выполнить бизнес-логику и выбрать Answer.
        
        Бизнес-логика:
        1. {детальное описание шага 1}
        2. {детальное описание шага 2}
        3. {детальное описание шага 3}
        
        Args:
            trigger_data: Данные от Trigger
            {
                "telegram_id": int - описание,
                "event": Message | CallbackQuery - описание,
                # ... другие поля
            }
            state: FSM контекст
            **kwargs: Дополнительные параметры
            {
                "param1": type - описание (если есть)
            }
            
        Returns:
            dict: Название Answer + данные для него
            {
                "answer_name": str,  # Название Answer
                "data": dict         # Данные для Answer
            }
        """
        # Выполняем бизнес-логику
        result = await self._execute_business_logic(trigger_data, state, **kwargs)
        
        # Определяем какой Answer нужен
        return await self._route_to_answer(result)
    
    async def _execute_business_logic(
        self, 
        trigger_data: dict, 
        state: FSMContext,
        **kwargs
    ) -> dict:
        """
        Выполнить всю бизнес-логику.
        
        Бизнес-логика:
        1. {подробное описание каждого шага}
        2. {что делаем}
        3. {какие сервисы вызываем}
        4. {что записываем в FSM}
        
        Returns:
            dict: Результат обработки со всеми данными
            {
                "field1": type - описание,
                "field2": type - описание,
                # ...
            }
        """
        telegram_id = trigger_data["telegram_id"]
        
        # Бизнес-логика здесь
        # ...
        
        return {
            "telegram_id": telegram_id,
            # ... результаты обработки
        }
    
    async def _route_to_answer(self, result: dict) -> dict:
        """
        Определить какой Answer использовать.
        
        Проверяет условия и выбирает подходящий Answer.
        
        Args:
            result: Результат бизнес-логики
            
        Returns:
            dict: Название Answer + данные
        """
        # Проверяем условия
        if result.get("condition1"):
            return {"answer_name": "state1", "data": result}
        
        if result.get("condition2"):
            return {"answer_name": "state2", "data": result}
        
        return {"answer_name": "default", "data": result}
```

#### 📖 Правила документирования Code

**Обязательно указать:**
1. **В docstring модуля:**
   - Задача Code (что за бизнес-логика)
   - Список виджетов где используется
2. **В docstring класса:**
   - Подробная бизнес-логика (пошагово)
   - ВСЕ используемые сервисы
   - ВСЕ условия роутинга к Answer
3. **В docstring метода run():**
   - Детальное описание бизнес-логики
   - Args с типами и описанием каждого поля
   - Returns с структурой данных
4. **В docstring метода _execute_business_logic():**
   - Подробное описание логики
   - Returns с описанием всех полей результата
5. **В docstring метода _route_to_answer():**
   - Описание логики роутинга

---

### Answer - Отрисовка экранов

#### 🎯 Назначение
Answer отвечает за **формирование и отправку UI экрана** пользователю. Один Answer = одно состояние экрана.

#### ✅ Обязанности Answer

- **Формирование текста сообщения** (с подстановкой данных)
- **Построение клавиатур** (inline, reply)
- **Отправка медиа** (фото, видео, стикеры, документы)
- **Сохранение ID отправленных сообщений** (для последующего удаления)
- **Опционально: легкая бизнес-логика** (логирование, метрики, UI-вычисления)

> **Важно:** Answer НЕ работает с FSM состояниями - только рисует UI!

#### 💡 Особенность Answer

Answer **МОЖЕТ** содержать свою бизнес-логику, но только связанную с UI:
- ✅ Логирование событий показа экрана
- ✅ Отправка метрик и аналитики
- ✅ Легкие вычисления для отображения (форматирование, подсчет)
- ❌ НЕ должен делать основные бизнес-запросы (это задача Code)

#### 📝 Структура Answer

```python
class SomeAnswer:
    async def run(self, event, user_lang: str, data: dict, **kwargs):
        """Отрисовать экран."""
        # Формируем текст
        text = self._build_text(data, user_lang)
        
        # Формируем клавиатуру
        keyboard = self._build_keyboard(data, user_lang, **kwargs)
        
        # Отправляем
        msg = await event.message.answer(text=text, reply_markup=keyboard)
        
        # Сохраняем ID сообщений
        await service.db_serv.create_messages(data["telegram_id"], [msg.message_id])
    
    def _build_text(self, data: dict, user_lang: str) -> str:
        """Построить текст сообщения."""
        pass
    
    def _build_keyboard(self, data: dict, user_lang: str, **kwargs):
        """Построить клавиатуру."""
        pass
```

#### 📋 Шаблон Answer

```python
"""
Answer: {Название состояния экрана}.

Feature: {Feature ID} — {Название фичи}
Scenario: {SC001}

Состояние экрана: {Описание когда показывается}.
Отображение: {Что видит пользователь}.

Используется в виджетах:
- handler/v1/user/{tag}/{Feature ID}/{widget1}_widget.py ({условие})
- handler/v1/user/{tag}/{Feature ID}/{widget2}_widget.py ({условие})
"""

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.vocab import MESSAGES, BUTTONS
from callback.user.{tag} import {SomeCallback}
import service

class {Name}Answer:
    """
    Answer для {описание состояния экрана}.
    
    Бизнес-логика Answer (если есть):
    1. {шаг 1 - например, логирование}
    2. {шаг 2 - например, метрики}
    
    Используемые сервисы (если есть):
    - service.{service}.{method}() - {описание}
    
    Используемые тексты:
    - MESSAGES["{key}"] - {описание}
    - BUTTONS["{key}"] - {описание}
    
    Используемые колбеки:
    - {CallbackName} - {описание}
    """
    
    async def run(
        self,
        event: Message | CallbackQuery,
        user_lang: str,
        data: dict,
        **kwargs
    ):
        """
        Отрисовать состояние экрана.
        
        Args:
            event: Message или CallbackQuery для отправки ответа
            user_lang: Язык пользователя
            data: Данные от Code
            {
                "telegram_id": int - описание,
                "field1": type - описание,
                # ... другие поля
            }
            **kwargs: Дополнительные параметры
            {
                "text_override": str (optional) - переопределить текст
                "show_back_button": bool (optional) - показать кнопку "Назад"
                # ... другие параметры
            }
        """
        telegram_id = data["telegram_id"]
        
        # Бизнес-логика Answer (если есть)
        # Например: логирование, метрики
        
        # Формируем текст
        text = kwargs.get("text_override") or self._build_text(data, user_lang)
        
        # Формируем клавиатуру
        keyboard = self._build_keyboard(data, user_lang, **kwargs)
        
        # Отправляем
        message_obj = event if isinstance(event, Message) else event.message
        msg = await message_obj.answer(text=text, reply_markup=keyboard)
        
        # Сохраняем ID сообщений
        await service.db_serv.create_messages(telegram_id, [msg.message_id])
    
    def _build_text(self, data: dict, user_lang: str) -> str:
        """
        Построить текст сообщения.
        
        Args:
            data: Данные от Code
            user_lang: Язык пользователя
            
        Returns:
            str: Текст сообщения
        """
        # Формирование текста
        return MESSAGES["{key}"][user_lang].format(**data)
    
    def _build_keyboard(
        self, 
        data: dict, 
        user_lang: str,
        **kwargs
    ) -> InlineKeyboardMarkup:
        """
        Построить клавиатуру.
        
        Args:
            data: Данные от Code
            user_lang: Язык пользователя
            **kwargs: Дополнительные параметры
            
        Returns:
            InlineKeyboardMarkup: Клавиатура
        """
        builder = InlineKeyboardBuilder()
        
        # Построение клавиатуры
        builder.button(
            text=BUTTONS["{key}"][user_lang],
            callback_data={SomeCallback}().pack()
        )
        
        return builder.as_markup()
```

#### 📖 Правила документирования Answer

**Обязательно указать:**
1. **В docstring модуля:**
   - Название состояния экрана
   - Когда показывается
   - Что отображается
   - **Список виджетов где используется** (важно!)
2. **В docstring класса:**
   - Описание экрана
   - Бизнес-логика Answer (если есть)
   - Используемые сервисы (если есть)
   - Используемые тексты (MESSAGES, BUTTONS)
   - Используемые колбеки
3. **В docstring метода run():**
   - Args с типами и описанием всех полей data и kwargs
   - Описание работы метода
4. **В docstring методов _build_*():**
   - Args и Returns
   - Описание логики построения

---

### 🔄 Работа с FSM состояниями - полный пример

#### Типичный Flow обработки события

```python
# 1️⃣ Trigger - сброс старого состояния
class StartVacancyCreationTrigger:
    async def run(self, event, state):
        telegram_id = event.from_user.id
        
        # Удаляем сообщения
        msgs_ids = await service.db_serv.get_user_messages(telegram_id)
        await service.message_serv.delete_messages(msgs_ids, telegram_id)
        await service.db_serv.delete_user_messages(telegram_id)
        
        # Сбрасываем старое состояние
        await state.set_state(None)
        await state.set_data({})
        
        return {
            "telegram_id": telegram_id,
            "event": event
        }

# 2️⃣ Code - установка нового состояния
class StartVacancyCreationCode:
    async def _execute_business_logic(self, trigger_data, state, **kwargs):
        telegram_id = trigger_data["telegram_id"]
        
        # Проверяем права
        user = await service.db_serv.get_user(telegram_id)
        if not user.can_create_vacancy:
            return {"error": "no_permission"}
        
        # Создаем заготовку вакансии
        vacancy_id = await service.db_serv.create_vacancy_draft(telegram_id)
        
        # ✅ Устанавливаем новое состояние - бизнес-решение!
        await state.set_state(VacancyState.waiting_name)
        await state.update_data(vacancy_id=vacancy_id)
        
        return {
            "telegram_id": telegram_id,
            "vacancy_id": vacancy_id
        }
    
    async def _route_to_answer(self, result):
        if result.get("error"):
            return {"answer_name": "error", "data": result}
        return {"answer_name": "ask_name", "data": result}

# 3️⃣ Answer - только отрисовка UI
class AskVacancyNameAnswer:
    async def run(self, event, user_lang, data, **kwargs):
        telegram_id = data["telegram_id"]
        
        # Формируем текст
        text = MESSAGES["ask_vacancy_name"][user_lang]
        
        # Отправляем сообщение
        message_obj = event if isinstance(event, Message) else event.message
        msg = await message_obj.answer(text=text)
        
        # Сохраняем ID сообщения
        await service.db_serv.create_messages(telegram_id, [msg.message_id])
```

#### Распределение ответственности

| Компонент | Работа с FSM | Пример |
|-----------|--------------|--------|
| **Trigger** | Сброс состояний | `await state.set_state(None)` |
| **Code** | Установка новых состояний | `await state.set_state(VacancyState.waiting_name)` |
| **Answer** | Не работает с FSM | — |

---

## Переиспользование компонентов

### 🎯 Когда компонент переиспользуемый?

**Все компоненты в node/ потенциально переиспользуемы.**

Даже если компонент сейчас используется в одном виджете, он может быть использован в других позже. Поэтому все компоненты размещаются в `node/`.

### 📝 Примеры переиспользования

#### Пример 1: VacancyListAnswer

```python
# Используется в трех виджетах:

# 1. handler/v1/user/control/F001/start_command_widget.py
from node.control.answer.vacancy_list_answer import VacancyListAnswer

answer = VacancyListAnswer()
await answer.run(message, user_lang, data)

# 2. handler/v1/user/vacancy/F002/list_widget.py
from node.control.answer.vacancy_list_answer import VacancyListAnswer

answer = VacancyListAnswer()
await answer.run(message, user_lang, data, show_back_button=True)

# 3. handler/v1/user/vacancy/F002/screening_widget.py
from node.control.answer.vacancy_list_answer import VacancyListAnswer

answer = VacancyListAnswer()
await answer.run(
    message, 
    user_lang, 
    data, 
    text_override="Выберите вакансию для скрининга:"
)
```

#### Пример 2: ClearMessagesTrigger (общий Trigger)

```python
# node/common/trigger/clear_messages_trigger.py

class ClearMessagesTrigger:
    """Общий Trigger для очистки сообщений."""
    
    async def run(self, event, state):
        telegram_id = event.from_user.id
        msgs_ids = await service.db_serv.get_user_messages(telegram_id)
        await service.message_serv.delete_messages(msgs_ids, telegram_id)
        await service.db_serv.delete_user_messages(telegram_id)
        
        return {"telegram_id": telegram_id, "event": event}

# Используется в МНОЖЕСТВЕ виджетов
```

### 🔧 Параметризация через kwargs

Answer может принимать дополнительные параметры для кастомизации:

```python
class VacancyListAnswer:
    async def run(self, event, user_lang, data, **kwargs):
        # Параметры:
        text_override = kwargs.get("text_override")  # Переопределить текст
        show_back_button = kwargs.get("show_back_button", False)  # Кнопка "Назад"
        items_per_page = kwargs.get("items_per_page", 5)  # Элементов на странице
        custom_callback = kwargs.get("custom_callback")  # Свой колбек
        
        # Используем параметры при построении UI
```

**Это позволяет:**
- ✅ Переиспользовать Answer с разными настройками
- ✅ Не дублировать код
- ✅ Сохранять гибкость

### 🔍 Как найти где используется компонент?

**Grep/поиск по проекту:**
```bash
# Найти все использования VacancyListAnswer
grep -r "VacancyListAnswer" handler/
```

**Или смотрим в документации компонента:**
```python
"""
Используется в виджетах:
- handler/v1/user/control/start_command_widget.py
- handler/v1/user/vacancy/list_widget.py
- handler/v1/user/vacancy/screening_widget.py
"""
```

---

## Чек-листы

### ✅ Добавление нового Trigger

- [ ] **Определить тег** к которому относится Trigger
- [ ] **Определить Feature ID и Scenario ID** из `prd.json`
- [ ] **Проверить существование директории** `node/{tag}/trigger/`
- [ ] **Если директории нет** - создать `node/{tag}/trigger/`
- [ ] **Создать файл** `{action}_trigger.py`
- [ ] **Создать класс** `{Action}Trigger`
- [ ] **В docstring модуля:**
  - [ ] Указать Feature ID и Scenario ID (обязательно!)
  - [ ] Описать назначение Trigger
  - [ ] Указать где используется (список виджетов)
- [ ] **В docstring класса:**
  - [ ] Описать что делает
  - [ ] Перечислить все визуальные операции
- [ ] **Реализовать метод run():**
  - [ ] Визуальные операции (удаление, стикеры, FSM)
  - [ ] Возврат данных для Code
- [ ] **В docstring run():**
  - [ ] Описать Args с типами
  - [ ] Описать Returns с полями
- [ ] **Не добавлять бизнес-логику** - только визуал!

---

### ✅ Добавление нового Code

- [ ] **Определить тег** к которому относится Code
- [ ] **Определить Feature ID и Scenario ID** из `prd.json`
- [ ] **Проверить существование директории** `node/{tag}/code/`
- [ ] **Если директории нет** - создать `node/{tag}/code/`
- [ ] **Создать файл** `{action}_code.py`
- [ ] **Создать класс** `{Action}Code`
- [ ] **В docstring модуля:**
  - [ ] Указать Feature ID и Scenario ID (обязательно!)
  - [ ] Описать задачу (что за бизнес-логика)
  - [ ] Указать маппинг сценариев на answer_name
  - [ ] Указать где используется (список виджетов)
- [ ] **В docstring класса:**
  - [ ] Описать бизнес-логику пошагово (нумерованный список)
  - [ ] Перечислить ВСЕ используемые сервисы
  - [ ] Описать ВСЕ условия роутинга к Answer
- [ ] **Реализовать метод run():**
  - [ ] Вызов _execute_business_logic()
  - [ ] Вызов _route_to_answer()
  - [ ] Возврат {"answer_name": str, "data": dict}
- [ ] **В docstring run():**
  - [ ] Описать бизнес-логику детально
  - [ ] Args с типами и описанием каждого поля
  - [ ] Returns с структурой
- [ ] **Реализовать метод _execute_business_logic():**
  - [ ] Вся бизнес-логика
  - [ ] Вызовы сервисов
  - [ ] Запись в FSM (если нужно)
  - [ ] Возврат результата
- [ ] **В docstring _execute_business_logic():**
  - [ ] Подробное описание логики
  - [ ] Returns с описанием всех полей
- [ ] **Реализовать метод _route_to_answer():**
  - [ ] Проверка условий
  - [ ] Возврат answer_name + data
- [ ] **В docstring _route_to_answer():**
  - [ ] Описание логики роутинга

---

### ✅ Добавление нового Answer

- [ ] **Определить тег** к которому относится Answer
- [ ] **Определить Feature ID и Scenario ID** из `prd.json`
- [ ] **Проверить существование директории** `node/{tag}/answer/`
- [ ] **Если директории нет** - создать `node/{tag}/answer/`
- [ ] **Создать файл** `{state}_answer.py`
- [ ] **Создать класс** `{State}Answer`
- [ ] **В docstring модуля:**
  - [ ] Указать Feature ID и Scenario ID (обязательно!)
  - [ ] Название состояния экрана
  - [ ] Когда показывается
  - [ ] Что отображается
  - [ ] **Список виджетов где используется** (обязательно!)
- [ ] **В docstring класса:**
  - [ ] Описание экрана
  - [ ] Бизнес-логика Answer (если есть)
  - [ ] Используемые сервисы (если есть)
  - [ ] Используемые тексты (MESSAGES, BUTTONS)
  - [ ] Используемые колбеки
- [ ] **Реализовать метод run():**
  - [ ] Бизнес-логика Answer (логи, метрики)
  - [ ] Формирование текста
  - [ ] Построение клавиатуры
  - [ ] Отправка сообщения
  - [ ] Сохранение ID сообщений
- [ ] **В docstring run():**
  - [ ] Args с типами и описанием data и kwargs
  - [ ] Описание работы
- [ ] **Реализовать методы _build_*():**
  - [ ] _build_text() - построение текста
  - [ ] _build_keyboard() - построение клавиатуры
  - [ ] Другие вспомогательные методы
- [ ] **В docstring _build_*():**
  - [ ] Args и Returns
  - [ ] Описание логики
- [ ] **Поддержать параметризацию через kwargs:**
  - [ ] text_override
  - [ ] show_back_button
  - [ ] Другие параметры (если нужно)

---

### 📋 Шаблоны компонентов

Полные шаблоны см. в разделах выше:
- [Шаблон Trigger](#📋-шаблон-trigger)
- [Шаблон Code](#📋-шаблон-code)
- [Шаблон Answer](#📋-шаблон-answer)

---

## 🎉 Заключение

Пакет `node` - это фундамент архитектуры, обеспечивающий:
- 🔄 Переиспользование компонентов
- 🎯 Четкое разделение ответственности
- 🧩 LEGO-подход к построению виджетов
- 📈 Масштабируемость без дублирования кода

**Правило:** Все UI-компоненты живут в `node/`, виджеты в `handler/` только оркестрируют их работу.

