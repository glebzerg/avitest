# Avito QA Internship Assignment

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-8.3+-green.svg)](https://pytest.org/)
[![Allure](https://img.shields.io/badge/Allure-2.13+-yellow.svg)](https://docs.qameta.io/allure/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Решение тестового задания на стажировку QA в Авито (весенняя волна 2026).

## Структура проекта

```
avito-qa-assignment/
├── tests/
│   ├── api/                    # API тесты
│   │   ├── test_create_item.py
│   │   ├── test_get_item.py
│   │   ├── test_get_seller_items.py
│   │   ├── test_get_statistics.py
│   │   └── test_delete_item.py
│   ├── e2e/                    # E2E тесты
│   │   ├── test_item_lifecycle.py
│   │   └── test_edge_cases.py
│   └── conftest.py             # Pytest fixtures
├── utils/
│   ├── api_client.py           # API клиент
│   ├── data_generator.py       # Генератор тестовых данных
│   └── assertions.py           # Кастомные ассерты
├── allure-results/             # Результаты Allure
├── BUGS.md                     # Баг-репорты
├── TESTCASES.md               # Тест-кейсы
├── pytest.ini                 # Конфигурация pytest
├── pyproject.toml             # Конфигурация black/isort
├── .flake8                    # Конфигурация flake8
├── requirements.txt           # Зависимости
└── README.md                  # Этот файл
```

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/avito-qa-assignment.git
cd avito-qa-assignment
```

### 2. Создание виртуального окружения

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

## Запуск тестов

### Базовый запуск всех тестов

```bash
pytest
```

### Запуск с подробным выводом

```bash
pytest -v
```

### Запуск только API тестов

```bash
pytest -m api
```

### Запуск только E2E тестов

```bash
pytest -m e2e
```

### Запуск позитивных тестов

```bash
pytest -m positive
```

### Запуск негативных тестов

```bash
pytest -m negative
```

### Запуск конкретного тестового файла

```bash
pytest tests/api/test_create_item.py
```

### Запуск с генерацией Allure отчёта

```bash
pytest --alluredir=allure-results
```

### Просмотр Allure отчёта

```bash
# Установка Allure CLI (если не установлен)
# macOS
brew install allure

# Linux
sudo apt-get install allure

# Windows (через scoop)
scoop install allure

# Генерация и открытие отчёта
allure serve allure-results
```

## Линтинг и форматирование

### Проверка кода flake8

```bash
flake8
```

### Автоматическое форматирование black

```bash
black .
```

### Сортировка импортов isort

```bash
isort .
```

### Проверка типов mypy

```bash
mypy .
```

### Запуск всех проверок

```bash
flake8 && black --check . && isort --check . && mypy .
```

## API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/1/item` | Создать объявление |
| GET | `/api/1/item/{id}` | Получить объявление по ID |
| GET | `/api/1/{sellerID}/item` | Получить все объявления продавца |
| GET | `/api/1/statistic/{id}` | Получить статистику по объявлению |
| DELETE | `/api/2/item/{id}` | Удалить объявление |

**Base URL:** `https://qa-internship.avito.com`

## Покрытие тестами

| Категория | Количество |
|-----------|------------|
| Позитивные тесты | 35 |
| Негативные тесты | 26 |
| E2E тесты | 10 |
| **Всего** | **71** |

## Дополнительные задания

### ✅ E2E тестирование

Реализованы сценарии:
- Полный жизненный цикл объявления
- Работа с несколькими объявлениями
- Идемпотентность операций
- Сценарии с несколькими продавцами

### ✅ Allure отчёты

- Интеграция с pytest-allure
- Шаги тестов (@allure.step)
- Описания тестов (@allure.title, @allure.description)
- Маркировка тестов (@allure.feature, @allure.story)

### ✅ Линтер и форматтер

- **Black** — автоматическое форматирование
- **flake8** — проверка стиля кода
- **isort** — сортировка импортов
- **mypy** — статический анализ типов

## Документация

- [TESTCASES.md](TESTCASES.md) — Полный набор тест-кейсов
- [BUGS.md](BUGS.md) — Баг-репорты

## Технологии

- **Python 3.11+** — язык программирования
- **pytest** — фреймворк для тестирования
- **requests** — HTTP клиент
- **pydantic** — валидация данных
- **Allure** — генерация отчётов
- **black/flake8/isort/mypy** — линтинг и форматирование

## Автор

**Глеб Писарев**  
QA-инженер  
- Email: glebzergeevidge@yandex.ru  
- Telegram: @glebzerg  
- GitHub: @glebzergeevidge

## Лицензия

MIT License
