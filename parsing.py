import asyncio
import os
from datetime import datetime, timedelta
import pytz
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest

from scripts import async_read_json_file, async_dump_json_file

api_id = 1
api_hash = ''
phone = ''


client = TelegramClient('phone', api_id, api_hash).start()


async def parsing(channels):
    bd = await async_read_json_file('bd.json')
    withe_list_words = (await async_read_json_file('words.json'))['withe_list_words']
    black_list_words = (await async_read_json_file('words.json'))['black_list_words']
    for channel in channels:
        channel_entity = await client.get_input_entity(channel)
        channel_id = channel_entity.channel_id
        # Ensure every channel_id is initialized in bd
        if str(channel_id) not in bd:
            bd[str(channel_id)] = 0  # Initialize with default value if not present

    await async_dump_json_file('bd.json', bd)

    if not os.path.exists("media"):
        os.makedirs("media")

    param_data = (await async_read_json_file('params.json'))['restart']
    while not param_data:
        for channel_id in bd.keys():
            new_posts = await client(GetHistoryRequest(
                peer=int(channel_id),  # Use channel_id directly
                limit=1,
                offset_id=0,
                offset_date=None,
                add_offset=0,
                max_id=0,
                min_id=0,
                hash=0
            ))

            if new_posts.messages:
                last_message = new_posts.messages[0]
                # The check below is now safe, as bd is guaranteed to have all channel_ids initialized
                if last_message.id > bd[str(channel_id)]:
                    message_conditions = not any(
                        black_word in last_message.message for black_word in black_list_words) and \
                                         all(withe_word in last_message.message for withe_word in withe_list_words)
                    if message_conditions:
                        post = await async_read_json_file('posts.json')
                        media_path = f"{channel_id}_{last_message.id}.png" if last_message.media and hasattr(
                            last_message.media, 'photo') else None
                        await client.download_media(last_message.media.photo, media_path) if media_path else None
                        post[f'{channel_id}-{last_message.id}'] = {
                            "text": last_message.message,
                            "owner": new_posts.chats[0].title,
                            "date": last_message.date.isoformat(),
                            "photo": media_path,
                            "sent": False
                        }
                        bd[str(channel_id)] = last_message.id  # Ensure to use str(channel_id) for consistency
                        await async_dump_json_file("posts.json", post)
                    await async_dump_json_file("bd.json", bd)
            await asyncio.sleep(1)
        param_data = (await async_read_json_file('params.json'))['restart']
    param = (await async_read_json_file('params.json'))
    param['restart'] = False
    await async_dump_json_file('params.json', param)
# channel_for_parsing = asyncio.run(async_read_json_file('channels.json'))
# client.loop.run_until_complete(parsing(channel_for_parsing))

async def connect():
    api_id = 23546937
    api_hash = '74f259c32ac5bc7904a121b77594edc9'
    phone = '+79773024886'
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