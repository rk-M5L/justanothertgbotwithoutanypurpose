import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command 
from aiogram.types import Message
from aiogram.filters import BaseFilter
import requests
import time
from aiogram.filters import CommandObject
from sources import add_domain, load_domains, delete_domain
import shutil
from aiogram.types import FSInputFile


TOKEN = "TOKEN HERE"
ADMIN_id = "YOUR ID HERE"


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
#Логи

ALLOWED_USERS = [
    111111111,#name
    111111112,#name
    111111113,#name
    111111114,#name
    111111115,#name
    #telegram_id,#name
]

class IsAllowedUser(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        # Проверяем, есть ли ID отправителя в белом списке
        return message.from_user.id in ALLOWED_USERS






bot = Bot(token=TOKEN)
dp = Dispatcher()

# Путь к папке с ключами (создастся автоматически при первом запуске)
KEYS_DIR = os.path.join(os.path.dirname(__file__), "keys")
USED_DIR = os.path.join(os.path.dirname(__file__), "keys", "used")

@dp.message(Command("request"), IsAllowedUser())
async def cmd_button_request(message: Message):
    os.makedirs(KEYS_DIR, exist_ok=True)
    os.makedirs(USED_DIR, exist_ok=True)

    available_keys = [
        f for f in os.listdir(KEYS_DIR)
        if f.endswith(".conf") or f.endswith(".vpn")
    ]

    if not available_keys:
        await message.answer("❌Ключей нет. Нужно сгенерировать новые конфиги и положить в папку `keys/`.")
        return

    key_filename = available_keys[0]
    key_path = os.path.join(KEYS_DIR, key_filename)
    used_path = os.path.join(USED_DIR, key_filename)

    try:
        await message.answer_document(
            document=FSInputFile(key_path),
            caption=f"🔑 Твой ключ: `{key_filename}`\n\nИмпортируй файл в приложение Amnezia."
        )
        shutil.move(key_path, used_path)

        user = message.from_user
        username = f"@{user.username}" if user.username else "(username скрыт)"
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        
        admin_msg = (
            f"🔔 <b>Выдан новый ключ!</b>\n\n"
            f"👤 <b>Пользователь:</b> {full_name}\n"
            f"🔗 <b>Ссылка:</b> {username}\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
            f"📁 <b>Файл:</b> <code>{key_filename}</code>"
        )
        
        await bot.send_message(chat_id=ADMIN_id, text=admin_msg, parse_mode="HTML")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при выдаче ключа: {e}")
#Команада первая	


#Команада Вторая
@dp.message(Command("analyse"), IsAllowedUser())
async def cmd_button_analyse(message: Message, command: CommandObject):
    # Получаем аргумент после команды
    url = command.args
    
    if not url:
        await message.answer("Укажи сайт: /analyse https://example.com")
        return
        
    # Добавляем https://, если пользователь забыл
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    await message.answer(f"Щя будет {url}...")

    try:
        start_time = time.time()
        # timeout=10 означает, что если сайт не ответит за 10 сек, будет ошибка
        response = requests.get(url, timeout=10)
        end_time = time.time()
        
        # Время ответа в миллисекундах
        response_time_ms = (end_time - start_time) * 1000
        
        status_code = response.status_code
        
        if status_code == 200:
            await message.answer(
                f"✅ Сайт **** и пашет!\n"
                f"Код ответа: {status_code}\n"
                f"Время ответа: {response_time_ms:.0f} мс"
            )
        else:
            await message.answer(
                f"⚠️ Сайт ответил, но с ошибкой.\n"
                f"Код ответа: {status_code}\n"
                f"Время ответа: {response_time_ms:.0f} мс"
            )

    except requests.exceptions.Timeout:
        await message.answer("❌ Таймаут и *****. Сайт не ответил за 10 секунд.")
    except requests.exceptions.RequestException as e:
        # Ловим все остальные сетевые ошибки (неверный адрес, нет соединения и т.д.)
        await message.answer(f"❌ Ошибка подключения (пошел *****):\n{e}")
#Команада Вторая


def get_network_traffic():
    """Читает /proc/net/dev и возвращает (rx_bytes, tx_bytes) для основного интерфейса"""
    try:
        with open('/proc/net/dev', 'r') as f:
            lines = f.readlines()
        
        # Пропускаем первые две строки (заголовки)
        for line in lines[2:]:
            # Разделяем имя интерфейса и цифры
            parts = line.split(':')
            if len(parts) != 2:
                continue
                
            iface_name = parts[0].strip()
            
            # Нас интересуют только реальные интерфейсы, начинающиеся на e (ethernet)
            # Исключаем lo (loopback), docker, veth и т.д.
            if iface_name.startswith('e') and iface_name != 'lo':
                data = parts[1].split()
                # data[0] - байты полученные (RX)
                # data[8] - байты отправленные (TX)
                rx_bytes = int(data[0])
                tx_bytes = int(data[8])
                return iface_name, rx_bytes, tx_bytes
                
        return None, 0, 0
    except Exception as e:
        return None, 0, 0

def format_bytes(b):
    """Переводит байты в удобочитаемый вид (GiB, MiB)"""
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if b < 1024.0:
            return f"{b:.2f} {unit}"
        b /= 1024.0
    return f"{b:.2f} PiB"

@dp.message(Command("traffic"), IsAllowedUser())
async def cmd_button_traffic(message: Message):
    iface, rx, tx = get_network_traffic()
    
    if not iface:
        await message.answer("❌ Не удалось найти сетевой интерфейс.")
        return

    text = (
        f"📊 <b>Трафик сервера ({iface}):</b>\n\n"
        f"⬇️ <b>Принято (RX):</b> {format_bytes(rx)}\n"
        f"⬆️ <b>Отправлено (TX):</b> {format_bytes(tx)}\n\n"
        f"<i>Всего: {format_bytes(rx + tx)}</i>\n\n"
        f"<b>Внимание:</b> Это счетчики с момента последней перезагрузки сервера, а не за месяц."
    )
    
    await message.answer(text, parse_mode="HTML")
#Команада Третья
		
@dp.message(Command("domains"), IsAllowedUser())
async def cmd_button_domains(message: Message):
    domains = load_domains()
    
    if not domains:
        await message.answer("📭 Список доменов пуст. Добавь через /add example.com")
        return

    # Собираем красивый список с нумерацией
    domain_list_text = "\n".join([f"{i+1}. {d}" for i, d in enumerate(domains)])
    
    text = (
        f"📋 <b>Домены в списке ({len(domains)}):</b>\n\n"
        f"{domain_list_text}\n\n"
        f"<i>Проверить все сразу: /domains</i>"
    )
    
    await message.answer(text, parse_mode="HTML")
#Команда четвертая


@dp.message(Command("del"), IsAllowedUser())
async def cmd_del_domain(message: Message, command: CommandObject):
    domain = command.args
    if not domain:
        await message.answer("Укажи, что удалить: /del example.com")
        return

    if delete_domain(domain):
        await message.answer(f"Домен {domain} удален из списка.")
    else:
        await message.answer(f"Домен {domain} не найден в списке.")
#Команда пятая


#БЛОК КОМАНД С ДОМЕНАМИ
#БЛОК КОМАНД С ДОМЕНАМИ

@dp.message(Command("add"), IsAllowedUser())
async def cmd_add_domain(message: Message, command: CommandObject):
    text = command.args
    if not text:
        await message.answer("Пиши домены через пробел: /add google.com ya.ru")
        return

    domains_to_add = text.replace(",", " ").split()
    added, already_exists = [], []

    for d in domains_to_add:
        if add_domain(d):
            added.append(d)
        else:
            already_exists.append(d)

    response = ""
    if added:
        response += f"✅ Добавлено: {', '.join(added)}\n"
    if already_exists:
        response += f"⚠️ Уже были в списке: {', '.join(already_exists)}"
    await message.answer(response.strip())

#БЛОК КОМАНД С ДОМЕНАМИ
#БЛОК КОМАНД С ДОМЕНАМИ

#НЕ ТРОГАТЬ!!!
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())    
#НЕ ТРОГАТЬ!!!
    
