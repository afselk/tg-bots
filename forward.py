from telethon import TelegramClient, events

# Initialize the Telegram client
api_id = "..."
api_hash = "..."
phone = "+7..."

client = TelegramClient("session_name", api_id, api_hash)

# Variable to store the initial chat ID
target_chat_id = None
forwarding_enabled = False

@client.on(events.NewMessage(pattern='forward start'))
async def start_forwarding(event):
    global target_chat_id, forwarding_enabled
    target_chat_id = event.chat_id
    forwarding_enabled = True
    await event.reply("Forwarding started. Messages from selected channels will be forwarded here.")

@client.on(events.NewMessage(pattern='forward stop'))
async def stop_forwarding(event):
    global forwarding_enabled
    forwarding_enabled = False
    await event.reply("Forwarding stopped. Messages from selected channels will no longer be forwarded.")

# List of channels to monitor for messages
monitored_channels = ["@infinityhedge", "@shoalresearch", "@wublockchainenglish"]  # Add channel IDs or usernames

@client.on(events.NewMessage(chats=monitored_channels))
async def forward_messages(event):
    global target_chat_id, forwarding_enabled
    if forwarding_enabled and target_chat_id:
        await client.forward_messages(target_chat_id, event.message)

print("Bot is running... Press Ctrl+C to stop.")
client.start()
client.run_until_disconnected()
