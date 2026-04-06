# Habit Tracker Bot

<img src="https://img.shields.io/badge/python-3.10+-blue.svg"> <img src="https://img.shields.io/badge/aiogram-3.x-green.svg"> <img src="https://img.shields.io/badge/FastAPI-0.100+-orange.svg"> <img src="https://img.shields.io/badge/database-sqlite-yellow.svg"> <img src="https://img.shields.io/badge/API-REST-red.svg">

Telegram бот для отслеживания привычек с визуализацией прогресса. Помогает формировать полезные привычки и отслеживать их выполнение день за днём.


## Возможности

### Telegram Бот
| Функция | Описание |
|---------|----------|
| **Добавление привычек** | Создайте список привычек, которые хотите отслеживать |
| **Отметка выполнения** | Ежедневно отмечайте выполненные привычки одним нажатием |
| **Статистика за неделю** | Просматривайте процент выполнения по каждой привычке |
| **Прогресс-бар** | Визуальное отображение прогресса в виде шкалы |
| **Защита от дублей** | Нельзя отметить одну привычку дважды в день |

### REST API
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| **GET** | `/stats/{telegram_id}` | Получить статистику пользователя за неделю |
| **POST** | `/habits` | Добавить новую привычку через JSON |
| **Аутентификация** | Bearer Token | Защита API с помощью токена |

## Технологический стек

- **Python 3.10+** - основной язык программирования
- **Aiogram 3.x** - современный фреймворк для Telegram ботов
- **FastAPI** - высокопроизводительный фреймворк для REST API
- **aiosqlite** - асинхронная работа с SQLite
- **asyncio** - асинхронное программирование
- **Uvicorn** - ASGI сервер для запуска API

## Структура проекта
```
Habit_Tracker_With_DB_Bot/
├── main.py # Telegram бот (aiogram)
├── api.py # REST API (FastAPI)
├── database.py # Работа с базой данных
├── run.py # Совместный запуск бота и API
├── habits.db # SQLite база данных (создаётся автоматически)
└── README.md # Документация проекта
```

## Безопасность

- **API защищен Bearer токеном**
- **Токен бота хранится в коде (рекомендуется вынести в .env для production)**
- **База данных изолирована и не требует внешних подключений**

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начало работы, автоматическая регистрация пользователя |
| `/menu` | Открыть главное меню с доступными действиями |


## Схема базы данных

Проект использует SQLite с тремя связанными таблицами:

### users
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY | Уникальный идентификатор |
| telegram_id | INTEGER UNIQUE | ID пользователя в Telegram |
| username | TEXT | Имя пользователя (опционально) |

### habits
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY | Уникальный идентификатор привычки |
| user_id | INTEGER | Внешний ключ к users.id |
| name | TEXT | Название привычки |
| created_date | DATE | Дата создания |

### habits_completions
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY | Уникальный идентификатор отметки |
| habit_id | INTEGER | Внешний ключ к habits.id |
| completion_date | DATE | Дата выполнения |

## Быстрый старт

### Предварительные требования

- Python 3.10 или выше
- Telegram аккаунт
- Токен бота (получить у [@BotFather](https://t.me/botfather))

### Установка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/KILVARiys/Habit_Tracker_With_DB_Bot.git
cd Habit_Tracker_With_DB_Bot
```
2. **Установите зависимости**
```bash
pip install aiogram aiosqlite fastapi uvicorn
```
3. **Настройте токен бота**
Откройте main.py и замените  на ваш токен:
```
TOKEN = 'YOUR_BOT_TOKEN_HERE'
```
4. **Настройте API токен (опционально)**
В файле api.py измените токен для API:
```
API_TOKEN = "your_secret_api_token_here"
```

## Запуск

### Вариант 1: Раздельный запуск (рекомендуется для разработки)
**Терминал 1 - Запуск Telegram бота:**
```bash
python main.py
```
**Терминал 2 - Запуск REST API:**
```bash
uvicorn api:app --reload --port 8000
```

### Вариант 2: Совместный запуск
```bash
python run.py
```

## Интерактивная документация API
**FastAPI автоматически генерирует документацию:**

- **Swagger UI: http://localhost:8000/docs**
- **ReDoc: http://localhost:8000/redoc**
