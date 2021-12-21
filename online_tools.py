import os, re , random ,requests,time,sqlite3
from datetime import datetime
from sessions import vk,vk_user,bot,size_values,upload,platforms
from CONFIG import IdGroupVK
from tools import json_gen,logger,write_file, convert_img
######################################################################################################################
############################################## VK TOOLS ##############################################################
######################################################################################################################
def kick( chat_id, member_id):
    vk.messages.removeChatUser(chat_id=chat_id, user_id=member_id,member_id=member_id)
######################################################################################################################
def send_to_specific_peer(msg,peerID):
    vk.messages.send(random_id=0, message=msg, peer_id=peerID)
######################################################################################################################
def getUserName(obj):  # извлечение имени и фамилии
    try:
        userId = int(obj)
        if 0 < userId < 2000000000:
            username = vk.users.get(user_id=userId)
            user = str(username[0]['first_name'] + " " + username[0]['last_name'])
            return user
    except:
        pass
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
        if member > 0 and admin != True:
            membListNotAdmin.append(member)
        if member > 0 and admin == True:
            membListAdmin.append(member)
    return [membList, membListNotAdmin, membListAdmin]
######################################################################################################################
def get_list_album():
    albums = vk_user.photos.getAlbums(owner_id=json_gen().return_config_file_json()['OWNER_ALBUM_PHOTO'])
    listAlbum = []
    for item in albums['items']:
        album = str(item['id'])
        size = str(item['size'])
        privacy = str(item['privacy_view'])
        if re.compile("'all'").search(privacy):
            listAlbum.append(album+'_'+size)
    return listAlbum
######################################################################################################################
def GET_CHAT_TITLE(obj):
    get_items_chat = vk.messages.getConversationsById(peer_ids=obj)
    for chats in get_items_chat['items']:
        chat_title = chats['chat_settings']['title']
        return chat_title
######################################################################################################################
def RandomMember(peer):
    userID = random.choice((GetMembers(peer)[0]))
    username = vk.users.get(user_id=userID)
    first_name = username[0]['first_name']
    last_name = username[0]['last_name']
    user = str(first_name + " " + last_name)
    randMember = '@id' + str(userID)
    name_in_id = str(randMember + '(' + user + ')')
    return name_in_id
######################################################################################################################
def get_tag(obj):
    try:
        tag_sep = obj.split(sep='|')
        tag_id = tag_sep[0].replace('[id', '')
        tag = re.findall(tag_id, obj)
        tag_name = tag_sep[1].replace(']', '')
        return [tag[0],tag_name]
    except:
        return [None,None]
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
    def __init__(self,sender,from_,query,m1,m2,peer,update,index,type_,arg):
        self.query = query
        self.type_ = type_
        self.sender = sender
        self.from_ = from_
        self.peer = peer
        self.m1 = m1
        self.m2 = m2
        self.update = update
        self.index = index
        self.arg = arg

    def key(self):
        if self.sender in self.from_:
            BD = sqlite3.connect('peers.db')
            edit = BD.cursor()
            edit.execute(self.query)
            str_E_G = list(edit.fetchone())
            if str_E_G[self.index] == self.type_('0'):
                str_E_G = self.type_('1')
                send_to_specific_peer(self.m1, self.peer)
            elif str_E_G[self.index] == self.type_('1'):
                str_E_G = self.type_('0')
                send_to_specific_peer(self.m2, self.peer)
            edit.execute(self.update, (self.type_(str_E_G), self.arg))
            print(self.update, (self.type_(str_E_G), int(self.arg)))
            BD.commit()
            BD.close()

