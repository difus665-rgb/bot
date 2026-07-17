import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# --- НАСТРОЙКИ ---
TOKEN = "8736462738:AAHYnNisq5No5j4d9MCMTYbVSdw6FVSGiMk"
ADMIN_IDS = [7294783514, 8866962638]  # Впиши сюда Telegram ID админов через запятую

# Временный список пользователей для рассылки (в памяти бота)
users_db = set()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- СОСТОЯНИЯ (FSM) ---
class Form(StatesGroup):
    waiting_for_helper_app = State()   
    waiting_for_tiktok_app = State()   
    waiting_for_youtube_app = State()  
    waiting_for_bug_report = State()   
    waiting_for_broadcast = State()    

# --- КЛАВИАТУРЫ ---

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Подать на хелпера", callback_data="apply_helper")],
    [InlineKeyboardButton(text="🎬 Подать на медию", callback_data="apply_media")],
    [InlineKeyboardButton(text="⚠️ Подать жалобу", callback_data="report_issue")],
    [InlineKeyboardButton(text="🐛 Баг/дюп", callback_data="report_bug")],
    [InlineKeyboardButton(text="❓ Прочее", callback_data="other")]
])

media_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📱 ТТ", callback_data="media_tiktok"),
        InlineKeyboardButton(text="🎥 ЮТ", callback_data="media_youtube")
    ],
    [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
])

cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")]
])

# Функция для безопасного экранирования спецсимволов в MarkdownV2
def escape_md(text: str) -> str:
    escaped = ""
    for char in text:
        if char in r"_*[]()~`>#+-=|{}.!":
            escaped += "\\" + char
        else:
            escaped += char
    return escaped


# --- ХЕНДЛЕРЫ ---

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    users_db.add(message.from_user.id)
    
    await message.answer(
        text="👋 *Lite SMP Support*\n\nВыбери действие:",
        reply_markup=main_menu,
        parse_mode="MarkdownV2"
    )

# Команда /broadcast для админов
@dp.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
        
    await message.answer("📢 Введите текст для рассылки пользователям бота (или нажмите кнопку отмены):", reply_markup=cancel_kb)
    await state.set_state(Form.waiting_for_broadcast)

# Обработка и отправка рассылки
@dp.message(Form.waiting_for_broadcast, F.text)
async def process_broadcast(message: Message, state: FSMContext):
    broadcast_text = f"📢 *РАССЫЛКА:*\n\n{message.text}"
    await message.answer(f"⏳ Начинаю рассылку для {len(users_db)} пользователей...")
    
    success_count = 0
    for user_id in users_db:
        try:
            await bot.send_message(chat_id=user_id, text=broadcast_text, parse_mode="Markdown")
            success_count += 1
            await asyncio.sleep(0.05)  
        except Exception:
            pass  

    await message.answer(f"✅ Рассылка завершена! Доставлено: {success_count} пользователям.")
    await state.clear()

@dp.callback_query(F.data.in_({"back_to_main", "cancel_action"}))
async def process_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text="👋 *Lite SMP Support*\n\nВыбери действие:",
        reply_markup=main_menu,
        parse_mode="MarkdownV2"
    )
    await callback.answer()

@dp.callback_query(F.data == "apply_media")
async def process_apply_media(callback: CallbackQuery):
    await callback.message.edit_text(
        text="✨ *Выбери платформу для подачи заявки на медиа-статус:*",
        reply_markup=media_menu,
        parse_mode="MarkdownV2"
    )
    await callback.answer()

@dp.callback_query(F.data == "apply_helper")
async def process_helper(callback: CallbackQuery, state: FSMContext):
    text_msg = (
        "📋 *Подача на хелпера*\n\n"
        "Критерии:\n"
        "\\- 14 лет\n"
        "\\- Быть адекватным, знать правила\n"
        "\\- Быть каждый день минимум 2 часа\n"
        "\\- Микрофон\n\n"
        "Отправь заявку в формате:\n\n"
        "1\\. Ник\n"
        "2\\. Возраст\n"
        "3\\. Что такое /ban /kick /mute\n"
        "4\\. Кем себя видишь\n"
        "5\\. Опыт\n"
        "6\\. Юзернейм для связи\n\n"
        "Напиши всё в одном сообщении\\."
    )
    await callback.message.edit_text(text=text_msg, reply_markup=cancel_kb, parse_mode="MarkdownV2")
    await state.set_state(Form.waiting_for_helper_app)
    await callback.answer()

