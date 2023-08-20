import re
import sqlite3
import time
from threading import Thread

from vk_api import VkApi, vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

# def captcha_handler(captcha):
#    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
#    return captcha.try_again(key)
triggerCode = False
vk_session: VkApi = vk_api.VkApi(
    token="vk1.a.t81s1mnlZR1MPoGgsmO2itULKOAOx-lRnXBd_YyVyZUIPZcMGU8H9ARBRTOJqInh67dJcAl3Dkv1QbaD0rkrbSTGUoBeIBj7H2qYdXb-GpU1G2Lp41rIJ0e9QNZxOlcLLisGD740W2St-r0hi0rVQdNV3d6fs9--PQtnlkLXbMjGnfb4MPry35a3e3LkpMWT09z6qXPyR1zfIzAHteJrsQ")
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 206973016)


def getUserName(obj):  # извлечение имени и фамилии
    try:
        userId = int(obj)
        if 0 < userId < 2000000000:
            username = vk.users.get(user_id=userId)
            user = str(username[0]['first_name'] + " " + username[0]['last_name'])
            return user
    except:
        pass


def get_audio():
    global triggerCode
    BD = sqlite3.connect('audio.db')
    edit = BD.cursor()
    edit.execute("""CREATE TABLE IF NOT EXISTS users( userid INT PRIMARY KEY, token TEXT, audio_id TEXT); """)
    BD.commit()
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if 0 < int(event.object.message['peer_id']) < 2000000000:
                TEXT = event.object.message['text']
                TEXTSplit = str(TEXT).split(sep=' ')
                OBJ = event.object.message
                if len(TEXTSplit) == 2:
                    if TEXTSplit[0] == '/set-audio' and TEXTSplit[1] == \
                            re.findall("[vka-zA-Z0-9.a-zA-Z0-9.a-zA-Z0-9_-]{220}", TEXTSplit[1])[0] and OBJ.get(
                            'attachments', False):
                        audio = OBJ['attachments'][0]['audio']
                        audio_id = str(audio['owner_id']) + "_" + str(audio['id'])
                        print(event.object.message['peer_id'], " ::: ", audio_id)
                        try:
                            data = (event.object.message['peer_id'], TEXTSplit[1], audio_id)
                            edit.execute("INSERT INTO users VALUES(?, ?, ?)", data)
                        except:
                            data = (TEXTSplit[1], audio_id, event.object.message['peer_id'])
                            edit.execute("UPDATE users SET token = ?, audio_id = ? where userid = ?", data)
                        BD.commit()
                if TEXT == "/мой токен":
                    try:
                        token = edit.execute("SELECT token FROM users where userid = ?",
                                             (event.object.message['peer_id'],))
                        vk.messages.send(random_id=0, message=token, peer_id=event.object.message['peer_id'])
                    except:
                        vk.messages.send(random_id=0, message="Вы не зарегестрированы",
                                         peer_id=event.object.message['peer_id'])
                if TEXT == "/delete":
                    edit.execute("DELETE FROM users where userid = ?", (event.object.message['peer_id'],))
                    BD.commit()
                if TEXT == 'help':
                    vk.messages.send(random_id=0,
                                     message=f"Команды автостатуса:\n /set-audio токен + ваше аудиовложение\nпример: \n/set-audio 1aae9b6d....7c1сafe821\n"
                                             f"Токен можете взять с сайта >> https://vkhost.github.io/ << \nВыберите *Настройки* , в верхней части *Пользователь*\n"
                                             f"Выберите опции *Статус*, *Доступ в любое время*\nИ нажмите *Получить* в самом внизу , после на новой странце "
                                             f"*Разрешить* \nИ в адресной строке скопируйте ключ как с примера (ваш будет другой )"
                                             f"после access_token= до &expires\n\n/мой токен\nКоманда работает только в лс и гапоминает ваш токен\n"
                                             f"Удобно при смене аудио, так как не нужно брать новый\n\n/delete\nУдаляет вас из базы автостатуса\n\n",
                                     peer_id=event.object.message['peer_id'])
        if triggerCode: exit()


def set_audio():
    global triggerCode
    timing = time.time()
    while True:
        if time.time() - timing > 10.0:
            timing = time.time()
            BD = sqlite3.connect('audio.db')
            edit = BD.cursor()
            edit.execute("SELECT * FROM users")
            for data in edit.fetchall():
                try:
                    Vk: VkApi = vk_api.VkApi(token=data[1])
                    vk_audio = Vk.get_api()
                    vk_audio.audio.setBroadcast(audio=data[2])
                except Exception as e:
                    e = str(e).split(sep=' ')[0]
                    error = {
                        '[5]': (
                        f"{getUserName(data[0])} ! Неверный токен: {data[1]}\n Удаляю его из базы", int(data[0]),
                        f"DELETE FROM users where userid = {data[0]}"),
                        '[3610]': (
                        f"Страница {getUserName(data[0])} удалена.\n Уничтожаю аккаунт {data[0]} из базы.", 388145277,
                        f"DELETE FROM users where userid = {data[0]}"),
                        '[10]': (
                        f"Сбой сервера вк, неуспешная проверка токена для {getUserName(data[0])}. ID = {data[0]} ",
                        388145277, ''),
                    }
                    if e in error:
                        msg = error.get(e)
                        vk.messages.send(random_id=0, message=msg[0], peer_id=msg[1])
                        edit.execute(msg[2])
                        BD.commit()
                    else:
                        vk.messages.send(random_id=0,
                                         message=f"Невалидная запись:\n {data[0]} - {getUserName(data[0])}\n\n{e}",
                                         peer_id=388145277)
        time.sleep(1)
        if triggerCode: exit()


Get = Thread(target=get_audio, args=())
Get.start()
SetA = Thread(target=set_audio, args=())
SetA.start()

if not Get.join() or not SetA.join():
    triggerCode = True
