# Документация архитектуры HR Bot

## 📋 Оглавление

1. [🌟 Обзор архитектуры](#-обзор-архитектуры)
2. [📚 Документация по пакетам](#-документация-по-пакетам)
3. [🚀 Быстрый старт](#-быстрый-старт)
4. [📖 Соглашения и стандарты](#-соглашения-и-стандарты)

## 🌟 Обзор архитектуры

HR Bot построен по модульной архитектуре с четким разделением ответственности между компонентами:

```
bot_refactor/
├── node/          # UI-компоненты (Trigger, Code, Answer) по тегам
├── handler/       # Виджеты-оркестраторы, собирающие компоненты
├── webhook/       # Обработчики webhook от внешних сервисов
├── core/          # Основные настройки и конфигурация
├── data/          # Файлы и буферы для работы
├── callback/      # Обработчики колбеков, организованные по тегам
├── state/         # Состояния FSM, организованные по тегам
└── service/       # API-клиенты к бэкенд-сервисам
```

### 🏷️ Система тегов

Ключевая концепция архитектуры - **теги**. Они объединяют связанные компоненты в логические группы:

- **Тег** - это название функциональной области (например, `onboarding`, `payment`, `analytics`)
- Компоненты с одинаковым тегом группируются в один модуль
- Это упрощает навигацию и поддержку кода

Допускается **вложенная структура внутри тега** (в `handler/`) для группировки виджетов по подсекциям/сценариям. При документировании виджетов указывайте полный путь к файлам.

### 📋 Пример структуры по тегам

```python
# Тег: onboarding
callback/onboarding.py      # SetCompanyNameCallback, SetCompanyDescriptionCallback
state/onboarding.py         # wait_company_name, wait_company_description

# Тег: payment  
callback/payment.py         # ProcessPaymentCallback, RefundCallback
state/payment.py           # wait_payment_data, processing_payment
```

## 📚 Документация по пакетам

| Пакет | Описание | Документация |
|-------|----------|--------------|
| **node** | UI-компоненты (Trigger, Code, Answer) по тегам | [📖 node.md](node.md) |
| **handler** | Виджеты-оркестраторы, собирающие компоненты из node | [📖 handler.md](handler.md) |
| **webhook** | Обработчики webhook от внешних сервисов | [📖 webhook.md](webhook.md) |
| **core** | Основные настройки, конфигурация, словари | [📖 core.md](core.md) |
| **data** | Файлы и буферы для работы приложения | [📖 data.md](data.md) |
| **callback** | Обработчики колбеков, организованные по тегам | [📖 callback.md](callback.md) |
| **state** | Состояния FSM, организованные по тегам | [📖 state.md](state.md) |
| **service** | API-клиенты к бэкенд-сервисам | [📖 service.md](service.md) |

## 📐 Трассируемость и тестирование

| Документ | Описание |
|----------|----------|
| [📖 BRD Template.md](BRD%20Template.md) | Формат PRD: JSON-схема, описание полей, пример |
| [📖 traceability.md](traceability.md) | Связь PRD → код → тесты, конвенции ID |
| [📖 tests.md](tests.md) | Конвенции тестирования: структура, нейминг, генерация из BDD |

## 🚀 Быстрый старт

### 1. Добавление нового функционала

1. **Проверьте PRD** — убедитесь, что фича и сценарии описаны в `prd.json` (Feature ID, Scenario ID, BDD)
2. **Определите тег** для вашего функционала (например, `notes`)
3. **Создайте компоненты в node:**
   - `node/{tag}/trigger/{action}_trigger.py` — визуальные операции
   - `node/{tag}/code/{action}_code.py` — бизнес-логика
   - `node/{tag}/answer/{state}_answer.py` — отрисовка экранов
   - В docstring каждого компонента укажите Feature ID и Scenario ID
4. **Создайте виджет-оркестратор** в `handler/v1/user/{tag}/{Feature ID}/{widget}_widget.py`
5. **Создайте состояния** в `state/{tag}.py` (если нужны новые)
6. **Создайте колбеки** в `callback/{tag}.py` (если нужны новые)
7. **Добавьте API-клиент** в `service/{service_name}_api/` (если фича работает с бэкендом)
8. **Создайте тесты** в `tests/{Feature ID}_{name}/test_{Scenario ID}_{name}.py`

### 2. Пример: добавление команды /start (Feature F001)

```bash
# 1. Создаем компоненты в node/
mkdir -p node/control/trigger node/control/code node/control/answer
touch node/control/trigger/start_command_trigger.py
touch node/control/code/start_command_code.py
touch node/control/answer/new_user_answer.py
touch node/control/answer/vacancy_list_answer.py

# 2. Создаем виджет-оркестратор в handler/ (директория = Feature ID)
mkdir -p handler/v1/user/control/F001
touch handler/v1/user/control/F001/start_command_widget.py

# 3. Виджет импортирует и связывает компоненты из node/

# 4. Создаем тесты
mkdir -p tests/F001_control
touch tests/F001_control/test_SC001_new_user_welcome.py
touch tests/F001_control/test_SC002_existing_user_dashboard.py
```

## 📖 Соглашения и стандарты

### 🎯 Именование

| Компонент | Шаблон именования | Пример |
|-----------|-------------------|---------|
| **Node Trigger** | `{action}_trigger.py` → `{Action}Trigger` | `start_command_trigger.py` → `StartCommandTrigger` |
| **Node Code** | `{action}_code.py` → `{Action}Code` | `start_command_code.py` → `StartCommandCode` |
| **Node Answer** | `{state}_answer.py` → `{State}Answer` | `vacancy_list_answer.py` → `VacancyListAnswer` |
| **Виджеты** | `{name}_widget.py` | `start_command_widget.py` |
| **Модули тегов** | `{tag_name}.py` | `onboarding.py` |
| **Классы колбеков** | `{Name}Callback` | `SetCompanyNameCallback` |
| **Переменные состояний** | `{snake_case}` | `wait_company_name` |
| **Пакеты API-клиентов** | `{service_name}_api` | `notes_api`, `auth_api`, `payment_api` |

### 📝 Документация

**Обязательные элементы документации:**

- **Модули:** Описание назначения и содержимого
- **Классы:** Назначение, поля, примеры использования
- **Состояния:** Когда используется, в каких виджетах
- **Методы:** Параметры, возвращаемые значения, примеры

Добавляйте в docstring виджета человекочитаемый блок связей:

```
Доступен из:
1. widget_name (+ путь до него)
   - Из какого state (+ путь до него)
   - Из какого answer (+ путь до него)

Переводит в:
1. widget_name (+ путь до него)
   - В каком state (+ путь до него)
   - Из какого answer (+ путь до него)
```

Это повышает наглядность и помогает быстрее ориентироваться в графе переходов.

### ✅ Чек-листы

В каждом файле документации пакета есть подробный чек-лист для добавления новых элементов.


---


