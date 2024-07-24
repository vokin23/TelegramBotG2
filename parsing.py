from datetime import datetime, timedelta
import pytz
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest


async def connect():
    api_id = 1
    api_hash = ''
    phone = '+7'
    # Создайте TelegramClient только один раз в main()
    client = TelegramClient(phone, api_id, api_hash)
    await client.start()
    return client


async def parse_channel_week(channel_id):
    pars = True
    client = await connect()
    timezone = pytz.timezone('Europe/Moscow')
    last_week = datetime.now(timezone) - timedelta(days=7)
    channel = await client.get_input_entity(channel_id)
    offset_id = 0
    limit = 100
    posts = []

    while pars:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))

        if not history.messages:
            break

        messages = history.messages

        for message in messages:
            message_date_utc = message.date.astimezone(pytz.UTC)
            if message_date_utc >= last_week:
                posts.append({
                    'id': message.id,
                    'link': f'https://t.me/{channel_id}/{message.id}',
                    'date': message.date
                })
            else:
                return posts

        offset_id = messages[len(messages) - 1].id
    return posts


async def parse_channel_month(channel_id):
    pars = True
    client = await connect()
    timezone = pytz.timezone('Europe/Moscow')
    last_week = datetime.now(timezone) - timedelta(days=30)
    channel = await client.get_input_entity(channel_id)
    offset_id = 0
    limit = 100
    posts = []


    while pars:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))

        if not history.messages:
            break

        messages = history.messages

        for message in messages:
            message_date_utc = message.date.astimezone(pytz.UTC)
            if message_date_utc >= last_week:
                posts.append({
                    'id': message.id,
                    'link': f'https://t.me/{channel_id}/{message.id}',
                    'date': message.date
                })
            else:
                return posts

        offset_id = messages[len(messages) - 1].id
    return posts


