from hashlib import md5
import random,json
from loguru import logger
from time import sleep
import time
from aiovk.api import API
from aiovk.sessions import TokenSession,VkCaptchaNeeded
from CONFIG import vktokenUser,full_permission_user_token
from tools import Formatter, json_config,calc_albums,get_sort_all_albums,get_max_photo,time_media
from aiohttp.client import ClientSession
from database_module.operations_repo import add_data_hash_audio


OWNER_ALBUM_PHOTO = json_config().read_key('sys','OWNER_ALBUM_PHOTO')

async def api_request(token,method,**params):
    try:
        vk = TokenSession(access_token=token)
        vk.API_VERSION = '5.131'
        api = API(session=vk)
        response = await api(method,**params)
        await vk.close()
    except VkCaptchaNeeded as e:
        c = vk.enter_captcha(e.url,e.sid)
        print(c)
    return response

async def get_list_album(method,params,token,v):
    url = f"https://api.vk.com/method/{method}?{Formatter.DictClass.dict_to_str(params, '=','&')}&access_token={token}&v={v}"
    async with ClientSession() as session:
        async with session.get(url) as response:
            alb_ph = await response.json()
        await session.close()
    sort = await get_sort_all_albums(api_obj=alb_ph)
    return sort

async def get_url_photo(photo):
    photo = await api_request(token=vktokenUser,method='photos.getById',photos=photo)
    return get_max_photo(photo)

async def get_photos(src):
    photoList = []
    alb_ph = await api_request(token=vktokenUser,method='photos.get', owner_id=OWNER_ALBUM_PHOTO,
                                           album_id=int(src.parse_album[0]), count=50,
                                           offset=random.randint(0, src.offset_max) * 50)
    for photo in alb_ph['items']:  photoList.append(str(photo['id']))
    return photoList

async def get_images_from_vk():
    list_a = await get_list_album(
        'photos.getAlbums',
        {'owner_id': json_config().read_key('sys','OWNER_ALBUM_PHOTO')},
        full_permission_user_token,
        '5.131'
    )
    alb = calc_albums(list_a)
    if alb.parse_album[1] != '0':
        alb_ph = await get_photos(alb)
        if alb_ph: return await get_url_photo(f"{str(OWNER_ALBUM_PHOTO)}_{random.choice(alb_ph)}")
            
            
async def get_audio(q:str,json_hash_name:str):
    start_time = time.time()
    data_pack = []
    data_pack_hash = []
    for block in range(2):
        sleep(2)
        audios = await api_request(token = vktokenUser, method='audio.search',
                        q=q,count=300, offset=300*(block))
        ids = ",".join([f"{i['owner_id']}_{i['id']}" for i in audios['items']])
        if ids:
            audio_with_url =await api_request(token=vktokenUser,method="audio.getById",audios=ids)
            data_hash = [
                {
                    'url': i['url'],
                    'md5hash': md5(i['url'].encode()).hexdigest(),
                    'name_audio': f"{i['artist']}-{i['title']}"
                } for i in audio_with_url
            ]
            data = [
                    {
                        'url': md5(i['url'].encode()).hexdigest(), 
                        'artist': i['artist'],
                        'title': i['title'],
                        'duration': time_media(i['duration'])
                    } for i in audio_with_url
            ]
            data_pack_hash.extend(data_hash)
            data_pack.extend(data)
    if not data_pack and not data_hash:
        return None
    with open(f'temps/{json_hash_name}.json','w') as f: json.dump(data_pack,f)
    await add_data_hash_audio(data_pack_hash)
    end_time = time.time()
    logger.warning(f" :find audio vk: {end_time - start_time}")
    return data_pack
    

async def get_content(url: str):
    userAgent = 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36'

    headers = {     
                'User-Agent': userAgent,
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            }
    async with ClientSession() as session:
            async with session.get(url,headers=headers) as f:
                if f.ok:  return await f.read()
