import re, random, sqlite3
from datetime import datetime
from sessions import vk, api_group, size_values, platforms, max_user_id
from CONFIG import IdGroupVK, full_permission_user_token
from tools import json_config, TEXT_SPLIT, dict_to_str
from vk_api.keyboard import VkKeyboard
from vkbottle.http import AiohttpClient


async def response_get_vk(method: str, params: dict, token: str, v: str):
    url = f"https://api.vk.com/method/{method}?{dict_to_str(params, '=')}&access_token={token}&v={v}"
    return await AiohttpClient().request_json(url)


######################################################################################################################
############################################## VK TOOLS ##############################################################
######################################################################################################################
async def kick(chat_id, member_id):
    await api_group.messages.remove_chat_user(chat_id=chat_id, user_id=member_id, member_id=member_id)


######################################################################################################################
def send_to_specific_peer(msg, peerID, key=None):
    msg = TEXT_SPLIT(msg, 4000)
    for z in msg: vk.messages.send(random_id=0, message=z, peer_id=peerID, keyboard=key)


######################################################################################################################

def create_keyboard(one_time, inline, list_butt):
    keyboard = VkKeyboard(one_time, inline)
    for i in list_butt: keyboard.add_callback_button(i[0], i[1], i[2])
    return keyboard.get_keyboard()


######################################################################################################################
async def getUserName(obj):  # извлечение имени и фамилии
    try:
        userId = int(obj)
        if 0 < userId < max_user_id:
            username = await api_group.users.get(user_id=userId)
            return str(username[0].first_name + " " + username[0].last_name)
    except:
        pass


######################################################################################################################
async def GetMembers(peer):
    members = await api_group.messages.get_conversation_members(peer_id=peer, group_id=IdGroupVK)
    membList = []
    membListNotAdmin = []
    membListAdmin = []
    memBots = []
    for mbs in members.items:
        member = mbs.member_id
        admin = mbs.is_admin
        owner = mbs.is_owner
        membList.append(member) if member > 0 else memBots.append(member)
        membListAdmin.append(member) if (admin or owner) else membListNotAdmin.append(member)
    # print([membList, membListNotAdmin, membListAdmin, memBots])
    return [membList, membListNotAdmin, membListAdmin, memBots]


######################################################################################################################
async def get_list_album():
    albums = await response_get_vk(
        'photos.getAlbums',
        {'owner_id': json_config().cfg_json()['OWNER_ALBUM_PHOTO']},
        full_permission_user_token,
        '5.131'
    )
    # api_user.photos.get_albums(owner_id=json_gen().return_config_file_json()['OWNER_ALBUM_PHOTO'])
    listAlbum = []
    for item in albums['response']['items']:
        album = str(item['id'])
        size = str(item['size'])
        privacy = str(item['privacy_view'])
        if re.compile("'all'").search(privacy): listAlbum.append(album + '_' + size)
    return listAlbum


######################################################################################################################
def GET_CHAT_TITLE(obj):
    get_items_chat = vk.messages.getConversationsById(peer_ids=obj)
    for chats in get_items_chat['items']: return chats['chat_settings']['title']


######################################################################################################################
async def RandomMember(peer):
    ListUserID = await GetMembers(peer)
    userID = random.choice(ListUserID[0])
    username = await api_group.users.get(user_ids=userID)
    user = str(username[0].first_name + " " + username[0].last_name)
    return str('@id' + str(userID) + '(' + user + ')')


######################################################################################################################
async def get_tag(obj):
    try:
        tag_sep = obj.split(sep='|')
        tag_id = tag_sep[0].replace('[id', '')
        tag = re.findall(tag_id, obj)
        tag_name = tag_sep[1].replace(']', '')
        return [tag[0], tag_name, tag_id]
    except:
        return [None, None, None]


######################################################################################################################
def get_max_photo(obj):
    urls = [size['url'] for size in obj['photo']['sizes']]
    types_ = [size['type'] for size in obj['photo']['sizes']]
    max_size = sorted(types_, key=lambda x: size_values.index(x))[-1]
    urldict = dict(zip(types_, urls))
    return urldict.get(max_size)


######################################################################################################################
def get_online(obj):
    fields = ''
    info = vk.users.get(user_ids=GetMembers(obj)[0], fields=['first_name', 'last_name', 'online', 'last_seen'])
    for field in info:
        online = '✅ONLINE' if field['online'] == 1 else '❌OFFLINE'
        get_seen = field.get('last_seen', None)
        if get_seen is not None:
            get_seen = f" C {datetime.fromtimestamp(get_seen['time'])} через " \
                       f"{platforms.get(get_seen['platform'])}" if online == '❌OFFLINE' else f"{platforms.get(get_seen['platform'])}"
        else:
            get_seen = ''
        fields += f"{field['first_name']} {field['last_name']} - {online} {get_seen}\n\n"
    return fields


######################################################################################################################
def get_conversation_message_ids(peer, id_, ext, fields):
    q = vk.messages.getByConversationMessageId(peer_id=peer, conversation_message_ids=id_, fields=fields, extended=ext)
    return q

######################################################################################################################
