from requests import get
from urllib import request
from online_tools import get_max_photo, getUserName, get_conversation_message_ids, GET_CHAT_TITLE
from telebot.types import InputMediaPhoto, InputMediaAudio
from resend_function import SendTG

line_a = "\n___________________________\n"
###########################################################################################
media = {
    'doc': lambda at: ('txt', f"{str(at['doc']['url']).replace('no_preview=1', '')}" + line_a,
                       f"{str(at['doc']['url']).replace('no_preview=1', '')}" + line_a, None),
    'video': lambda at: ('txt', f"https://vk.com/video{at['video']['owner_id']}_{at['video']['id']}" + line_a,
                         f"https://vk.com/video{at['video']['owner_id']}_{at['video']['id']}" + line_a, None),
    "link": lambda at: ('txt', f"{at['link']['url']}" + line_a, f"{at['link']['url']}" + line_a, None),
    'audio_message': lambda at: ('audio', f"{at['audio_message']['link_mp3']}", "" if at == True else "",
                                 at['audio_message']['link_mp3']),
    'photo': lambda at: ('photo', f"{get_max_photo(at)}" + line_a, '', get_max_photo(at)),
    'audio': lambda at: ('audio', f" https://vk.com/audio{at['audio']['owner_id']}_{at['audio']['id']}",
                         f"https://vk.com/audio{at['audio']['owner_id']}_{at['audio']['id']}"
                         f"\n{at['audio']['artist']} - {at['audio']['title']} {at['audio'].get('subtitle', '')}\nДлительность: "
                         f"{str(int(at['audio']['duration']) // 60)}: {str(int(at['audio']['duration']) % 60)}" + line_a,
                         at['audio']['url']),
    'sticker': lambda at: ('photo', at['sticker']['images'][2]['url'] + line_a, '' if at == True else '',
                           get(at['sticker']['images'][2]['url']).content)
}
###########################################################################################
tab = {
    'chat_kick_user': lambda act: f"⚠⚠⚠ УДАЛЕН {str(getUserName(act['action']['member_id']))} ⚠⚠⚠",
    'chat_invite_user': lambda act: f"⚠⚠⚠ ДОБАВЛЕН {str(getUserName(act['action']['member_id']))} ⚠⚠⚠",
    'chat_invite_user_by_link': lambda act: f"⚠⚠⚠ ПРИГЛАШЕН ПО ССЫЛКЕ {str(getUserName(act['from_id']))} ⚠⚠⚠",
    'chat_title_update': lambda act: f"⚠⚠⚠ Обновлено название чата {str(act['action']['text'])} ⚠⚠⚠",
    'chat_photo_update': lambda act: f"⚠⚠⚠ Обновлено фото чата ⚠⚠⚠ ",
    'chat_photo_remove': lambda act: f"⚠⚠⚠ Удалено фото чата ⚠⚠⚠ ",
    'chat_pin_message': lambda act: f"⚠⚠⚠ {str(getUserName(act['action']['member_id']))} запинил сообщение:\n"
                                    f"{get_conversation_message_ids(act['peer_id'], act['action']['conversation_message_id'], None, None)['items'][0]['text']}",
    'chat_unpin_message': lambda act: f"⚠⚠⚠{str(getUserName(act['action']['member_id']))} отпинил сообщение ⚠⚠⚠"
}


