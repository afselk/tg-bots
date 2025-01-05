# Telegram Forwarding Bot

This script is a Telegram bot that forwards messages from specified channels to a target chat upon receiving the `forward start` command. It stops forwarding messages when the `forward stop` command is issued.

## Features
- Start forwarding messages from selected channels with the `forward start` command.
- Stop forwarding messages with the `forward stop` command.
- Monitor and forward messages from multiple specified Telegram channels.

## Prerequisites
1. **Python 3.7 or higher**
2. **Telethon library**
   Install it using pip:
   ```bash
   pip install telethon
   ```
3. **Telegram API credentials**
   Generate API credentials for your Telegram account. You can obtain these credentials by following the instructions at [Telegram API Documentation](https://core.telegram.org/api/obtaining_api_id#obtaining-api-id).

## Setup
1. Clone or download this repository.
2. Replace the placeholders in the script with your Telegram API credentials:
   - `api_id`
   - `api_hash`
3. Specify the channels to monitor by adding their usernames or IDs to the `monitored_channels` list in the script.

## Running the Bot
To run the bot:

1. **Directly Run in Terminal**
   ```bash
   python3 your_script_name.py
   ```

2. **Run in Background Using nohup**
   ```bash
   nohup python3 your_script_name.py > output.log 2>&1 &
   ```
   - This command ensures the bot keeps running even if the terminal is closed.
   - Logs will be saved in `output.log`.

## Commands
- **Start Forwarding**: Send `forward start` to the bot to enable message forwarding.
- **Stop Forwarding**: Send `forward stop` to the bot to disable message forwarding.

## Customization
- Update the `monitored_channels` list in the script to include the channels you want to monitor.

## Example
- Monitored Channels: `@infinityhedge`, `@shoalresearch`, `@wublockchainenglish`
