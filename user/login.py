import asyncio
import os
from telethon import TelegramClient
from telethon import events, Button

from .. import API_HASH, API_ID, BOT, PROXY_START, PROXY_TYPE, connectionType, CONFIG_DIR
from .. import chat_id, jdbot, BOT_SET, logger
from ..bot.utils import press_event, V4, row, split_list

# 兼容青龙新版目录
try:
    qlver = os.environ['QL_BRANCH']
    QLMain = '/ql/data' if qlver >= 'v2.12.0' else '/ql'
except:
    QLMain = '/ql'

if BOT.get('proxy_user') and BOT['proxy_user'] != "代理的username,有则填写，无则不用动":
    proxy = {
        'proxy_type': BOT['proxy_type'],
        'addr': BOT['proxy_add'],
        'port': BOT['proxy_port'],
        'username': BOT['proxy_user'],
        'password': BOT['proxy_password']}
elif PROXY_TYPE == "MTProxy":
    proxy = (BOT['proxy_add'], BOT['proxy_port'], BOT['proxy_secret'])
else:
    proxy = (BOT['proxy_type'], BOT['proxy_add'], BOT['proxy_port'])


# 开启tg对话
if PROXY_START and BOT.get('noretry') and BOT['noretry']:
    user = TelegramClient(f'{CONFIG_DIR}/user', API_ID, API_HASH, connection=connectionType, proxy=proxy)
elif PROXY_START:
    user = TelegramClient(f'{CONFIG_DIR}/user', API_ID, API_HASH, connection=connectionType, proxy=proxy,
                          connection_retries=None)
elif BOT.get('noretry') and BOT['noretry']:
    user = TelegramClient(f'{CONFIG_DIR}/user', API_ID, API_HASH)
else:
    user = TelegramClient(f'{CONFIG_DIR}/user', API_ID, API_HASH, connection_retries=None)
#解决/user重复对话, user?不回复问题
if BOT_SET['开启user'].lower() == 'true':
    logger.info("开启user监控")
    user = user.start()

def restart():
    text = "pm2 restart jbot"
    os.system(text)


def start():
    file = "/jd/config/botset.json" if V4 else f"{QLMain}/config/botset.json"
    with open(file, "r", encoding="utf-8") as f1:
        botset = f1.read()
    botset = botset.replace('user": "False"', 'user": "True"')
    with open(file, "w", encoding="utf-8") as f2:
        f2.write(botset)
    restart()


def close():
    file = "/jd/config/botset.json" if V4 else f"{QLMain}/config/botset.json"
    with open(file, "r", encoding="utf-8") as f1:
        botset = f1.read()
    botset = botset.replace('user": "True"', 'user": "False"')
    with open(file, "w", encoding="utf-8") as f2:
        f2.write(botset)
    restart()


def state():
    file = "/jd/config/botset.json" if V4 else f"{QLMain}/config/botset.json"
    with open(file, "r", encoding="utf-8") as f1:
        botset = f1.read()
    return 'user": "True"' in botset
    

@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/user$'))
async def user_login(event):
    try:
        login = False
        sender = event.sender_id
        session = "/jd/config/user.session" if V4 else f"{QLMain}/config/user.session"
        async with jdbot.conversation(sender, timeout=120) as conv:
            msg = await conv.send_message("请做出你的选择")
            buttons = [
                Button.inline("重新登录", data="relogin") if os.path.exists(session) else Button.inline("我要登录", data="login"),
                Button.inline("关闭user", data="close") if state() else Button.inline("开启user", data="start"),
                Button.inline('取消会话', data='cancel')
            ]
            msg = await jdbot.edit_message(msg, '请做出你的选择：', buttons=split_list(buttons, row))
            convdata = await conv.wait_event(press_event(sender))
            res = bytes.decode(convdata.data)
            if res == 'cancel':
                await jdbot.edit_message(msg, '对话已取消')
                # return
            elif res == 'close':
                await jdbot.edit_message(msg, "关闭成功，准备重启机器人！")
                close()
            elif res == 'start':
                await jdbot.edit_message(msg, "开启成功，请确保session可用，否则请进入容器修改botset.json并删除user.session！\n现准备重启机器人！")
                start()
            else:
                await jdbot.delete_messages(chat_id, msg)
                login = True
        if login:
            await user.connect()
            async with jdbot.conversation(sender, timeout=100) as conv:
                msg = await conv.send_message('请输入手机号：\n例如：+8618888888888')
                phone = await conv.get_response()
                await user.send_code_request(phone.raw_text, force_sms=True)
                msg = await conv.send_message('请输入手机验证码:\n例如`code12345code`\n两边的**code**必须有！')
                code = await conv.get_response()
                await user.sign_in(phone.raw_text, code.raw_text.replace('code', ''))
                await jdbot.send_message(chat_id, '恭喜您已登录成功！\n自动重启中！')
            start()
    except asyncio.exceptions.TimeoutError:
        await jdbot.edit_message(msg, '登录已超时，对话已停止')
    except Exception as e:
        await jdbot.send_message(chat_id, '登录失败\n 再重新登录\n' + str(e))
    # finally:
    #     await user.disconnect()