@dp.callback_query(F.data == "media_youtube")
async def process_youtube(callback: CallbackQuery, state: FSMContext):
    text_msg = (
        "🎥 *Подача на ютубера*\n\n"
        "Критерии:\n"
        "\\- 50\\+ подписчиков\n"
        "\\- 100\\+ просмотров на видео / 500\\+ на шортсе/в ют\n"
        "\\- 1 видео на сервере с IP в описании\n"
        "\\- Видео ≥1080p 30fps\n"
        "\\- Адекватность и знание правил\n"
        "\\- Шортс раз в 2 дня / видео раз в неделю\n\n"
        "Отправь заявку в формате:\n\n"
        "1\\. Ник\n"
        "2\\. Ссылка на канал\n"
        "3\\. Возраст\n"
        "4\\. Образ себя\n"
        "5\\. Юзернейм для связи\n\n"
        "Напиши всё в одном сообщении\\."
    )
    await callback.message.edit_text(text=text_msg, reply_markup=cancel_kb, parse_mode="MarkdownV2")
    await state.set_state(Form.waiting_for_youtube_app)
    await callback.answer()

@dp.callback_query(F.data == "media_tiktok")
async def process_tiktok(callback: CallbackQuery, state: FSMContext):
    text_msg = (
        "📱 *Подача на тик токера*\n\n"
        "Критерии:\n"
        "\\- 30\\+ подписчиков\n"
        "\\- 50\\+ просмотров на видео / 350\\+ на шортсе/тт\n"
        "\\- 1 видео на сервере с IP в описании\n"
        "\\- Видео ≥1080p 30fps\n"
        "\\- Адекватность и знание правил\n"
        "\\- Шортс раз в 2 дня / видео раз в неделю\n\n"
        "Отправь заявку в формате:\n\n"
        "1\\. Ник\n"
        "2\\. Ссылка на канал\n"
        "3\\. Возраст\n"
        "4\\. Образ себя\n"
        "5\\. Юзернейм для связи\n\n"
        "Напиши всё в одном сообщении\\."
    )
    await callback.message.edit_text(text=text_msg, reply_markup=cancel_kb, parse_mode="MarkdownV2")
    await state.set_state(Form.waiting_for_tiktok_app)
    await callback.answer()

@dp.callback_query(F.data == "report_bug")
async def process_bug(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="🐛 *Репорт бага или дюпа*\n\nПожалуйста, подробно опиши найденный баг или дюп в одном сообщении\\. К этому разделу можно прикрепить фото\\.",
        reply_markup=cancel_kb,
        parse_mode="MarkdownV2"
    )
    await state.set_state(Form.waiting_for_bug_report)
    await callback.answer()

# Кнопка "Прочее" (Контакты администраторов)
@dp.callback_query(F.data == "other")
async def process_other(callback: CallbackQuery):
    await callback.message.edit_text(
        text="❓ *Раздел Прочее*\n\nПо дополнительным вопросам вы можете связаться с администрацией проекта:\n👉 @hkelnn2\n👉 @Azurekil",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]]),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "report_issue")
async def process_issue(callback: CallbackQuery):
    await callback.message.answer("Раздел находится в разработке.")
    await callback.answer()


# --- ПРИЕМ ЗАЯВОК (СТРОГО ОДНИМ ТЕКСТОВЫМ БЛОКОМ С ПРОВЕРКОЙ ЗАПОЛНЕНИЯ) ---

