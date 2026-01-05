import discord
from discord.ext import commands
import os
import asyncio
import time
import requests

# List of tokens can be pasted here
TOKENS = [
    os.environ.get('DISCORD_TOKEN'),
]

# Whitelist
WHITELIST = ["billagotfam", "1397131599543271485", "vanshbhaiya12"]

# Headers for more authentic join requests
BROWSER_HEADERS = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://discord.com',
    'Referer': 'https://discord.com/channels/@me',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Discord-Locale': 'en-US',
}

async def start_bot(token):
    if not token:
        return

    client = discord.Client(self_bot=True)

    @client.event
    async def on_ready():
        print(f'SYSTEM ONLINE: {client.user} (ID: {client.user.id})')
        try:
            await client.change_presence(activity=discord.Game(name="Billa Botter"))
        except:
            pass

    @client.event
    async def on_message(message):
        if message.content.startswith('!'):
            author_id = str(message.author.id)
            author_name = str(message.author)
            if author_id not in WHITELIST and author_name not in WHITELIST:
                return

            cmd_parts = message.content.split(' ')
            cmd = cmd_parts[0][1:]
            args = cmd_parts[1:]

            if cmd == "join":
                invite_code = args[0].split('/')[-1]
                print(f"[{client.user}] Attempting advanced join for: {invite_code}")
                
                # Dynamic headers with token
                headers = BROWSER_HEADERS.copy()
                headers['Authorization'] = token
                # Discord uses X-Super-Properties for device info, often used in join checks
                headers['X-Super-Properties'] = 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwidmVyc2lvbiI6IjEyMC4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMCIsInJlZmVycmVyIjoiaHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8iLCJyZWZlcnJpbmdfZG9tYWluIjoiaHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8iLCJzZWFyY2hfZW5naW5lIjoiZ29vZ2xlIiwiY3VzdG9tX3JlZmVycmVyIjoiaHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8iLCJvc19hcmNoIjoieDg2In0='

                try:
                    # Direct API POST to simulate browser behavior
                    resp = requests.post(f'https://discord.com/api/v9/invites/{invite_code}', headers=headers, json={})
                    
                    if resp.status_code == 200:
                        print(f"[{client.user}] Join Success: Joined {resp.json().get('guild', {}).get('name', 'Server')}")
                    elif resp.status_code == 400 and 'captcha_key' in resp.json():
                        print(f"[{client.user}] BYPASS ATTEMPT: Discord requested captcha. Attempting header-spoof jump...")
                        # If headers weren't enough, we attempt one more time with a slightly different context
                        headers['X-Context-Properties'] = 'eyJsb2NhdGlvbiI6IkpvaW4gR3VpbGQiLCJndWlsZF9pZCI6bnVsbCwiY2hhbm5lbF9pZCI6bnVsbCwiY2hhbm5lbF90eXBlIjpudWxsfQ=='
                        retry_resp = requests.post(f'https://discord.com/api/v9/invites/{invite_code}', headers=headers, json={})
                        if retry_resp.status_code == 200:
                            print(f"[{client.user}] Bypass Success: Jumped captcha via context spoofing!")
                        else:
                            print(f"[{client.user}] Bypass Failed: Server requires manual captcha solution.")
                    else:
                        print(f"[{client.user}] Join Failed: {resp.status_code} - {resp.text}")
                except Exception as e:
                    print(f"[{client.user}] Join error: {e}")

            elif cmd == "vc":
                if not args: return
                try:
                    channel_id = int(args[0])
                    channel = client.get_channel(channel_id) or await client.fetch_channel(channel_id)
                    if isinstance(channel, discord.VoiceChannel):
                        await channel.connect()
                        print(f"[{client.user}] Joined VC: {channel.name}")
                except Exception as e:
                    print(f"[{client.user}] VC Error: {e}")

            elif cmd == "leave":
                await message.guild.leave()

            elif cmd == "dm":
                try:
                    user = await client.fetch_user(int(args[0]))
                    await user.send(" ".join(args[1:]))
                except Exception as e: print(f"DM error: {e}")

            elif cmd == "massdm":
                msg = " ".join(args)
                for m in message.guild.members:
                    if not m.bot: asyncio.create_task(m.send(msg))

            elif cmd == "purge":
                for m in message.guild.members:
                    if str(m.id) not in WHITELIST: asyncio.create_task(message.guild.ban(m))

            elif cmd == "nick":
                await message.guild.me.edit(nick=" ".join(args))

    try:
        await client.start(token)
    except Exception as e:
        print(f"Runtime Error: {e}")

async def main():
    if not TOKENS or not TOKENS[0]:
        print("TOKEN ERROR")
        return
    await asyncio.gather(*[start_bot(t) for t in TOKENS if t])

if __name__ == "__main__":
    asyncio.run(main())
