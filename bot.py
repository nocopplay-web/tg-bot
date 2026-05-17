from os import getenv
import asyncio
from os import *

from aiogram import Router, Bot, Dispatcher, html
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from aiogram.enums import parse_mode

load_dotenv()

token = getenv("BOT_TOKEN")

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
        "Нужен бот пишите <a href='https://kwork.ru/user/nocopplay-dev'>сюда</a>",
        parse_mode="HTML")
    
@rou.message(Command("help"))
async def help(message: Message):
     await message.answer(
        "Вот что я умею:\n\n"
        "/start - запустить меня\n"
        "/add - добавить данные\n"
        "/check - посмотреть данные\n"
        "/checkdata - за определенный момент времени")
    
async def main():
    bot = Bot(token=token)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())