@dp.message(Form.waiting_for_helper_app, F.text)
async def app_helper_done(message: Message, state: FSMContext):
    # Проверка: если текст слишком короткий, просим написать нормально
    if len(message.text) < 20:
        await message.answer("❌ Ваше сообщение слишком короткое. Пожалуйста, заполните анкету полностью по пунктам в одном сообщении.")
        return

    username = f"@{message.from_user.username}" if message.from_user.username else "Нет юзернейма"
    full_admin_msg = (
        f"🔔 *НОВАЯ ЗАЯВКА НА ХЕЛПЕРА\\!*\n"
        f"От: {escape_md(username)} \\(ID: {message.from_user.id}\\)\n"
        f"────────────────────────\n"
        f"{escape_md(message.text)}"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=full_admin_msg, parse_mode="MarkdownV2")
        except Exception as e:
            logging.error(f"Ошибка отправки админу {admin_id}: {e}")

    await message.answer("✅ Ваша заявка на хелпера успешно отправлена администрации Lite SMP!", reply_markup=main_menu)
    await state.clear()

@dp.message(Form.waiting_for_youtube_app, F.text)
async def app_youtube_done(message: Message, state: FSMContext):
    if len(message.text) < 20 or "http" not in message.text.lower():
        await message.answer("❌ Пожалуйста, отправьте корректную заявку в одном сообщении, обязательно указав ссылку на ваш YouTube-канал.")
        return

    username = f"@{message.from_user.username}" if message.from_user.username else "Нет юзернейма"
    full_admin_msg = (
        f"🎥 *НОВАЯ ЗАЯВКА НА ЮТУБЕРА\\!*\n"
        f"От: {escape_md(username)} \\(ID: {message.from_user.id}\\)\n"
        f"────────────────────────\n"
        f"{escape_md(message.text)}"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=full_admin_msg, parse_mode="MarkdownV2")
        except Exception as e:
            logging.error(f"Ошибка отправки админу {admin_id}: {e}")

    await message.answer("✅ Ваша заявка на статус Ютубера успешно отправлена администрации Lite SMP!", reply_markup=main_menu)
    await state.clear()

@dp.message(Form.waiting_for_tiktok_app, F.text)
async def app_tiktok_done(message: Message, state: FSMContext):
    if len(message.text) < 20:
        await message.answer("❌ Пожалуйста, отправьте полную заполненную анкету на TikTok-медиа в одном сообщении.")
        return

    username = f"@{message.from_user.username}" if message.from_user.username else "Нет юзернейма"
    full_admin_msg = (
        f"📱 *НОВАЯ ЗАЯВКА НА ТИКТОК\\!*\n"
        f"От: {escape_md(username)} \\(ID: {message.from_user.id}\\)\n"
        f"────────────────────────\n"
        f"{escape_md(message.text)}"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=full_admin_msg, parse_mode="MarkdownV2")
        except Exception as e:
            logging.error(f"Ошибка отправки админу {admin_id}: {e}")

    await message.answer("✅ Ваша заявка на статус TikTok-медиа успешно отправлена администрации Lite SMP!", reply_markup=main_menu)
    await state.clear()

@dp.message(Form.waiting_for_bug_report, F.text | F.photo)
async def bug_report_done(message: Message, state: FSMContext):
    username = f"@{message.from_user.username}" if message.from_user.username else "Нет юзернейма"
    alert = f"⚠️ *КТО\\-ТО СООБЩИЛ О БАГЕ/ДЮПЕ\\!*\nОт: {escape_md(username)} \\(ID: {message.from_user.id}\\)\n\n"
    
    for admin_id in ADMIN_IDS:
        try:
            if message.photo:
                await bot.send_photo(
                    chat_id=admin_id, 
                    photo=message.photo[-1].file_id, 
                    caption=alert + escape_md(message.caption or "Фото без описания"),
                    parse_mode="MarkdownV2"
                )
            else:
                await bot.send_message(chat_id=admin_id, text=alert + escape_md(message.text), parse_mode="MarkdownV2")
        except Exception as e:
            logging.error(f"Не удалось отправить баг админу {admin_id}: {e}")
            
    await message.answer("✅ Спасибо за информацию! Репорт отправлен разработчикам Lite SMP.", reply_markup=main_menu)
    await state.clear()


# --- ЗАПУСК ---
async def main():
    print("Бот Lite SMP обновлен и запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())