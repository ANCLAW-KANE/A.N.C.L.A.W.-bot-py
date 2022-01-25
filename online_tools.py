import re , random,sqlite3
from datetime import datetime
from sessions import vk,vk_user,size_values,platforms
from CONFIG import IdGroupVK
from tools import json_gen,TEXT_SPLIT
from  vk_api.keyboard import VkKeyboard
######################################################################################################################
############################################## VK TOOLS ##############################################################
######################################################################################################################
def kick( chat_id, member_id):
    vk.messages.removeChatUser(chat_id=chat_id, user_id=member_id,member_id=member_id)
######################################################################################################################
def send_to_specific_peer(msg,peerID,key=None):
    msg = TEXT_SPLIT(msg, 4000)
    for z in msg: vk.messages.send(random_id=0, message=z, peer_id=peerID,keyboard=key)
######################################################################################################################

def create_keyboard(one_time,inline,list_butt):
    keyboard = VkKeyboard(one_time,inline)
    for i in list_butt: keyboard.add_callback_button(i[0],i[1],i[2])
    return keyboard.get_keyboard()
######################################################################################################################
def getUserName(obj):  # извлечение имени и фамилии
    try:
        userId = int(obj)
        if 0 < userId < 2000000000:
            username = vk.users.get(user_id=userId)
            user = str(username[0]['first_name'] + " " + username[0]['last_name'])
            return user
    except: pass
######################################################################################################################
def GetMembers(peer):
    members = vk.messages.getConversationMembers(peer_id=peer, group_id=IdGroupVK)
    membList = []
    membListNotAdmin = []
    membListAdmin = []
    for mbs in members['items']:
        member = mbs['member_id']
        admin = mbs.get('is_admin', False)
        if member > 0:
            membList.append(member)
            if not admin: membListNotAdmin.append(member)
            if admin: membListAdmin.append(member)
    return [membList, membListNotAdmin, membListAdmin]
######################################################################################################################
def get_list_album():
    albums = vk_user.photos.getAlbums(owner_id=json_gen().return_config_file_json()['OWNER_ALBUM_PHOTO'])
    listAlbum = []
    for item in albums['items']:
        album = str(item['id'])
        size = str(item['size'])
        privacy = str(item['privacy_view'])
        if re.compile("'all'").search(privacy): listAlbum.append(album+'_'+size)
    return listAlbum
######################################################################################################################
def GET_CHAT_TITLE(obj):
    get_items_chat = vk.messages.getConversationsById(peer_ids=obj)
    for chats in get_items_chat['items']: return chats['chat_settings']['title']
######################################################################################################################
def RandomMember(peer):
    userID = random.choice((GetMembers(peer)[0]))
    username = vk.users.get(user_id=userID)
    user = str(username[0]['first_name'] + " " + username[0]['last_name'])
    return str('@id' + str(userID) + '(' + user + ')')
######################################################################################################################
def get_tag(obj):
    try:
        tag_sep = obj.split(sep='|')
        tag_id = tag_sep[0].replace('[id', '')
        tag = re.findall(tag_id, obj)
        tag_name = tag_sep[1].replace(']', '')
        return [tag[0],tag_name,tag_id]
    except: return [None,None,None]
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
def get_conversation_message_ids(peer,id_,ext,fields):
    q = vk.messages.getByConversationMessageId(peer_id = peer,conversation_message_ids=id_,fields=fields,extended=ext)
    return q

######################################################################################################################

class Invertor(object):#класс для переключения 0 1 значений в БД
    def __init__(self,query,m1,m2,peer,update,index,type_,arg):
        self.query = query
        self.type_ = type_
        self.peer = peer
        self.m1 = m1
        self.m2 = m2
        self.update = update
        self.index = index
        self.arg = arg

    def key(self):
            BD = sqlite3.connect('peers.db')
            edit = BD.cursor()
            edit.execute(self.query)
            str_E_G = list(edit.fetchone())
            m = "ERROR"
            if str_E_G[self.index] == self.type_('0'):
                str_E_G = self.type_('1')
                m = self.m1
            elif str_E_G[self.index] == self.type_('1'):
                str_E_G = self.type_('0')
                m = self.m2
            edit.execute(self.update, (self.type_(str_E_G), self.arg))
            if BD.total_changes != 0:
                send_to_specific_peer(m,self.peer)
                BD.commit()
            else: send_to_specific_peer("Произошла непредвиденная поломка в переключении значения",self.peer)
            BD.close()

