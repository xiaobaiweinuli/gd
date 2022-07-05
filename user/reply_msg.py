from telethon import events

from .login import user


@user.on(events.NewMessage(pattern=r'^re?[ 0-9]*$', outgoing=True))
async def mycp(event):
    num = event.raw_text.split(' ')
    num = int(num[-1]) if isinstance(num, list) and len(num) == 2 else 1
    reply = await event.get_reply_message()
    await event.delete()
    for _ in range(num):
        await reply.forward_to(int(event.chat_id))
