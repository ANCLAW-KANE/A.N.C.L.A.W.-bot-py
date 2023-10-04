import random
from aiovk.api import API
from aiovk.sessions import TokenSession
from CONFIG import vktokenUser,full_permission_user_token
from tools import Formatter, json_config,calc_albums,get_sort_all_albums,get_max_photo
from aiohttp.client import ClientSession

OWNER_ALBUM_PHOTO = json_config().read_key('sys','OWNER_ALBUM_PHOTO')

async def api_request(token,method,**params):
    vk = TokenSession(access_token=token)
    vk.API_VERSION = '5.131'
    api = API(session=vk)
    response = await api(method,**params)
    await vk.close()
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
        '5.131')
    alb = calc_albums(list_a)
    if alb.parse_album[1] != '0':
        alb_ph = await get_photos(alb)
        if alb_ph: return await get_url_photo(f"{str(OWNER_ALBUM_PHOTO)}_{random.choice(alb_ph)}")
            
            

    