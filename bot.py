import asyncio
import os
import json
import re
import shutil

from telethon import TelegramClient, events
from telethon.tl.types import InputMediaPhoto, KeyboardButton, ReplyInlineMarkup, KeyboardButtonRow, \
    KeyboardButtonCallback
import telethon.utils

from parsing import parsing, parse_channel_week, parse_channel_month
from screenshots import make_screenshot
from scripts import async_read_json_file, async_dump_json_file, get_channel_id, get_files_in_directory, \
    create_docx_from_screenshots


# Данные для авторизации
api_id = 1
api_hash = ''
token = ""
# Целевой канал
channel_id = ''


awaiting_channel_input = {}

# Читаем директорию с медиа
media_dir = 'media'
bot = TelegramClient('bot', api_id=api_id, api_hash=api_hash).start(bot_token=token)


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):

    start_botton = ReplyInlineMarkup(
        [
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(
                        text="Белый список слов",
                        data='withe'.encode('utf-8')
                    ),
                    KeyboardButtonCallback(
                        text="Черный список слов",
                        data=f'black'.encode('utf-8')
                    )
                ]
            ),
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(
                        text="Запустить парсер",
                        data=f'pars'.encode('utf-8')
                    ),
                    KeyboardButtonCallback(
                        text="Начать автоматическую публикацию",
                        data=f'publih'.encode('utf-8')
                    )
                ]
            ),
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(
                        text="Перезагрузка системы",
                        data=f'restart'.encode('utf-8')
                    ),
                    KeyboardButtonCallback(
                        text="Добавить каналы",
                        data=f'add_channels'.encode('utf-8')
                    )
                ]
            ),
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(
                        text="Формирование отчетов",
                        data=f'otchet'.encode('utf-8')
                    )
                ]
            )
        ]
    )
    await event.respond("Доброго времени суток! Данный бот работает в тестовом канале: https://t.me/testpotapov", buttons=start_botton)


@bot.on(events.CallbackQuery(data='withe'))
async def post(event):
    withe_list_words = (await async_read_json_file('words.json'))['withe_list_words']
    if withe_list_words and withe_list_words[0] != "":
        words = f"{withe_list_words[0]}"
        for i, word in enumerate(withe_list_words, start=1):
            words += f'\n{i} {word}'
        await event.respond(f"Список белого листа слов:{words}")
    else:
        await event.respond(f"Список белого листа слов пуст!")


@bot.on(events.CallbackQuery(data='black'))
async def post(event):
    black_list_words = (await async_read_json_file('words.json'))['black_list_words']
    if black_list_words:
        words = f"{black_list_words[0]}"
        for i, word in enumerate(black_list_words, start=1):
            words += f'\n{i} {word}'
        await event.respond(f"Список черного листа слов:{words}")
    else:
        await event.respond(f"Список черного листа слов пуст!")


@bot.on(events.CallbackQuery(data='pars'))
async def post(event):
    channels = (await async_read_json_file('channels.json'))['channels']
    await event.respond(f"Парсер запущен!")
    await parsing(channels)


@bot.on(events.CallbackQuery(data='publih'))
async def post(event):
    param_data = (await async_read_json_file('params.json'))['restart']
    await event.respond(f"Начинаю публикацию готовых постов!")
    while not param_data:
        posts = await async_read_json_file('posts.json')
        if posts:
            for post_id, post_info in posts.items():
                if not post_info["sent"]:
                    if post_info["photo"] in os.listdir(media_dir):
                        await bot.send_message(
                            entity=channel_id,
                            message=f"{post_info['text']}\n\nАвтор поста: {post_info['owner']}",
                            file=f'{media_dir}/{post_info["photo"]}'
                        )
                    else:
                        await bot.send_message(
                            entity=channel_id,
                            message=f"{post_info['text']}\n\nАвтор поста: {post_info['owner']}"
                        )
                posts[post_id]["sent"] = True
                await async_dump_json_file('posts.json', posts)
        else:
            await event.respond(f"На данный момент постов для публикации нет!\n"
                                f"Я продолжу работу в автоматическом режиме через 5 минут!")
            await asyncio.sleep(60 * 4 + 30)
        param_data = (await async_read_json_file('params.json'))['restart']
        await asyncio.sleep(30)
    param = (await async_read_json_file('params.json'))
    param['restart'] = False
    await async_dump_json_file('params.json', param)


