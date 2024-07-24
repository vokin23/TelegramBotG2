import asyncio
import shutil
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputFile, FSInputFile
from telethon import TelegramClient

from parsing import parse_channel_week, parse_channel_month
from screenshots import make_screenshot
from script import get_channel_id, create_docx_from_screenshots, get_files_in_directory


bot_token = '6875408032:AAHFg21Mlg-qWPQEx7TnsIltHlIhHIUVwzQ'




bot = Bot(token=bot_token)
dp = Dispatcher()

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Сформировать недельный отчет"),
            KeyboardButton(text="Сформировать месячный отчет")
        ]
    ]
)


class States_bot(StatesGroup):
    week = State()
    month = State()


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.answer(f'Доброго времени суток! Выберите какой отчет нужно сформировать!', reply_markup=start_kb)
    currnet_state = await state.get_state()
    if currnet_state is None:
        return
    await state.clear()


@dp.message(F.text == 'Сформировать недельный отчет')
async def handle_week(message: types.Message, state: FSMContext):
    await message.answer(f'Отправьте ссылку на канал!')
    await state.set_state(States_bot.week)


@dp.message(F.text == 'Сформировать месячный отчет')
async def handle_month(message: types.Message, state: FSMContext):
    await message.answer(f'Отправьте ссылку на канал!')
    await state.set_state(States_bot.month)


@dp.message(States_bot.week, F.text.contains('http'))
async def handle_week_number(message: types.Message, state: FSMContext):
    username = message.from_user.username
    telegram_link = message.text
    channel_id = get_channel_id(telegram_link)
    posts = await parse_channel_week(channel_id)
    for post in posts:
        make_screenshot(post['link'], post['id'], username)
    file_paths = get_files_in_directory(username)
    create_docx_from_screenshots(file_paths, f'{username}-недельный-отчет.docx')

    document = FSInputFile(f'{username}-недельный-отчет.docx')
    await bot.send_document(chat_id=message.chat.id, document=document, caption='Вот ваш недельный отчет!')
    shutil.rmtree(username)
    os.remove(f'{username}-недельный-отчет.docx')
    await state.clear()


@dp.message(States_bot.month, F.text.contains('http'))
async def handle_month_number(message: types.Message, state: FSMContext):
    username = message.from_user.username
    telegram_link = message.text
    channel_id = get_channel_id(telegram_link)
    posts = await parse_channel_month(channel_id)
    for post in posts:
        make_screenshot(post['link'], post['id'], username)
    file_paths = get_files_in_directory(username)
    create_docx_from_screenshots(file_paths, f'{username}-месячный-отчет.docx')

    document = FSInputFile(f'{username}-месячный-отчет.docx')
    await bot.send_document(chat_id=message.chat.id, document=document, caption='Вот ваш месячный отчет!')
    shutil.rmtree(username)
    os.remove(f'{username}-месячный-отчет.docx')
    await state.clear()


async def main():

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())