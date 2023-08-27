from loguru import logger
from vkbottle.bot import BotLabeler
from vkbottle import GroupEventType, GroupTypes
from keyboards import keyboard_event
from tools import data_msg

labeler = BotLabeler()

@labeler.raw_event(event=GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent, blocking=False)
async def bot_event(ev: GroupTypes.MessageEvent):
    logger.log("STATE","\n_________________________EVT_________________________")
    await keyboard_event(ev.payload, ev).check_Callback()
    if data_msg.msg is not None: 
        await ev.send_message(f"{data_msg.msg}")