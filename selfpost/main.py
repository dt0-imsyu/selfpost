import asyncio
import json
import os
import time
import uuid
from typing import Any, Dict, Optional

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from apikeys import botkey
from geminiapp import aireq

DATA_FILE = "bot_data.json"


class BotStates(StatesGroup):
    wait_channel = State()
    wait_topic = State()
    wait_interval = State()
    wait_test_topic = State()
    wait_image = State()


bot = Bot(token=botkey)
dp = Dispatcher()
scheduler_task: Optional[asyncio.Task] = None


def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return {"users": {}}
    if "users" not in data:
        data["users"] = {}
    return data


def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def get_or_create_user_data(data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    user_key = str(user_id)
    if user_key not in data["users"]:
        data["users"][user_key] = {"channels": [], "pending_posts": {}}
    return data["users"][user_key]


def build_main_menu() -> types.InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        types.InlineKeyboardButton(text="подключенные каналы", callback_data="podkl")
    )
    b.row(
        types.InlineKeyboardButton(text="новости бота", url="https://t.me/deliverystatus_update")
    )
    return b.as_markup()


def build_channels_menu(user_id: int) -> types.InlineKeyboardMarkup:
    data = load_data()
    user_data = get_or_create_user_data(data, user_id)
    b = InlineKeyboardBuilder()
    channels = user_data.get("channels", [])
    for channel in channels:
        status = "ON" if channel.get("enabled", True) else "OFF"
        b.row(
            types.InlineKeyboardButton(
                text=f"{channel['title']} ({status})",
                callback_data=f"ch_manage:{channel['chat_id']}",
            )
        )
    b.row(types.InlineKeyboardButton(text="➕ Подключить канал", callback_data="ch_add"))
    b.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main"))
    return b.as_markup()


def build_channel_manage_menu(chat_id: int, enabled: bool) -> types.InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="✏️ Изменить тему", callback_data=f"ch_topic:{chat_id}"))
    b.row(types.InlineKeyboardButton(text="⏱ Изменить интервал", callback_data=f"ch_interval:{chat_id}"))
    toggle_text = "⏸ Остановить автопостинг" if enabled else "▶️ Запустить автопостинг"
    b.row(types.InlineKeyboardButton(text=toggle_text, callback_data=f"ch_toggle:{chat_id}"))
    b.row(types.InlineKeyboardButton(text="🚀 Сгенерировать сейчас", callback_data=f"ch_generate:{chat_id}"))
    b.row(types.InlineKeyboardButton(text="🗑 Удалить канал", callback_data=f"ch_delete:{chat_id}"))
    b.row(types.InlineKeyboardButton(text="⬅️ К каналам", callback_data="podkl"))
    return b.as_markup()


def find_channel(user_data: Dict[str, Any], chat_id: int) -> Optional[Dict[str, Any]]:
    for channel in user_data.get("channels", []):
        if channel["chat_id"] == chat_id:
            return channel
    return None


async def generate_post_text(topic: str) -> str:
    prompt = (
        "Ты контент-редактор Telegram-канала. Напиши один готовый пост на русском языке. "
        "Пиши понятно и живо, без хештегов-спама и лишней воды. "
        f"Тема поста: {topic}"
    )
    return await asyncio.to_thread(aireq, prompt)


async def send_draft_to_admin(user_id: int, channel: Dict[str, Any], generated_text: str) -> None:
    data = load_data()
    user_data = get_or_create_user_data(data, user_id)
    pending_posts = user_data.setdefault("pending_posts", {})
    draft_id = str(uuid.uuid4())[:8]
    pending_posts[draft_id] = {
        "channel_id": channel["chat_id"],
        "channel_title": channel["title"],
        "text": generated_text,
        "image_file_id": None,
        "created_at": int(time.time()),
    }
    save_data(data)

    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"draft_publish:{draft_id}"))
    b.row(types.InlineKeyboardButton(text="🖼 Добавить картинку", callback_data=f"draft_image:{draft_id}"))
    b.row(types.InlineKeyboardButton(text="❌ Пропустить", callback_data=f"draft_skip:{draft_id}"))

    text = (
        f"Готов черновик для канала: {channel['title']}\n\n"
        f"{generated_text}\n\n"
        "Выберите действие:"
    )
    await bot.send_message(chat_id=user_id, text=text, reply_markup=b.as_markup())