@bot.on(events.CallbackQuery(data='restart'))
async def handle_restart(event):
    param_data = (await async_read_json_file('params.json'))
    param_data["restart"] = True
    await async_dump_json_file('params.json', param_data)
    if param_data:
        while param_data:
            await event.respond("Система перезагружается!")
            await asyncio.sleep(10)
            param_data = (await async_read_json_file('params.json'))['restart']
        await event.respond("Система успешно перезагрузилась! Все активные функции остановлены!")
        await start(event)


@bot.on(events.CallbackQuery(data='add_channels'))
async def add_channels_handler(event):
    sender_id = event.sender_id
    awaiting_channel_input[sender_id] = 'add_channels'
    await event.respond("Пожалуйста, введите ID канала или его @username:")


@bot.on(events.CallbackQuery(data='otchet'))
async def otchet(event):
    otchet_botton = ReplyInlineMarkup(
        [
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(
                        text="Сформировать недельный отчет",
                        data='weak'.encode('utf-8')
                    ),
                    KeyboardButtonCallback(
                        text="Сформировать месячный отчет",
                        data=f'mounht'.encode('utf-8')
                    )
                ]
            )
        ]
    )
    await event.respond("Пожалуйста, выберите формат отчета!", buttons=otchet_botton)


@bot.on(events.CallbackQuery(data='weak'))
async def weak_otchet(event):
    sender_id = event.sender_id
    awaiting_channel_input[sender_id] = 'weak'
    await event.respond("Пожалуйста, введите ссылку на канал для формирования недельного отчета:")


@bot.on(events.CallbackQuery(data='mounht'))
async def weak_otchet(event):
    sender_id = event.sender_id
    awaiting_channel_input[sender_id] = 'mounht'
    await event.respond("Пожалуйста, введите ссылку на канал для формирования месячного отчета:")


@bot.on(events.NewMessage())
async def handle_new_message_otchet(event):
    sender_id = event.sender_id
    if sender_id in awaiting_channel_input:
        if awaiting_channel_input[sender_id] == 'weak':
            message_text = event.message.message.strip()
            if re.search(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', message_text):
                channel_id = get_channel_id(message_text)
                posts = await parse_channel_week(channel_id)
                username = event.sender.username
                for post in posts:
                    make_screenshot(post['link'], post['id'], username)
                file_paths = get_files_in_directory(username)
                create_docx_from_screenshots(file_paths, f'{username}-недельный-отчет.docx')

                await event.respond('Вот ваш недельный отчет!', file=f'{username}-недельный-отчет.docx')
                shutil.rmtree(username)
                os.remove(f'{username}-недельный-отчет.docx')
                awaiting_channel_input.pop(sender_id)
            else:
                await event.respond("Пожалуйста, отправьте корректную ссылку.")
        elif awaiting_channel_input[sender_id] == 'mounht':
            username = event.from_user.username
            telegram_link = event.text
            channel_id = get_channel_id(telegram_link)
            posts = await parse_channel_month(channel_id)
            for post in posts:
                make_screenshot(post['link'], post['id'], username)
            file_paths = get_files_in_directory(username)
            create_docx_from_screenshots(file_paths, f'{username}-месячный-отчет.docx')

            await event.respond('Вот ваш месячный отчет!', file=f'{username}-месячный-отчет.docx')
            shutil.rmtree(username)
            os.remove(f'{username}-месячный-отчет.docx')
        elif awaiting_channel_input[sender_id] == 'add_channels':
            message_text = event.message.message.strip()
            # Проверка на наличие ссылки в сообщении
            if re.search(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', message_text):
                channels = await async_read_json_file('channels.json')
                if 'channels' not in channels:
                    channels['channels'] = []

                channel_new = message_text.split('/')[-1]
                if channel_new not in channels['channels']:
                    channels['channels'].append(channel_new)
                    await async_dump_json_file('channels.json', channels)
                    await event.respond(f"Ссылка {message_text} успешно добавлена!")
                else:
                    await event.respond(f"Ссылка {message_text} уже есть в списке.")
                awaiting_channel_input[sender_id] = False
            else:
                await event.respond("Пожалуйста, отправьте ссылку.")


print("Бот запущен.")
bot.run_until_disconnected()
