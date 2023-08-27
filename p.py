'''
from vkbottle.bot import Message

from sessions import vb

from respond_func import Respondent_command
import tracemalloc

@vb.on.message(text='/мем')
async def a(msg: Message):
    resp = Respondent_command(msg.text, msg.from_id, msg.peer_id, msg)
    r = await resp.get_album_photos_mem()
    await msg.answer(r[0], r[1])
vb.run_forever()
'''

cl = []
for i in range(0, 256): 
    cl.append(f'\x1b[38;5;{i}m')
for _ in range(0,101):
    for z in cl:
        print(f"■{z}",end='')