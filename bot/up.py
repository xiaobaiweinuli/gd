import os
import sys
from asyncio import exceptions

import requests
from telethon import events

from .update import version, botlog
from .. import chat_id, jdbot, logger, JD_DIR, BOT_SET


@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/upbot$'))
async def myupbot(event):
    msg = await jdbot.send_message(chat_id, "/upbot 监控机器人暂不支持原bot更新，会冲突。请使用 `/upgd` 更新")
    return


@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/ver$', incoming=True))
async def bot_ver(event):
    await jdbot.send_message(chat_id, f'当前版本\n{version}\n{botlog}')
