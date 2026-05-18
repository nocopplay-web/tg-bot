from os import getenv
import asyncio
from os import *
import sqlite3


from datetime import datetime
from aiogram.client.session.aiohttp import AiohttpSession
from datetime import date
from aiogram import Router, Bot, Dispatcher, html
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from aiogram.enums import parse_mode

load_dotenv()

token = getenv("BOT_TOKEN")

def create_deals_table():
    con = sqlite3.connect("deals.db")
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            buy_price REAL,
            sell_price REAL,
            buy_date TEXT,
            sell_date TEXT
        )
    """)
    con.commit()
    con.close()


if not token:
    raise ValueError("BOT_TOKEN не найден в файле .env. Пожалуйста, создайте файл .env и добавьте туда BOT_TOKEN=ваш_токен")

dp = Dispatcher()

rou = Router()
dp.include_router(rou)

@rou.message(Command("start"))
async def start(message: Message):
        await message.answer(
        "Я бот для записи подсчётов!\n\n"
        "Меня создал <b>@sintik_vb</b>\n\n"
        "Нужен бот пишите <a href='https://kwork.ru/user/nocopplay-dev'>сюда</a>\n",
        parse_mode="HTML")
    
@rou.message(Command("help"))
async def help(message: Message):
     await message.answer(
        "Вот что я умею:\n\n"
        "/start - запустить меня\n"
        "/buy - добавить покупку\n"
        "/sell - добавить продажу\n"
        "/history - история сделок\n"
        "/profit - общая прибыль\n"
        "/active - активные ваши товары\n")
    
    
@rou.message(Command("active"))
async def active(message: Message):
    user_id = message.from_user.id
    con = sqlite3.connect("deals.db")
    cursor = con.cursor()
    
    cursor.execute("SELECT * FROM deals WHERE user_id = ? AND sell_date IS NULL ORDER BY buy_date DESC", (user_id,))
    rows = cursor.fetchall()
    con.close()
    
    if len(rows) == 0:
        await message.answer("Активных товаров нет!")
        return
    
    text = "Активные товары:\n\n"
    
    for row in rows:
        name = row[2]
        buy_price =row[3]
        buy_date = row[5]
            
        buy_date_obj = date.fromisoformat(row[5])
        buy_date_display = buy_date_obj.strftime("%d.%m.%Y")
        
        text += f"{name} | Куплен: {buy_date_display} за {buy_price}\n"
    await message.answer(text)
    
@rou.message(Command("profit"))
async def profit(message: Message):
    user_id = message.from_user.id
    con = sqlite3.connect("deals.db")
    cursor = con.cursor()
    
    cursor.execute("SELECT SUM(sell_price - buy_price) FROM deals WHERE user_id = ? AND sell_price IS NOT NULL", (user_id,))
    result = cursor.fetchone()
    con.close()
    if result[0] is None:
        await message.answer("Прибыли пока нет")
    else:
        profit = result[0]
        await message.answer(f"Общая прибыль: {profit} руб.")
        
    
@rou.message(Command("history"))
async def history(message: Message):
    args = message.text.split()
    
    if len(args) > 2:
        await message.answer("Формат: /history или /history дата")
        return
    
    user_id = message.from_user.id
    
    con = sqlite3.connect("deals.db")
    cursor = con.cursor()
    
    if len(args) == 1:
        cursor.execute("SELECT * FROM deals WHERE user_id = ? ORDER BY buy_date DESC", (user_id,))
        rows = cursor.fetchall()
        con.close()
    elif len(args) == 2:
        date_str = args[1]
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
            date_iso = date_obj.isoformat()
        except ValueError:
            await message.answer("Неверный формат даты. Используйте ДД.ММ.ГГГГ, пример /history 17.05.2026")
            con.close()
            return
        cursor.execute("SELECT * FROM deals WHERE user_id = ? AND (buy_date = ? OR sell_date = ?) ORDER BY buy_Date DESC", (user_id, date_iso, date_iso))
        rows = cursor.fetchall()
        con.close()
        
        
    if len(rows) == 0:
        await message.answer("История пуста")
        return
    
    text = "История ваших сделок:\n\n"
    for row in rows:
        name = row[2]
        buy_price =row[3]
        sell_price = row[4]
        buy_date = row[5]
        sell_date = row[6]

    
        buy_date_obj = date.fromisoformat(row[5])
        buy_date_display = buy_date_obj.strftime("%d.%m.%Y")
        
        if sell_price is not None:
            sell_date_obj = date.fromisoformat(row[6])
            sell_date_display = sell_date_obj.strftime("%d.%m.%Y")
            profit = sell_price - buy_price
            text += f"{name} | Куплен: {buy_date_display} за {buy_price} | Продан: {sell_date_display} за {sell_price} | Прибыль: {profit}\n"
        else:
            text += f"{name} | Куплен {buy_date_display} за {buy_price} | Не продан\n"
    
    await message.answer(text)
    
@rou.message(Command("sell"))
async def sell(message: Message):
    args = message.text.split()
    
    if len(args) < 3:
        await message.answer("Формат: /sell название цена")
        return
    
    name = args[1]
    try:
        sell_price = float(args[2])
    except ValueError:
        await message.answer("Цена должна быть числом")
        return
    
    user_id = message.from_user.id
    con = sqlite3.connect("deals.db")
    cursor = con.cursor()
    
    cursor.execute("SELECT * FROM deals WHERE user_id = ? AND name = ? AND sell_date IS NULL ORDER BY buy_date ASC LIMIT 1", (user_id, name))
    row = cursor.fetchone()
    
    if row is None:
        await message.answer("Товар не найде или уже продан")
        con.close()
        return
    deal_id = row[0]
    buy_price = row[3]
    buy_date_str = row[5]
    
    buy_date_obj = date.fromisoformat(buy_date_str)
    buy_date_display = buy_date_obj.strftime("%d.%m.%Y")
    days = (date.today() - buy_date_obj).days
    profit = sell_price - buy_price
    profit_per_day = round(profit / days) if days > 0 else profit
    
    sell_date_str = date.today().isoformat()
    sell_date_display = date.today().strftime("%d.%m.%Y")
    
    cursor.execute("UPDATE deals SET sell_price = ?, sell_date = ? WHERE id = ?", (sell_price, sell_date_str, deal_id))    
    con.commit()
    con.close()
    
    await message.answer(
        f"{name} Продан {sell_date_display} за {sell_price}.\n"
        f"Куплен {buy_date_display} за {buy_price}.\n"
        f"Прошло {days} дней.\n"
        f"Прибыль: {profit} ({profit_per_day} руб/день)"
    )
@rou.message(Command("buy"))
async def buy(message: Message):
    args = message.text.split()
    
    if len(args) < 3:
        await message.answer("Формат: /buy название цена")
        return
        
    name = args[1]
    try:
        price = float(args[2])
    except ValueError:
        await message.answer("Цена должна быть числом")
        return
    
    user_id = message.from_user.id
    buy_date = date.today().isoformat()
    buy_date_display = date.today().strftime("%d.%m.%Y")
    
    con = sqlite3.connect("deals.db")
    cursor = con.cursor()
    cursor.execute("INSERT INTO deals (user_id, name, buy_price, buy_date) VALUES (?, ?, ?, ?)", (user_id, name, price, buy_date))
    con.commit()
    con.close()
    
    await message.answer(f"Покупка {name} за {price} руб.\nДата {buy_date_display}")
    
async def main():
    create_deals_table()
    session = AiohttpSession(proxy="http://45.95.56.189:8080")
    bot = Bot(token=token, session=session)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())
    
