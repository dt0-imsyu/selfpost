# Selfpost

**Selfpost** is a Telegram bot that helps channel owners keep a steady posting rhythm. It generates post drafts with Gemini, sends them to the admin for review, and publishes only after manual approval.

**Selfpost** - Telegram-бот для ведения канала по расписанию. Он генерирует черновики постов через Gemini, присылает их администратору в личные сообщения и публикует только после подтверждения.

---

## Русская версия

### Что умеет бот

- подключает один или несколько Telegram-каналов;
- проверяет, что бот добавлен в канал администратором;
- хранит тему и интервал публикаций для каждого канала;
- по расписанию генерирует черновик поста через Gemini;
- позволяет сгенерировать пост вручную в любой момент;
- отправляет черновик администратору в личку;
- дает выбор: опубликовать, добавить изображение или пропустить;
- публикует пост в канал только после подтверждения.

### Зачем это нужно

Selfpost закрывает простую, но частую проблему: канал нужно вести регулярно, а идеи и время есть не всегда. Бот не публикует контент самовольно, а работает как ассистент: готовит черновик, напоминает о публикации и оставляет финальное решение за человеком.

Проект показывает работу с асинхронным Telegram-ботом, FSM-сценариями, интеграцией LLM, простым планировщиком задач и хранением состояния без отдельной базы данных.

### Стек

- Python 3.11+
- aiogram 3
- Google Gemini API
- python-dotenv
- JSON-файл для локального хранения данных

### Быстрый старт

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Заполните `.env`:

```env
BOT_TOKEN=telegram-bot-token
GEMINI_API_KEY=gemini-api-key
GEMINI_MODEL=gemini-2.5-flash-lite
SELFPOST_DATA_FILE=bot_data.json
```

Запустите бота:

```bash
python selfpost/main.py
```

### Как пользоваться

1. Создайте Telegram-бота через BotFather.
2. Получите ключ Gemini API.
3. Добавьте оба ключа в `.env`.
4. Добавьте бота администратором в Telegram-канал.
5. Напишите боту `/start`.
6. Подключите канал по `@username` или `chat_id`.
7. Укажите тему канала и интервал генерации.

### Безопасность

Секреты не должны лежать в коде или попадать в Git. Для токенов используется `.env`, а `.env.example` служит только шаблоном. Если реальный Telegram-токен или Gemini API key когда-либо был опубликован, его нужно перевыпустить.

---

## English Version

### Features

- connects one or multiple Telegram channels;
- checks that the bot has admin rights in the channel;
- stores a topic and posting interval for each channel;
- generates scheduled post drafts with Gemini;
- supports manual post generation on demand;
- sends each draft to the admin in private messages;
- lets the admin publish, attach an image, or skip the draft;
- publishes only after explicit admin approval.

### Why This Project Exists

Selfpost solves a practical content workflow problem: Telegram channels need consistent posting, but writing ideas from scratch every day is time-consuming. The bot acts as an assistant, not an autopublisher. It prepares a draft, reminds the admin, and keeps the final decision human.

As a portfolio project, it demonstrates an async Telegram bot, aiogram FSM flows, LLM integration, lightweight scheduling, and local JSON-based persistence.

### Tech Stack

- Python 3.11+
- aiogram 3
- Google Gemini API
- python-dotenv
- JSON-based local storage

### Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Fill in `.env`:

```env
BOT_TOKEN=telegram-bot-token
GEMINI_API_KEY=gemini-api-key
GEMINI_MODEL=gemini-2.5-flash-lite
SELFPOST_DATA_FILE=bot_data.json
```

Run the bot:

```bash
python selfpost/main.py
```

### Usage

1. Create a Telegram bot with BotFather.
2. Create a Gemini API key.
3. Put both secrets into `.env`.
4. Add the bot as an admin to your Telegram channel.
5. Send `/start` to the bot.
6. Connect the channel using `@username` or `chat_id`.
7. Set the channel topic and generation interval.

### Security

Secrets must not be stored in code or committed to Git. Runtime credentials are loaded from `.env`, while `.env.example` is only a template. If a real Telegram token or Gemini API key was ever published, rotate it immediately.
