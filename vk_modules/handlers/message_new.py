import random
from loguru import logger
from vkbottle import PhotoMessageUploader
from vkbottle.bot import Message , BotLabeler
from vkbottle.dispatch.rules.base import PeerRule, FromUserRule,AttachmentTypeRule,StickerRule
from vkbottle.dispatch.rules.abc import AndRule
from vk_modules.handlers.keyboard_handler import keyboard_event
from vk_modules.handlers.respond_priv import privileges
from vk_modules.hadlers_rules import MessageNotCommandRule,MuteRule,MessageNotEmpty
from sessions_vk import api_group,vb
from database_module.markov_repo import MarkovRepository
from database_module.peer_repo import PeerRepository
from markov.generators import Generator
from tools import Writer, download_image,get_max_photo
from CONFIG import path_img

labeler = BotLabeler()

async def PhotoLoad(photo: bytes,msg:Message):
    upload = PhotoMessageUploader(vb.api)
    attachment = await upload.upload(file_source=photo,peer_id = msg.peer_id)
    await msg.answer(attachment=attachment)
    

async def process_ldem(generator: Generator,msg:Message):
    photo = await generator.generate_big_demotivator(square=True)
    if photo: await PhotoLoad(photo=photo,msg=msg)

async def process_dem(generator: Generator,msg:Message):
    photo = await generator.generate_demotivator()
    if photo: await PhotoLoad(photo=photo,msg=msg)

async def process_stck(msg:Message):
    stck = Writer.read_file_json('stickers_vk.json')
    if stck : 
        stickers = stck['sticker_vk']
        await  msg.answer(sticker_id=random.choice(stickers))

async def process_txt(generator: Generator,msg:Message):
    txt = await generator.generate_text()
    await  msg.answer(txt)

async def sticker_add(msg: Message):
    stcks = Writer.read_file_json('stickers_vk.json')
    if stcks and msg.attachments[0].sticker.sticker_id not in stcks['sticker_vk']: 
        stickers:list = stcks['sticker_vk']
        stickers.append(msg.attachments[0].sticker.sticker_id)
        data = {'sticker_vk': stickers}
        Writer.write_file_json('stickers_vk.json',data)

async def markov_manager(message:Message):
    mRepo = MarkovRepository(message.peer_id)
    history = await mRepo.get_history()
    generator = Generator(msg = history,obj=message.peer_id)

    pRepo = PeerRepository(message.peer_id)
    peer_repo = await pRepo.get_params_peer()
    r = random.randint(0, 100)
    chances = sorted([peer_repo['g_ldem'],peer_repo['g_dem'],peer_repo['g_stck'],peer_repo['g_txt']])
    nums = list(filter(lambda x: x >= r, chances))
    closest_number = min(nums) if nums else None
    data = {
        peer_repo['g_ldem']:(process_ldem,(generator,message)),
        peer_repo['g_dem']:(process_dem,(generator,message)),
        peer_repo['g_stck']:(process_stck,(message,)),
        peer_repo['g_txt']:(process_txt,(generator,message))
    }
    if closest_number in data:
        key = data.get(closest_number)
        await key[0](*key[1])

####################################################################################################
@labeler.message(MuteRule(), blocking=True)
async def mute(msg: Message):
    logger.log("STATE","\n_________________________Check_mute_________________________")
    await api_group.messages.delete(peer_id=msg.peer_id,delete_for_all=True, cmids=msg.conversation_message_id)
        

@labeler.message(StickerRule(),blocking=False)
async def sticker_func(msg:Message):
    logger.log("STATE","\n_________________________STICKER_________________________")
    await sticker_add(msg)
    await markov_manager(msg)

@labeler.message(MessageNotCommandRule(), blocking=False)
async def bot(msg: Message):
        logger.log("STATE","\n_________________________MSG_________________________")
        # if FSM(from_id, peerID).check_state() != None: send_to_specific_peer(c, peerID)
        if msg.payload: await keyboard_event(msg).check_Callback()
        await privileges(txt=msg.text, fromid=msg.from_id, peer=msg.peer_id, obj=msg).EVIL_GOD() #исправить


@labeler.message(MessageNotCommandRule(),FromUserRule(),PeerRule(), blocking=False)
async def markov_data(message: Message) -> None:
    logger.log("STATE","\n_________________________MARKOV_________________________")
    await markov_manager(message=message)
    
        
@labeler.message(~MessageNotEmpty(),AttachmentTypeRule("photo"),blocking=False)
async def save_photo(message: Message):
    logger.log("STATE","\n_________________________PHOTO_________________________")
    urls = [get_max_photo(i) for i in message.attachments[0:]]
    for img in urls: await download_image(img,path_img,message.peer_id)
    