######################################################################################################################
################################################ TELEGRAM TOOLS ######################################################
######################################################################################################################
class SendTG(object):
    def __init__(self, method, adress, log ,text, att):
        """
        :param method: 'txt', 'photo', 'audio'
        :param adress: int
        :param text: str
        :param att: [attachments]
        """
        self.n = 1000
        self.method = method
        self.adress = adress
        self.log = log
        self.text = len(text) if text is not None else 0
        self.text_sep = [text[i:i + self.n] for i in range(0, len(text) - (len(text) // self.n), self.n)] \
            if self.text != 0 else ''
        self.att = att
    ################################################################################################
    def send_message(self):
        if self.text_sep != '':
            for z in self.text_sep:
                bot.send_message(chat_id=self.adress,text=z,disable_web_page_preview=False)
                logger(z)
    ################################################################################################
    def send_photo(self):
        if self.text < self.n:
            for z in self.att:
                bot.send_photo(chat_id=self.adress, photo=z,caption=self.text_sep[0])
                logger(f"{self.log}")
        else:
            self.send_message()
            for z in self.att:
                bot.send_photo(chat_id=self.adress, photo=z)
                logger(f"{self.log}")
    ################################################################################################
    def send_audio(self):
        try:
            for z in self.att:
                bot.send_audio(chat_id=self.adress, audio=z, caption=f"{self.text_sep[0]}")
                logger(f"{self.text_sep[0]}")
        except:
            bot.send_message(chat_id=self.adress,text=f"{self.text_sep[0]}",disable_web_page_preview=False)
            logger(f"{self.text_sep[0]}")
    ################################################################################################
    def sender(self):
        #print(self.att)
        #print(self.text)
        #print(self.text_sep)
        #print(self.att)
        methods = {
            'txt': self.send_message,
            'photo': self.send_photo,
            'audio': self.send_audio,
        }
        if self.method in methods:
            methods.get(self.method)()
######################################################################################################################
######################################################################################################################
class SendTGtoVK(object):
    def __init__(self,obj,adress):
        self.obj = obj
        self.msg = self.obj.text
        self.idmessage_start = int(self.obj.message_id)
        self.adress = adress
        self.id = None
        self.caption = self.obj.caption if self.obj.caption is not None else ''
        self.name = None
        self.download = None
        self.att = None
    ################################################################################################
    def is_it(self):
        if self.obj.text:
            idmessage = int(self.obj.message_id) - 1
            if self.msg and not self.obj.forward_from and not self.obj.forward_sender_name:
                last_name = self.obj.from_user.last_name
                if last_name is None: last_name = ''
                self.caption = str(self.obj.from_user.first_name) + ' ' + last_name + ' : ' + self.msg
            if idmessage < self.idmessage_start:
                if self.obj.forward_from:
                    time.sleep(1)
                    last_name_fwd = self.obj.forward_from.last_name
                    if self.msg is None: self.msg = ''
                    if last_name_fwd is None: last_name_fwd = ''
                    user = str(self.obj.forward_from.first_name) + ' ' + str(last_name_fwd)
                    self.caption = ' От  ' + user + "\n " + str(self.msg)
                if self.obj.forward_sender_name:
                    time.sleep(1)
                    self.caption = ' От  ' + self.obj.forward_sender_name + "\n " + str(self.msg)
        elif self.obj.video:
            self.id = self.obj.video.file_id
            self.name = self.id + '.mp4'
            write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
            self.download = upload.video(video_file=self.name, name=self.id, wallpost=0, is_private=True, group_id=IdGroupVK)
            self.att = f"video{str(self.download['owner_id'])}_{str(self.download['video_id'])}?list={str(self.download['access_key'])}"
        elif self.obj.photo:
            try: self.id = self.obj.photo[2].file_id
            except: self.id = self.obj.photo[0].file_id
            self.name = self.id + '.jpg'
            write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
            self.download = upload.photo_messages(photos=self.name, peer_id=self.adress)[0]
            self.att = f"photo{str(self.download['owner_id'])}_{str(self.download['id'])}_{str(self.download['access_key'])}"
        elif self.obj.audio:
            self.id = self.obj.audio.file_id
            self.name = self.id + '.mp3'
            write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
            u = vk.docs.getMessagesUploadServer(type='audio_message', peer_id=self.adress)
            responses = requests.post(u['upload_url'], files={'file': open(self.id + '.mp3', 'rb')}).json()
            self.download = vk.docs.save(file=responses['file'])
            self.att = f"doc{str(self.download['audio_message']['owner_id'])}_{str(self.download['audio_message']['id'])}"
        elif self.obj.sticker:
            self.id = self.obj.sticker.file_id
            if str((bot.get_file(self.id)).file_path).split(sep='.')[1] != 'tgs':
                self.name = self.id + '.webp'
                write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
                convert_img(self.name, f"{self.id}.png", "png")
                self.download = upload.graffiti(image=f"{self.id}.png", group_id=IdGroupVK)
                self.att = f"doc{str(self.download['graffiti']['owner_id'])}_{str(self.download['graffiti']['id'])}_" \
                           f"{str(self.download['graffiti']['access_key'])}"
        elif self.obj.document:
            try:
                self.id = self.obj.document.file_id
                sep = str(self.obj.document.mime_type).split(sep='/')[1]
                if sep == 'mp4':
                    self.name = self.id + '.mp4'
                    write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
                    self.download = upload.video(video_file=self.name, name=self.id, wallpost=0, is_private=True,group_id=IdGroupVK,repeat=True)
                    self.att = f"video{str(self.download['owner_id'])}_{str(self.download['video_id'])}?list={str(self.download['access_key'])}"
                else:
                    file_type = self.obj.document.file_name.split(sep='.')[-1]
                    name_file = self.obj.document.file_name.split(sep='.')[0]
                    self.name = f"{self.id}.{file_type}"
                    write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
                    self.caption += f"\n{file_type}"
                    try:self.download = upload.document(doc=self.name, title=f"{name_file}.{file_type}",group_id=IdGroupVK, to_wall=0)
                    except:
                        os.remove(self.name)
                        self.name = self.id + '.test'
                        write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
                        self.download = upload.document(doc=self.name, title=f"{name_file}.test",group_id=IdGroupVK, to_wall=0)
                    self.att = f"doc{str(self.download['doc']['owner_id'])}_{str(self.download['doc']['id'])}?" \
                               f"{str(self.download['doc']['url']).split(sep='?')[1].replace('&no_preview=1', '')}"
            except Exception as e:
                vk.messages.send(random_id=random.randint(0, 999999), message=e, peer_id=json_gen().return_config_file_json()['PEER_CRUSH_EVENT'])
                SendTG('txt', self.obj.chat.id, e, f'\n⚠⚠⚠ Ошибка загрузки ⚠⚠⚠\n{e}', None).sender()
    ################################################################################################
    def upload_vk(self):
        try:
            self.is_it()
            vk.messages.send(random_id=random.randint(0, 999999), message=self.caption, peer_id=self.adress,attachment=self.att)
            logger(f"\n{self.att}\n")
            if self.name is not None : os.remove(f"{self.name}")
            try:os.remove(f"{self.id}.png")
            except:pass
        except:pass
######################################################################################################################