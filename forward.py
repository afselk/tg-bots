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

def check_forward_type(event):
    if (event.message.text.split(':')[2]).replace(" ","")=='batch':
        forward_type ="batch_forward_to"
    else:
        forward_type = "direct_forward_to"
    return forward_type
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
    new_chat_to_forward= await get_channel_id((event.message.text.split(':')[1]).replace(" ",""))
    forward_type=check_forward_type(event)

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
@client.on(events.NewMessage(pattern='tg chat load stop:'))
async def stop_forwarding(event):
    global target_chat_ids
    new_chat_to_forward = await get_channel_id((event.message.text.split(':')[1]).replace(" ", ""))
    forward_type=check_forward_type(event)

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

@client.on(events.NewMessage(pattern='all tg chats load stop'))
async def stop_all_forwarding(event):
    global target_chat_ids
    for chat_id in list(target_chat_ids.keys()):
        for forward_type in ["batch_forward_to","direct_forward_to"]:
            if str(event.chat_id) in target_chat_ids[chat_id][forward_type]:
                target_chat_ids[chat_id][forward_type].remove(str(event.chat_id))

        if len(target_chat_ids[chat_id]["batch_forward_to"]) == 0 and len(target_chat_ids[chat_id]["direct_forward_to"]) == 0:
            del (target_chat_ids[chat_id])
    await event.reply("You are stopped forwarding all channels")
@client.on(events.NewMessage())
async def forward_messages(event):
    global target_chat_ids
    print (target_chat_ids)
    if str(event.chat_id) in target_chat_ids.keys():

        if event.sender:
            sender = await event.get_sender()
            author_name = sender.first_name or sender.username or "Unknown"
        elif event.message.fwd_from:
            author_name=(event.message.fwd_from.from_name or event.message.fwd_from.channel_post)
        else:
            author_name = "Unknown"

        target_chat_ids[str(event.chat_id)]["messages"].append({"author":author_name,"id":event.message.id,"message":event.message.message})

        for target_chat_id in target_chat_ids[str(event.chat_id)]["direct_forward_to"]:
            try:
                await client.forward_messages(int(target_chat_id), event.message)
            except Exception as e:
                print(f"[DEBUG] Failed sending request to chat_id: {e}")
        if len(target_chat_ids[str(event.chat_id)]["messages"])>=deliver_message:
            for forward_to in target_chat_ids[str(event.chat_id)]["batch_forward_to"]:
                try:
                    await client.send_message(int(forward_to), "The following are new messages from the Telegram chats: "+str([{k: v for k, v in item.items() if k != "id"} for item in target_chat_ids[str(event.chat_id)]["messages"]]))
                except Exception as e:
                    print(f"[DEBUG] Failed sending request to chat_id: {e}")
            target_chat_ids[str(event.chat_id)]["messages"]=[]

@client.on(events.MessageDeleted)
async def on_message_deleted(event):
    global target_chat_ids
    for target in target_chat_ids.keys():
        find_message_to_delete=False
        for message in target_chat_ids[target]["messages"]:
            if message['id']==event.deleted_id:
                find_message_to_delete=True
        if find_message_to_delete:
            target_chat_ids[target]["messages"]=[obj for obj in target_chat_ids[target]["messages"] if obj.get("id") != event.deleted_id]


print("Bot is running... Press Ctrl+C to stop.")
client.start()
client.run_until_disconnected()
