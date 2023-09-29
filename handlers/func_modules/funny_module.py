    
from online_tools import get_list_album
import math, random
from sessions import api_user
from tools import json_config


class Funny:    
    
    def __init__(self):
        self.OWNER_ALBUM_PHOTO = json_config().read_key('sys','OWNER_ALBUM_PHOTO')
        
#######################################/мем ######################################
    async def get_album_photos_mem(self):
        try:
            offset_max = 0
            photoList = []
            list_a = await get_list_album()
            parse_album = str(random.choice(list_a)).split(sep='_')
            if int(parse_album[1]) > 50: offset_max = math.floor(int(parse_album[1]) / 50)
            if parse_album[1] != '0':
                alb_ph = await api_user.photos.get(owner_id=self.OWNER_ALBUM_PHOTO,
                                                   album_id=parse_album[0], count=50,
                                                   offset=random.randint(0, offset_max) * 50)
                for photo in alb_ph.items:  photoList.append(str(photo.id))
                if photoList is not None or not []:
                    self.send_msg.attachment = f"photo{str(self.OWNER_ALBUM_PHOTO)}_{random.choice(photoList)}"
        except:
            self.send_msg.msg = f'Мем спизжен китайцами , повторите позже...'
            self.send_msg.attachment = 'photo388145277_456240127'

    
