from loguru import logger
from vkbottle.bot import Message, BotLabeler
from vk_modules.hadlers_rules import PrefixRoleRule
from vk_modules.who_modules.role_handler import RoleCommand
################################################################################################


labeler = BotLabeler()

@labeler.message(PrefixRoleRule(),blocking=False)
async def role_command(msg: Message):
    logger.log("STATE","\n_________________________ROL_________________________")
    await RoleCommand(fromid=msg.from_id, peer=msg.peer_id, txt=msg.text, obj=msg).Check()