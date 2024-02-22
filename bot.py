import asyncio
import json
import os
import nest_asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from crawler import get_data

nest_asyncio.apply()
load_dotenv()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

async def update_channel_data(chat_id, channel_name, context):
    response = get_data(channel_name)
    if response["status"] == "success":
        file_creation_time = response["time"]
        if "new_titles" in response and response["new_titles"]:  
            new_titles = response["new_titles"]
            await send_list_items_as_messages(channel_name, chat_id, new_titles, context)
            completion_message = f"--- {channel_name.capitalize()} 업데이트 완료 {file_creation_time}"
            await context.bot.send_message(channel_name, chat_id=chat_id, text=completion_message)
        else: 
            no_new_data_message = f"--- {channel_name.capitalize()} 새로운 데이터가 없습니다. {file_creation_time}"
            await context.bot.send_message(chat_id=chat_id, text=no_new_data_message)
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"크롤링 작업에 실패했습니다. [{channel_name.capitalize()}]")

async def send_list_items_as_messages(channel_name, chat_id, data_list, context):
    MAX_MESSAGE_LENGTH = 4096
    message = ""
    for item in data_list:
        item_message = f"+ [NEW: {channel_name}]  {item}\n"  
        if len(message) + len(item_message) > MAX_MESSAGE_LENGTH:
            await context.bot.send_message(chat_id=chat_id, text=message)
            message = item_message 
        else:
            message += item_message
    if message:  
        await context.bot.send_message(chat_id=chat_id, text=message)

def load_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    except FileNotFoundError:
        return {"posts": {}}

def print_data():
    data = load_data('./public/posts_data.json')
    title = set(data["posts"].keys())
    return title

async def send_message(app: Application):
    await app.bot.send_message(chat_id=CHAT_ID, text="$harks Lockbit Monitoring Bot")

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    chat_id = update.message.chat_id

    commands_to_channels = {
        "lockbit -u": "lockbit",
        "blacksuit -u": "blacksuit",
        "alphv -u": "alphv",
        "leakbase -u": "leakbase",
    }

    if user_text in commands_to_channels:
        await update_channel_data(chat_id, commands_to_channels[user_text], context)

    if user_text == "리스트업":
        data_list = print_data()
        await send_list_items_as_messages(commands_to_channels[user_text], chat_id, data_list, context)
        await context.bot.send_message(chat_id=chat_id, text="--- 리스트업 완료")
    
async def update_periodically(channel_name, app: Application, chat_id: str):
    time = 3600
    if channel_name == 'leakbase':
        time = 300

    while True:
        response = get_data(channel_name)
        if response["status"] == "success":
            file_creation_time = response["time"]
            if "new_titles" in response and response["new_titles"]:  
                new_titles = response["new_titles"]
                await send_list_items_as_messages(channel_name, chat_id, new_titles, app)
                completion_message = f"--- {channel_name.capitalize()} 업데이트 완료 {file_creation_time}"
                await app.bot.send_message(chat_id=chat_id, text=completion_message)
            else:
                no_new_data_message = f"--- {channel_name.capitalize()} {file_creation_time} 새로운 데이터가 없습니다."
                await app.bot.send_message(chat_id=chat_id, text=no_new_data_message)
        else:
            await app.bot.send_message(chat_id=chat_id, text=f"크롤링 작업에 실패했습니다. [{channel_name.capitalize()}]")
        await asyncio.sleep(time)  


async def main():
    application = Application.builder().token(TOKEN).build()

    echo_handler = MessageHandler(filters.TEXT, handler)
    application.add_handler(echo_handler)
    
    asyncio.create_task(update_periodically('leakbase', application, CHAT_ID))
    asyncio.create_task(update_periodically('lockbit', application, CHAT_ID))
    asyncio.create_task(update_periodically('blacksuit', application, CHAT_ID))
    asyncio.create_task(update_periodically('alphv', application, CHAT_ID))

    await send_message(application)

    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