###########################################################################################
class parse_resend(object):
    def __init__(self, node, obj, peer, from_):
        self.const_peer = 2000000000
        self.node = node
        self.obj = obj
        self.peer = peer
        self.from_ = from_
        self.user = str(getUserName(self.from_)) if self.from_ is not None else ''
        self.TitleChat = GET_CHAT_TITLE(self.peer) if self.peer > self.const_peer else ''
        self.TEXT = self.obj['text']
        self.tb = ''
        self.photos = []
        self.audios = []
        self.m = []
        self.key = None
        self.attachm = self.obj.get('attachments', 0)
        self.attachm_wall = self.attachm[0].get('wall', 0) if self.attachm != [] else None
        self.action = self.obj.get('action', 0)

    ###########################################################################################
    def text_box(self):
        self.tb += line_a
        ######################################## источник ################################################
        if self.peer > self.const_peer:
            self.tb += f"{self.user} ( https://vk.com/id{str(self.from_)} ) из чата : " \
                       f"{str(self.peer)}\n  [ {str(self.TitleChat)} ]\n"
        else:
            self.tb += f"\nЛичное сообщение от пользователя\n {str(self.user)} \n"
        if self.TEXT != '': self.tb += f"{line_a}{self.TEXT}{line_a}"

    ######################################## Вложения ################################################
    def attachment_box(self):
        self.text_box()
        message = self.tb
        for att in self.attachm:
            if att['type'] in media and att['type'] not in ['photo', 'audio', 'audio_message']:
                self.m += [media.get(att['type'])(att)]
            elif att['type'] == 'photo':
                self.photos.append(InputMediaPhoto(media.get(att['type'])(att)[3], caption=self.tb))
            elif att['type'] == 'audio' or 'audio_message':
                z = media.get(att['type'])(att)
                try:
                    request.urlopen(z[3])
                    message += z[2]
                    self.audios.append(InputMediaAudio(z[3], caption=message))
                    message = ""
                except:
                    self.m += [media.get(att['type'])(att)]

    ####################################### Стена #############################################
    def wall_parse(self):
        if self.attachm_wall:
            self.text_box()
            self.tb += "поделился постом :\n"
            ######################################## Имя источника ################################################
            ag = self.attachm_wall['from'].get('name', 0)
            attachm = self.attachm_wall.get('attachments', 0)
            if ag == 0:
                self.tb += f"\n Пользовтель: {self.attachm_wall['from']['first_name']}" \
                           f" {self.attachm_wall['from']['last_name']}"
            else:
                self.tb += f"\n группа: {self.attachm_wall['from']['name']}"
            ###########################################################################################
            if self.attachm_wall['text'] != '': self.tb += f"\n{line_a}\n{self.attachm_wall['text']}{line_a}"
            ###########################################################################################
            if attachm != 0:
                for wall_att in attachm:
                    self.m = media.get(wall_att['type'])(wall_att)
                    if wall_att['type'] == 'doc' or 'video' or 'link' or 'audio': self.tb += self.m[2]
                    if wall_att['type'] == 'photo': self.photos.append(InputMediaPhoto(self.m[3], caption=self.tb))

    ################################# Обработка событий чата ###################################
    def action_box(self):
        if self.obj['action'] is not None:
            if self.obj['action']['type'] in tab:
                self.key = f"Чат: {self.obj['peer_id']}\n {tab.get(self.obj['action']['type'])(self.obj)}"

    #############################################################################################################
    def sender(self):
        if self.TEXT != '' and self.attachm == []:
            self.text_box()
            SendTG('txt', self.node, self.tb, self.tb, []).sender()
        if self.attachm and not self.attachm_wall:
            self.attachment_box()
            for z in self.m: SendTG(z[0], self.node, f"{self.tb}\n {z[1]}", f"{self.tb}\n {z[2]}", [z[3]]).sender()
            if self.photos: SendTG('photo', self.node, f"{self.tb}\n ", f"{self.tb}\n ", self.photos).sender()
            if self.audios: SendTG('audio', self.node, f"{self.tb}\n ", f"{self.tb}\n ", self.audios).sender()
        if self.attachm_wall:
            self.wall_parse()
            if self.photos: SendTG('photo', self.node, f"{self.tb}\n {self.m[1]}", f"{self.tb}\n {self.m[2]}",
                                   self.photos).sender()
            if not self.photos: SendTG('txt', self.node, self.tb, self.tb, []).sender()
        if self.action != 0:
            if self.action['type'] in tab:
                self.action_box()
                SendTG('txt', self.node, self.key, self.key, []).sender()
