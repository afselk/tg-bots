from telethon import TelegramClient, events
import asyncio
from telethon.errors.rpcerrorlist import FloodWaitError
import os
import json
import random

api_id = os.environ.get('api_id')
api_hash = os.environ.get('api_hash')
phone = os.environ.get('phone')

client = TelegramClient("session_name", api_id, api_hash)
active_schedules = {}
sleep_time=30


def choose_and_remove(elements, weights):
    chosen = random.choices(elements, weights=weights, k=1)[0]
    index = elements.index(chosen)
    elements.pop(index)
    weight = weights.pop(index)
    return chosen, weight

@client.on(events.NewMessage(pattern="show start"))
async def start_schedule(event):
    chat_id = event.chat_id

    if chat_id in active_schedules:
        await event.reply("Show is already running.")
        return

    await event.reply("kk")


    async def send_message():
        with open('prompts.json', 'r', encoding='utf-8') as file:
            available_prompts_with_weights = json.load(file)
        last_removed_prompt = []
        last_removed_weight = None
        while chat_id in active_schedules:
            try:
                chosen_prompts,chosen_weight=choose_and_remove(available_prompts_with_weights["available_prompts"], available_prompts_with_weights["weights"])
                if not last_removed_prompt and not None:
                    available_prompts_with_weights["available_prompts"].append(last_removed_prompt)
                    available_prompts_with_weights["weights"].append(last_removed_weight)
                last_removed_prompt=chosen_prompts
                last_removed_weight=last_removed_weight
                print(f"[DEBUG] Sending news summary request to chat_id: {chat_id}")

                await client.send_message(
                    chat_id,
                    random.choice(chosen_prompts)
                )
                await asyncio.sleep(sleep_time)

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
