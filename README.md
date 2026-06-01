# Selfpost

Selfpost — Telegram-бот для автоматизации контент-плана канала. Он подключается к каналу, по расписанию генерирует черновик поста через Gemini и присылает его администратору в личные сообщения. Администратор может опубликовать текст сразу, добавить изображение или пропустить черновик.

## Возможности

- подключение нескольких Telegram-каналов;
- проверка, что бот добавлен в канал администратором;
- генерация постов под заданную тему канала;
- ручной запуск генерации в любой момент;
- настройка интервала автогенерации для каждого канала;
- черновики с подтверждением перед публикацией;
- добавление изображения к черновику;
- локальное хранение настроек каналов и ожидающих публикаций.

## Стек

- Python 3.11+;
- aiogram 3;
- Google Gemini API;
- python-dotenv.

## Быстрый старт

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

## Как пользоваться

1. Создайте Telegram-бота через BotFather и добавьте токен в `.env`.
2. Получите ключ Gemini API и добавьте его в `.env`.
3. Добавьте бота администратором в нужный канал.
4. Напишите боту `/start`.
5. Подключите канал по `@username` или `chat_id`.
6. Задайте тему и интервал генерации.

## Безопасность

Секреты не должны храниться в репозитории. Используйте `.env`, а файл `.env.example` оставляйте только как шаблон. Если токен Telegram или Gemini когда-либо попал в публичный репозиторий, его нужно перевыпустить.

## Статус проекта

Проект подходит для портфолио как пример Telegram-бота с асинхронной логикой, FSM-сценариями, интеграцией LLM и простым планировщиком публикаций.
=======
RU:
Selfpost - бот в телеграм, который ведет за вас тг канал.
Он подключается в тг канал и напоминает вам раз в определенное время опубликовать пост.Бот сам генерирует пост на заданную тему канала и присылает вам в ЛС.В черновик можно добавить фото, а также администратор решает публиковать пост или нет(бот сам опубликует пост, администратору надо нажать всего 1 кнопку). Это облегчает ведение тг канала, позволяя делать посты за 1 минуту и строго по графику.
В боте использованы api aiogram 3.0 для написания тг бота, api gemini.
-----------------------------------
ENG:
Selfpost is a Telegram bot that manages your Telegram channel for you.
It connects to your Telegram channel and reminds you to publish a post at a specific time. The bot automatically generates a post on a given channel topic and sends it to you via private messages. You can add a photo to the draft, and the administrator decides whether to publish the post (the bot will publish the post automatically; the administrator only needs to click one button). This simplifies managing your Telegram channel, allowing you to post in as little as one minute and strictly according to the schedule.
The bot uses the Aiogram 3.0 API for writing the Telegram bot and the Gemini API.