async def generate_and_notify(user_id: int, chat_id: int) -> None:
    data = load_data()
    user_data = get_or_create_user_data(data, user_id)
    channel = find_channel(user_data, chat_id)
    if not channel:
        return
    topic = channel.get("topic", "новости и полезные советы")
    try:
        generated_text = await generate_post_text(topic)
    except Exception as err:
        await bot.send_message(user_id, f"Ошибка генерации поста для {channel['title']}: {err}")
        return
    await send_draft_to_admin(user_id, channel, generated_text)


async def scheduler_loop() -> None:
    while True:
        data = load_data()
        now = int(time.time())
        users = data.get("users", {})
        changed = False

        for user_key, user_data in users.items():
            user_id = int(user_key)
            channels = user_data.get("channels", [])
            for channel in channels:
                if not channel.get("enabled", True):
                    continue
                next_run = int(channel.get("next_run", 0))
                if now < next_run:
                    continue
                interval_min = int(channel.get("interval_minutes", 120))
                channel["next_run"] = now + interval_min * 60
                changed = True
                asyncio.create_task(generate_and_notify(user_id, channel["chat_id"]))

        if changed:
            save_data(data)
        await asyncio.sleep(30)


@dp.message(Command("start"))
async def start_handler(message: types.Message) -> None:
    data = load_data()
    get_or_create_user_data(data, message.from_user.id)
    save_data(data)
    await message.answer(
        "Здравствуйте! Я помогу автоматизировать постинг в каналы.\n"
        "Выберите раздел:",
        reply_markup=build_main_menu(),
    )


