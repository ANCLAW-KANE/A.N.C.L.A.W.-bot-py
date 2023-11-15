import os, requests, time, traceback, random
from tools import logger, write_file, convert_img, TEXT_SPLIT, json_config
from sessions_vk import bot, upload, vk, client
from CONFIG import IdGroupVK


# global d_media_group,att
# id_media_group = []
# att = []
######################################################################################################################
################################################ TELEGRAM TOOLS ######################################################
######################################################################################################################
class SendTG(object):
    def __init__(self, method, adress, log, text, att):
        """
        :param method: Метод отправки('txt', 'photo', 'audio')
        :type method: str
        :param adress: куда отправить
        :type adress: int
        :param text: Текст сообщения
        :type text: str
        :param att: Список медиа вложений [attachments]
        :type att: list
        """
        self.n = 1000
        self.method = method
        self.adress = adress
        self.log = log
        self.text = len(text) if text is not None else 0
        self.text_sep = TEXT_SPLIT(text, self.n)
        self.att = att

    ################################################################################################
    def send_message(self):
        if self.text_sep != '':
            for z in self.text_sep:
                bot.send_message(chat_id=self.adress, text=z, disable_web_page_preview=False)
                logger(self.log)

    ################################################################################################
    def send_photo(self):
        if self.text > self.n:
            self.send_message()
        try:
            bot.send_media_group(chat_id=self.adress, media=self.att)
        except:
            bot.send_photo(chat_id=self.adress, photo=self.att[0], caption=self.text_sep)
        logger(f"{self.log}")

    ################################################################################################
    def send_audio(self):
        try:
            bot.send_media_group(chat_id=self.adress, media=self.att)
        except:
            bot.send_message(chat_id=self.adress, text=f"{self.text_sep[0]}", disable_web_page_preview=False)
        logger(f"{self.text_sep[0]}")

    ################################################################################################
    def sender(self):
        methods = {
            'txt': self.send_message,
            'photo': self.send_photo,
            'audio': self.send_audio,
        }
        if self.method in methods: methods.get(self.method)()


######################################################################################################################
######################################################################################################################
class SendTGtoVK(object):
    def __init__(self, obj, adress):
        self.obj = obj
        self.msg = self.obj.text
        self.idmessage_start = int(self.obj.message_id)
        self.adress = adress
        self.id = None
        self.caption = self.obj.caption if self.obj.caption is not None else ''
        self.name = None
        self.download = None
        self.att = ""

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
            if self.obj.video.file_size > 20971510:
                client.connect()
                client.download_file((bot.get_file(self.id)).file_path)
            else:
                write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
            self.download = upload.video(video_file=self.name, name=self.id,
                                         wallpost=0, is_private=True, group_id=IdGroupVK)
            self.att = f"video{str(self.download['owner_id'])}_" \
                       f"{str(self.download['video_id'])}?list={str(self.download['access_key'])}"
        elif self.obj.photo:
            try:
                self.id = self.obj.photo[2].file_id
            except:
                self.id = self.obj.photo[0].file_id
            self.name = self.id + '.jpg'
            write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
            self.download = upload.photo_messages(photos=self.name, peer_id=self.adress)[0]
            self.att = f"photo{str(self.download['owner_id'])}_{str(self.download['id'])}_" \
                       f"{str(self.download['access_key'])}"
        elif self.obj.audio:
            self.id = self.obj.audio.file_id
            self.name = self.id + '.mp3'
            write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
            u = vk.docs.getMessagesUploadServer(type='audio_message', peer_id=self.adress)
            responses = requests.post(u['upload_url'], files={'file': open(self.id + '.mp3', 'rb')}).json()
            self.download = vk.docs.save(file=responses['file'])
            self.att = f"doc{str(self.download['audio_message']['owner_id'])}_" \
                       f"{str(self.download['audio_message']['id'])}"
        elif self.obj.sticker:
            self.id = self.obj.sticker.file_id
            if str((bot.get_file(self.id)).file_path).split(sep='.')[1] != 'tgs':
                self.name = self.id + '.webp'
                write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
                convert_img(self.name, f"{self.id}.png", "png")
                self.download = upload.graffiti(image=f"{self.id}.png", group_id=IdGroupVK)
                try:
                    os.remove(f"{self.id}.png")
                except:
                    pass
                self.att = f"doc{str(self.download['graffiti']['owner_id'])}_{str(self.download['graffiti']['id'])}_" \
                           f"{str(self.download['graffiti']['access_key'])}"
        elif self.obj.document:
            try:
                self.id = self.obj.document.file_id
                sep = str(self.obj.document.mime_type).split(sep='/')[1]
                if sep == 'mp4':
                    self.name = self.id + '.mp4'
                    write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
                    self.download = upload.video(video_file=self.name, name=self.id, wallpost=0,
                                                 is_private=True, group_id=IdGroupVK, repeat=True)
                    self.att = f"video{str(self.download['owner_id'])}_" \
                               f"{str(self.download['video_id'])}?list={str(self.download['access_key'])}"
                else:
                    file_type = self.obj.document.file_name.split(sep='.')[-1]
                    name_file = self.obj.document.file_name.split(sep='.')[0]
                    self.name = f"{self.id}.{file_type}"
                    write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
                    self.caption += f"\n{file_type}"
                    try:
                        self.download = upload.document(doc=self.name, title=f"{name_file}.{file_type}",
                                                        group_id=IdGroupVK, to_wall=0)
                    except:
                        os.remove(self.name)
                        self.name = self.id + '.test'
                        write_file(self.name, bot.download_file((bot.get_file(self.id)).file_path))
                        self.download = upload.document(doc=self.name, title=f"{name_file}.test",
                                                        group_id=IdGroupVK, to_wall=0)
                    self.att = f"doc{str(self.download['doc']['owner_id'])}_{str(self.download['doc']['id'])}?" \
                               f"{str(self.download['doc']['url']).split(sep='?')[1].replace('&no_preview=1', '')}"
            except Exception as e:
                logger(f"\n________________________\n{traceback.format_exc()}\n"
                       f"________________________\n\n\n", "ERROR.log")
                vk.messages.send(random_id=random.randint(0, 999999), message=e,
                                 peer_id=json_config().cfg_json()['PEER_CRUSH_EVENT'])
                SendTG('txt', self.obj.chat.id, e, f'\n⚠⚠⚠ Ошибка загрузки ⚠⚠⚠\n{e}', []).sender()
        # return self.obj.chat.id , self.caption , self.att
        ################################################################################################

    def upload_vk(self):
        try:
            self.is_it()
            # if self.obj.media_group_id is None:
            vk.messages.send(random_id=0, message=self.caption, peer_id=self.adress, attachment=self.att)
            # elif self.obj.media_group_id > 0 and self.obj.media_group_id not in
            # else:
            #    if self.caption is not None: self.caption = self.caption
            #    if [self.obj.chat.id,self.obj.media_group_id] in id_media_group:
            #        att.append([self.obj.chat.id,self.att])
            #    else: id_media_group.append([self.obj.chat.id,self.obj.media_group_id])
            logger(f"{self.caption}\n{self.att}\n")
        except:
            logger(f"\n________________________\n{traceback.format_exc()}\n________________________\n\n\n", "ERROR.log")
            pass
        if self.name is not None:
            if os.path.isfile(self.name): os.remove(f"{self.name}")
######################################################################################################################
