from telethon import TelegramClient, events
import asyncio
from telethon.errors.rpcerrorlist import FloodWaitError

api_id = "..."
api_hash = "..."
phone = "+7..."

client = TelegramClient("session_name", api_id, api_hash)
active_schedules = {}

@client.on(events.NewMessage(pattern="show start"))
async def start_schedule(event):
    chat_id = event.chat_id

    if chat_id in active_schedules:
        await event.reply("Show is already running.")
        return

    await event.reply("kk")

    async def send_message():
        try:
            while chat_id in active_schedules:
                print(f"[DEBUG] Sending news summary request to chat_id: {chat_id}")
                # First message
                await client.send_message(
                    chat_id,
                    "@PepTVbot create an audio message summarizing the news from the past 5 minutes in the style of a live TV presenter. "
                    "Don't forget about your tone of voice but keep it natural, engaging, and concise, with no hashtags to ensure clarity for listeners. "
                    "Limit the message to 2 paragraphs, 80 words tops."
                    "Don't start it with the word *breaking*"
                )
                await asyncio.sleep(120)  # Wait 60 seconds
                
                print(f"[DEBUG] Sending filler joke request to chat_id: {chat_id}")
                # Second message
                await client.send_message(
                    chat_id,
                    "@PepTVbot you're a live TV presenter. Awkward silence is in the studio. Create an engaging audio message with a joke in your style towards listeners to fill in the awkward silence. The joke needs to be sharp, biting, and hit right at the heart of those crypto wannabe edgelords who laugh at every dumb gag about currency."
                    "Limit the message to a length of a short tweet, 30 words tops."
                )
                await asyncio.sleep(120)  # Wait 60 seconds for the next cycle
        except FloodWaitError as e:
            print(f"[WARNING] Rate limited. Sleeping for {e.seconds} seconds.")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"[ERROR] Error in send_message: {e}")

    active_schedules[chat_id] = asyncio.create_task(send_message())

@client.on(events.NewMessage(pattern="show stop"))
async def stop_schedule(event):
    chat_id = event.chat_id

    if chat_id not in active_schedules:
        await event.reply("No active show in this chat.")
        return

    active_schedules[chat_id].cancel()
    del active_schedules[chat_id]
    await event.reply("Show stopped.")

print("[INFO] Bot is running...")
client.start()
client.run_until_disconnected()