@dp.callback_query(F.data == "back_main")
async def back_main_handler(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text("Главное меню:", reply_markup=build_main_menu())
    await callback.answer()





@dp.callback_query(F.data == "podkl")
async def channels_handler(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(
        "Управление каналами. Выберите канал или подключите новый:",
        reply_markup=build_channels_menu(callback.from_user.id),
    )
    await callback.answer()


@dp.callback_query(F.data == "ch_add")
async def add_channel_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(
        "Отправьте @username канала или его chat_id (например, -1001234567890).\n"
        "Важно: бот должен быть добавлен в канал администратором."
    )
    await state.set_state(BotStates.wait_channel)
    await callback.answer()


@dp.message(BotStates.wait_channel)
async def get_channel_handler(message: types.Message, state: FSMContext) -> None:
    raw_channel = message.text.strip()
    chat_ref: Any = raw_channel
    if raw_channel.startswith("-100") and raw_channel[1:].isdigit():
        chat_ref = int(raw_channel)
    try:
        chat = await bot.get_chat(chat_ref)
    except Exception:
        await message.answer("Не удалось найти канал. Проверьте username/chat_id и попробуйте снова.")
        return

    me = await bot.get_me()
    try:
        member = await bot.get_chat_member(chat.id, me.id)
    except Exception:
        await message.answer("Не могу проверить права в канале. Добавьте бота в админы и повторите.")
        return
    if member.status not in {"administrator", "creator"}:
        await message.answer("Бот не администратор этого канала. Выдайте права и повторите подключение.")
        return

    data = load_data()
    user_data = get_or_create_user_data(data, message.from_user.id)
    if find_channel(user_data, chat.id):
        await message.answer("Этот канал уже подключен.")
        await state.clear()
        return

    user_data["channels"].append(
        {
            "chat_id": chat.id,
            "title": chat.title or str(chat.id),
            "topic": "новости и полезные советы",
            "interval_minutes": 120,
            "next_run": int(time.time()) + 300,
            "enabled": True,
        }
    )
    save_data(data)
    await state.clear()
    await message.answer(
        f"Канал `{chat.title or chat.id}` подключен.\n"
        "Текущая тема: новости и полезные советы\n"
        "Интервал: 120 минут",
        parse_mode="Markdown",
    )
    await message.answer("Список каналов:", reply_markup=build_channels_menu(message.from_user.id))


@dp.callback_query(F.data.startswith("ch_manage:"))
async def manage_channel_handler(callback: types.CallbackQuery) -> None:
    chat_id = int(callback.data.split(":")[1])
    data = load_data()
    user_data = get_or_create_user_data(data, callback.from_user.id)
    channel = find_channel(user_data, chat_id)
    if not channel:
        await callback.answer("Канал не найден.", show_alert=True)
        return
    info = (
        f"Канал: {channel['title']}\n"
        f"Тема: {channel['topic']}\n"
        f"Интервал: {channel['interval_minutes']} мин\n"
        f"Статус: {'включен' if channel.get('enabled', True) else 'выключен'}"
    )
    await callback.message.edit_text(
        info,
        reply_markup=build_channel_manage_menu(chat_id, channel.get("enabled", True)),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("ch_topic:"))
async def channel_topic_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    chat_id = int(callback.data.split(":")[1])
    await state.update_data(edit_chat_id=chat_id)
    await state.set_state(BotStates.wait_topic)
    await callback.message.answer("Введите новую тему для генерации постов:")
    await callback.answer()


@dp.message(BotStates.wait_topic)
async def set_topic_handler(message: types.Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    chat_id = state_data.get("edit_chat_id")
    if not chat_id:
        await message.answer("Не удалось определить канал. Повторите через меню.")
        await state.clear()
        return
    data = load_data()
    user_data = get_or_create_user_data(data, message.from_user.id)
    channel = find_channel(user_data, int(chat_id))
    if not channel:
        await message.answer("Канал не найден.")
        await state.clear()
        return
    channel["topic"] = message.text.strip()
    save_data(data)
    await message.answer(f"Тема обновлена: {channel['topic']}")
    await state.clear()


@dp.callback_query(F.data.startswith("ch_interval:"))
async def channel_interval_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    chat_id = int(callback.data.split(":")[1])
    await state.update_data(edit_chat_id=chat_id)
    await state.set_state(BotStates.wait_interval)
    await callback.message.answer("Введите интервал в минутах (например, 180):")
    await callback.answer()


@dp.message(BotStates.wait_interval)
async def set_interval_handler(message: types.Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    chat_id = state_data.get("edit_chat_id")
    if not chat_id:
        await message.answer("Не удалось определить канал. Повторите через меню.")
        await state.clear()
        return
    try:
        interval = int(message.text.strip())
        if interval < 5:
            raise ValueError
    except ValueError:
        await message.answer("Введите целое число не меньше 5.")
        return
    data = load_data()
    user_data = get_or_create_user_data(data, message.from_user.id)
    channel = find_channel(user_data, int(chat_id))
    if not channel:
        await message.answer("Канал не найден.")
        await state.clear()
        return
    channel["interval_minutes"] = interval
    channel["next_run"] = int(time.time()) + interval * 60
    save_data(data)
    await message.answer(f"Интервал обновлен: {interval} минут.")
    await state.clear()


@dp.callback_query(F.data.startswith("ch_toggle:"))
async def channel_toggle_handler(callback: types.CallbackQuery) -> None:
    chat_id = int(callback.data.split(":")[1])
    data = load_data()
    user_data = get_or_create_user_data(data, callback.from_user.id)
    channel = find_channel(user_data, chat_id)
    if not channel:
        await callback.answer("Канал не найден.", show_alert=True)
        return
    channel["enabled"] = not channel.get("enabled", True)
    if channel["enabled"]:
        channel["next_run"] = int(time.time()) + channel.get("interval_minutes", 120) * 60
    save_data(data)
    await callback.answer("Статус обновлен.")
    await manage_channel_handler(callback)


@dp.callback_query(F.data.startswith("ch_generate:"))
async def channel_generate_now_handler(callback: types.CallbackQuery) -> None:
    chat_id = int(callback.data.split(":")[1])
    await callback.answer("Генерирую пост...")
    await generate_and_notify(callback.from_user.id, chat_id)


@dp.callback_query(F.data.startswith("ch_delete:"))
async def channel_delete_handler(callback: types.CallbackQuery) -> None:
    chat_id = int(callback.data.split(":")[1])
    data = load_data()
    user_data = get_or_create_user_data(data, callback.from_user.id)
    before = len(user_data.get("channels", []))
    user_data["channels"] = [c for c in user_data.get("channels", []) if c["chat_id"] != chat_id]
    after = len(user_data["channels"])
    save_data(data)
    if before == after:
        await callback.answer("Канал не найден.", show_alert=True)
        return
    await callback.message.edit_text(
        "Канал удален. Список подключений:",
        reply_markup=build_channels_menu(callback.from_user.id),
    )
    await callback.answer()




@dp.callback_query(F.data == "resp1")
async def test_request_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("Введите тему для генерации тестового поста")
    await state.set_state(BotStates.wait_test_topic)
    await callback.answer()


@dp.message(BotStates.wait_test_topic)
async def test_topic_handler(message: types.Message, state: FSMContext) -> None:
    generated = await generate_post_text(message.text)
    await message.reply(generated)
    await state.clear()


@dp.callback_query(F.data.startswith("draft_publish:"))
async def draft_publish_handler(callback: types.CallbackQuery) -> None:
    draft_id = callback.data.split(":")[1]
    data = load_data()
    user_data = get_or_create_user_data(data, callback.from_user.id)
    draft = user_data.get("pending_posts", {}).get(draft_id)
    if not draft:
        await callback.answer("Черновик не найден.", show_alert=True)
        return
    try:
        if draft.get("image_file_id"):
            await bot.send_photo(
                chat_id=draft["channel_id"],
                photo=draft["image_file_id"],
                caption=draft["text"],
            )
        else:
            await bot.send_message(chat_id=draft["channel_id"], text=draft["text"])
    except Exception as err:
        await callback.answer(f"Ошибка публикации: {err}", show_alert=True)
        return
    del user_data["pending_posts"][draft_id]
    save_data(data)
    await callback.message.edit_text("Пост опубликован ✅")
    await callback.answer()


@dp.callback_query(F.data.startswith("draft_skip:"))
async def draft_skip_handler(callback: types.CallbackQuery) -> None:
    draft_id = callback.data.split(":")[1]
    data = load_data()
    user_data = get_or_create_user_data(data, callback.from_user.id)
    if draft_id in user_data.get("pending_posts", {}):
        del user_data["pending_posts"][draft_id]
        save_data(data)
    await callback.message.edit_text("Черновик пропущен ❌")
    await callback.answer()


@dp.callback_query(F.data.startswith("draft_image:"))
async def draft_image_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    draft_id = callback.data.split(":")[1]
    data = load_data()
    user_data = get_or_create_user_data(data, callback.from_user.id)
    if draft_id not in user_data.get("pending_posts", {}):
        await callback.answer("Черновик не найден.", show_alert=True)
        return
    await state.update_data(image_draft_id=draft_id)
    await state.set_state(BotStates.wait_image)
    await callback.message.answer("Пришлите картинку одним сообщением.")
    await callback.answer()


@dp.message(BotStates.wait_image)
async def image_upload_handler(message: types.Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer("Нужно отправить именно изображение.")
        return
    state_data = await state.get_data()
    draft_id = state_data.get("image_draft_id")
    if not draft_id:
        await message.answer("Черновик не найден. Повторите действие.")
        await state.clear()
        return
    data = load_data()
    user_data = get_or_create_user_data(data, message.from_user.id)
    draft = user_data.get("pending_posts", {}).get(draft_id)
    if not draft:
        await message.answer("Черновик больше не доступен.")
        await state.clear()
        return
    draft["image_file_id"] = message.photo[-1].file_id
    save_data(data)
    await message.answer("Картинка добавлена. Теперь нажмите «Опубликовать» в сообщении с черновиком.")
    await state.clear()


async def main() -> None:
    global scheduler_task
    print("пред. ком. очищены")
    await bot.delete_webhook(drop_pending_updates=True)
    print("бот запускается")
    scheduler_task = asyncio.create_task(scheduler_loop())
    try:
        await dp.start_polling(bot)
    finally:
        if scheduler_task:
            scheduler_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await scheduler_task


if __name__ == "__main__":
    import contextlib

    asyncio.run(main())
