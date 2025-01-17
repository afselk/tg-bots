from telethon import TelegramClient, events
import asyncio
from telethon.errors.rpcerrorlist import FloodWaitError
import os
import json
import random

api_id = os.environ.get('api_id')
api_hash = os.environ.get('api_hash')

client = TelegramClient("session_name", api_id, api_hash)
active_schedules = {}
sleep_time=90

target_chat_ids = {}
deliver_message=5
forward_type="batch_forward_to"
prompts_config='prompts.json'

def is_negative_number(s):
    try:
        return int(s) < 0
    except ValueError:
        return False

async def get_channel_id(channel_username):
    try:
        if str(channel_username).isdigit() or str(channel_username).startswith('-100') or is_negative_number(channel_username):
            return str(channel_username)
        else:
            entity = await client.get_entity(channel_username)
            return str(entity.id)
    except:
        return False

async def stop_all_forwarding(event):
    global target_chat_ids
    for chat_id in list(target_chat_ids.keys()):
        for forward_type in ["batch_forward_to","direct_forward_to"]:
            if str(event.chat_id) in target_chat_ids[chat_id][forward_type]:
                target_chat_ids[chat_id][forward_type].remove(str(event.chat_id))

        if len(target_chat_ids[chat_id]["batch_forward_to"]) == 0 and len(target_chat_ids[chat_id]["direct_forward_to"]) == 0:
            del (target_chat_ids[chat_id])
    await event.reply("You are stopped forwarding all channels")

def choose_and_remove(elements, weights):
    chosen = random.choices(elements, weights=weights, k=1)[0]
    index = elements.index(chosen)
    elements.pop(index)
    weight = weights.pop(index)
    return chosen, weight

@client.on(events.NewMessage(pattern="tv start"))
async def start_schedule(event):
    chat_id = str(event.chat_id)

    if chat_id in active_schedules:
        await event.reply("Show is already running.")
        return

    await event.reply("kk")


    async def send_message():
        with open(prompts_config, 'r', encoding='utf-8') as file:
            available_prompts_with_weights = json.load(file)
        last_removed_prompt = []
        last_removed_weight = None
        while chat_id in active_schedules.keys():
            try:
                chosen_prompts,chosen_weight=choose_and_remove(available_prompts_with_weights["available_prompts"], available_prompts_with_weights["weights"])
                if last_removed_weight:
                    available_prompts_with_weights["available_prompts"].append(last_removed_prompt)
                    available_prompts_with_weights["weights"].append(last_removed_weight)
                if chosen_weight:
                    last_removed_prompt=chosen_prompts
                    last_removed_weight=chosen_weight

                    if len(chosen_prompts)==0:
                        print('comments')
                        message_sent=0
                        for source_chat_id in target_chat_ids.keys():
                            if (len(target_chat_ids[source_chat_id]["messages"]) >= deliver_message
                            and chat_id in target_chat_ids[source_chat_id]["batch_forward_to"]):
                                try:
                                    await client.send_message(int(chat_id),
                                                              "@PepTVbot provide comments on the latest chat from the Community Telegram group. Roast the poor quality comments, provide mild praise to any half-decent comments or questions. Mention that you can join the Community Telegram group using link under this stream."
                                                              + str([{k: v for k, v in item.items() if k != "id"} for item in target_chat_ids[source_chat_id]["messages"]]))
                                    message_sent+=1
                                    target_chat_ids[source_chat_id]["messages"] = []
                                except Exception as e:
                                    print(f"[DEBUG] Failed sending request to chat_id: {e}")

                        if message_sent:
                            await asyncio.sleep(sleep_time)
                    else:
                        await client.send_message(
                            int(chat_id),
                            random.choice(chosen_prompts)
                        )
                        await asyncio.sleep(sleep_time)
            except FloodWaitError as e:
                print(f"[WARNING] Rate limited. Sleeping for {e.seconds} seconds.")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"[ERROR] Error in send_message: {e}")

    active_schedules[chat_id] = asyncio.create_task(send_message())

@client.on(events.NewMessage(pattern="tv stop"))
async def stop_schedule(event):
    chat_id = str(event.chat_id)
    await stop_all_forwarding(event)
    if chat_id not in active_schedules:
        await event.reply("No active show in this chat.")
        return

    active_schedules[chat_id].cancel()
    del active_schedules[chat_id]
    await event.reply("Show stopped.")

@client.on(events.NewMessage(pattern="tv monitor chat start:"))
async def start_forwarding(event):
    global target_chat_ids,deliver_message
    new_chat_to_forward= await get_channel_id((event.message.text.split(':')[1]).replace(" ",""))
    if str(event.chat_id) in active_schedules.keys():
        if new_chat_to_forward not in target_chat_ids.keys():
            target_chat_ids[new_chat_to_forward]={"batch_forward_to":[],"direct_forward_to":[],"messages":[]}
            target_chat_ids[new_chat_to_forward][forward_type].append(str(event.chat_id))
            await event.reply("Forwarding started. Messages from provided channel will be forwarded here.")
        else:
            if event.chat_id not in target_chat_ids[new_chat_to_forward][forward_type]:
                target_chat_ids[new_chat_to_forward]["batch_forward_to"].append(str(event.chat_id))
                await event.reply("Forwarding started. Messages from provided channel will be forwarded here.")
            else:
                await event.reply("Forwarded already")
    else:
        await event.reply("Scheduler should be started")
@client.on(events.NewMessage(pattern="tv monitor chat drop:"))
async def stop_forwarding(event):
    global target_chat_ids
    new_chat_to_forward = await get_channel_id((event.message.text.split(':')[1]).replace(" ", ""))

    if new_chat_to_forward in target_chat_ids.keys():
        if str(event.chat_id) not in target_chat_ids[new_chat_to_forward][forward_type]:
            await event.reply("You are not forwarding this chanel")
        else:
            target_chat_ids[new_chat_to_forward][forward_type].remove(str(event.chat_id))
            if len(target_chat_ids[new_chat_to_forward]["batch_forward_to"])==0 and len(target_chat_ids[new_chat_to_forward]["direct_forward_to"])==0:
                del(target_chat_ids[new_chat_to_forward])
            await event.reply("Forwarding stopped. Messages from provided channel will no longer be forwarded.")
    else:
        await event.reply("You are not forwarding this chanel")

@client.on(events.NewMessage())
async def forward_messages(event):
    global target_chat_ids
    if str(event.chat_id) in target_chat_ids.keys():

        if event.sender:
            sender = await event.get_sender()
            if sender.bot:
                return
            author_name = sender.first_name or sender.username or "Unknown"
        elif event.message.fwd_from:
            author_name=(event.message.fwd_from.from_name or event.message.fwd_from.channel_post)
        else:
            author_name = "Unknown"
        if len(event.message.message)<200:
            target_chat_ids[str(event.chat_id)]["messages"].append({"author":author_name,"id":event.message.id,"message":event.message.message})

@client.on(events.MessageDeleted)
async def on_message_deleted(event):
    global target_chat_ids
    for target in target_chat_ids.keys():
        find_message_to_delete=False
        for message in target_chat_ids[target]["messages"]:
            if message['id'] in event.deleted_ids:
                find_message_to_delete=True
        if find_message_to_delete:
            target_chat_ids[target]["messages"]=[obj for obj in target_chat_ids[target]["messages"] if obj.get("id") not in event.deleted_ids]

print("[INFO] Bot is running...")
client.start()
client.run_until_disconnected()
