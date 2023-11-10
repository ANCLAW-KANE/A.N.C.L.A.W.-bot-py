    
from vk_modules.online_tools import get_list_album
import random
from sessions_vk import api_user
from tools import json_config,calc_albums,get_sort_all_albums

class Funny:    
    
    def __init__(self):
        self.OWNER_ALBUM_PHOTO = json_config().read_key('sys','OWNER_ALBUM_PHOTO')
    

#######################################/мем ######################################
    async def get_album_photos_mem(self):
        try:
            list_a = await get_sort_all_albums(await get_list_album())
            alb = calc_albums(list_a)
            parse_album = alb.parse_album
            offset_max = alb.offset_max
            if parse_album[1] != '0':
                alb_ph = await api_user.photos.get(owner_id=self.OWNER_ALBUM_PHOTO,
                                                   album_id=parse_album[0], count=50,
                                                   offset=random.randint(0, offset_max) * 50)
                photoList = [str(photo.id) for photo in alb_ph.items]
                if photoList is not None or not []:
                    self.send_msg.attachment = f"photo{str(self.OWNER_ALBUM_PHOTO)}_{random.choice(photoList)}"
        except:
            self.send_msg.msg = f'Мем спизжен китайцами , повторите позже...'
            self.send_msg.attachment = 'photo388145277_456240127'


    
