from telethon import TelegramClient, events

# Initialize the Telegram client
import os

api_id = os.environ.get('api_id')
api_hash = os.environ.get('api_hash')

client = TelegramClient("session_name", api_id, api_hash)

# Variable to store the initial chat ID
target_chat_ids = {}
deliver_message=5


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


@client.on(events.NewMessage(pattern='tg chat load start:'))
async def start_forwarding(event):
    global target_chat_ids,deliver_message
    new_chat_to_forward= await get_channel_id((event.message.text.split(':')[-1]).replace(" ",""))
    if new_chat_to_forward not in target_chat_ids.keys():
        target_chat_ids[new_chat_to_forward]={"forward_to":[str(event.chat_id)],"messages":[]}
        await event.reply("Forwarding started. Messages from provided channel will be forwarded here.")
    else:
        if event.chat_id not in target_chat_ids[new_chat_to_forward]["forward_to"]:
            target_chat_ids[new_chat_to_forward]["forward_to"].append(str(event.chat_id))
            await event.reply("Forwarding started. Messages from provided channel will be forwarded here.")
        else:
            await event.reply("Forwarded already")
@client.on(events.NewMessage(pattern='tg chat load stop:'))
async def stop_forwarding(event):
    global target_chat_ids
    new_chat_to_forward = await get_channel_id((event.message.text.split(':')[-1]).replace(" ", ""))
    if new_chat_to_forward in target_chat_ids.keys():
        if str(event.chat_id) not in target_chat_ids[new_chat_to_forward]["forward_to"]:
            await event.reply("You are not forwarding this chanel")
        else:
            target_chat_ids[new_chat_to_forward]["forward_to"].remove(str(event.chat_id))
            if len(target_chat_ids[new_chat_to_forward]["forward_to"])==0:
                del(target_chat_ids[new_chat_to_forward])
            await event.reply("Forwarding stopped. Messages from provided channel will no longer be forwarded.")
    else:
        await event.reply("You are not forwarding this chanel")

@client.on(events.NewMessage(pattern='all tg chats load stop'))
async def stop_all_forwarding(event):
    global target_chat_ids
    for chat_id in target_chat_ids.keys():
        if str(event.chat_id) in target_chat_ids[chat_id]["forward_to"]:
            target_chat_ids[chat_id]["forward_to"].remove(str(event.chat_id))
            if len(target_chat_ids[chat_id]["forward_to"]) == 0:
                del (target_chat_ids[chat_id])
    await event.reply("You are stopped forwarding all channels")
@client.on(events.NewMessage())
async def forward_messages(event):
    global target_chat_ids
    print(target_chat_ids)
    print(event.chat_id)
    if str(event.chat_id) in target_chat_ids.keys():
        target_chat_ids[str(event.chat_id)]["messages"].append(event.message)
        if len(target_chat_ids[str(event.chat_id)]["messages"])>=deliver_message:
            for forward_to in target_chat_ids[str(event.chat_id)]["forward_to"]:
                try:
                    await client.forward_messages(int(forward_to), target_chat_ids[str(event.chat_id)]["messages"])
                except Exception as e:
                    print(f"[DEBUG] Failed sending request to chat_id: {e}")
            target_chat_ids[str(event.chat_id)]["messages"]=[]

print("Bot is running... Press Ctrl+C to stop.")
client.start()
client.run_until_disconnected()
