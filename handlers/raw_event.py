from loguru import logger
from vkbottle.bot import BotLabeler
from vkbottle import GroupEventType, GroupTypes
from handlers.kb_handlers.keyboard_handler import keyboard_event

labeler = BotLabeler()

@labeler.raw_event(event=GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent, blocking=False)
async def bot_event(ev: GroupTypes.MessageEvent):
    logger.log("STATE","\n_________________________EVT_________________________")
    print("ev ::: ", ev)
    await keyboard_event(ev).check_Callback()

    