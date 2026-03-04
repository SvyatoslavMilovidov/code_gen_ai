# Правила нейминга

[← Назад к оглавлению](README.md)

---

## Файлы

| Раздел | Суффикс файла | Пример |
|--------|---------------|--------|
| model | `_model.py` | `candidate_model.py` |
| schema | `_schema.py` | `candidate_schema.py` |
| repository | `_repository.py` | `candidate_repository.py` |
| service | `_service.py` | `candidate_service.py` |
| provider | `_provider.py` | `linkedin_provider.py` |
| api endpoint | по HTTP методу | `get.py`, `post.py`, `put.py`, `delete.py` |

## Классы

| Раздел | Суффикс класса | Пример |
|--------|----------------|--------|
| model | `Model` | `CandidateModel` |
| schema | по назначению | `CandidateCreateSchema`, `CandidateResponseSchema` |
| repository | `Repository` | `CandidateRepository` |
| service | `Service` | `CandidateService` |
| provider | `Provider` | `LinkedInProvider` |
| enum | `Enum` | `CandidateStatusEnum` |

## Схемы (суффиксы классов)

| Назначение | Суффикс | Пример | HTTP |
|------------|---------|--------|------|
| Базовая | `Base` | `CandidateBaseSchema` | — |
| Создание | `Create` | `CandidateCreateSchema` | POST |
| Обновление | `Update` | `CandidateUpdateSchema` | PUT/PATCH |
| Ответ API | `Response` | `CandidateResponseSchema` | все |
| Фильтрация | `Filter` | `CandidateFilterSchema` | GET (query) |

## Группы (подпапки)

Имя папки = имя главной сущности в **нижнем регистре**:

```
model/
  candidate/     # Всё связанное с кандидатами
  search/        # Всё связанное с поиском
  
service/
  candidate/
  search/
  providers/     # Внешние провайдеры
```

## Примеры

### Полный путь для сущности Candidate

| Слой | Файл | Класс |
|------|------|-------|
| model | `model/candidate/candidate_model.py` | `CandidateModel` |
| schema | `schema/candidate/candidate_schema.py` | `CandidateCreateSchema`, `CandidateResponseSchema` |
| repository | `repository/candidate/candidate_repository.py` | `CandidateRepository` |
| service | `service/candidate/candidate_service.py` | `CandidateService` |
| api | `api/v1/endpoints/candidate/get.py` | функции `get_candidates`, `get_candidate` |

### Связанные сущности

Если `CandidateEvaluation` связана с `Candidate`:

```
model/candidate/
  candidate_model.py      # CandidateModel
  evaluation_model.py     # CandidateEvaluationModel (или EvaluationModel)

repository/candidate/
  candidate_repository.py
  evaluation_repository.py
```

## Соглашения

### 1. snake_case для файлов и папок

```
✅ candidate_service.py
❌ CandidateService.py
❌ candidateService.py
```

### 2. PascalCase для классов

```python
✅ class CandidateService:
❌ class candidate_service:
❌ class candidateService:
```

### 3. Явные суффиксы

Суффикс в имени файла **И** в имени класса:

```python
# candidate_model.py
class CandidateModel:  # ✅ Суффикс Model
    pass

# candidate_repository.py
class CandidateRepository:  # ✅ Суффикс Repository
    pass
```

### 4. Множественное число для коллекций в API

```
/api/v1/candidates      # ✅ множественное
/api/v1/candidate       # ❌ единственное
```

---

[Далее: Правила документирования →](04-documentation.md)
