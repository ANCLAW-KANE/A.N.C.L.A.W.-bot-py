import re , logging, random
from sessions import vk,vk_user,bot
from CONFIG import IdGroupVK,OWNER_ALBUM_PHOTO
################################ VK TOOLS #################################################
def kick( chat_id, member_id):
    vk.messages.removeChatUser(chat_id=chat_id, user_id=member_id,member_id=member_id)

def send_to_specific_peer(msg,peerID):
    vk.messages.send(random_id=0, message=msg, peer_id=peerID)

def getUserName(object):  # извлечение имени и фамилии
    userId = int(object)
    if 0 < userId < 2000000000:
        username = vk.users.get(user_id=userId)
        first_name = username[0]['first_name']
        last_name = username[0]['last_name']
        user = str(first_name + " " + last_name)
        return user

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

def clear_docs():
    d = vk_user.docs.get(owner_id='-'+ str(IdGroupVK))
    docs = []
    for item in d['items']:
        doc = str(item['id'])
        docs.append(doc)
    for doc_ in docs:
        vk_user.docs.delete(owner_id='-'+ str(IdGroupVK),doc_id=doc_)
    return 'Удаление завершено'

def get_list_album():
    albums = vk_user.photos.getAlbums(owner_id=OWNER_ALBUM_PHOTO)
    listAlbum = []
    for item in albums['items']:
        album = str(item['id'])
        size = str(item['size'])
        privacy = str(item['privacy_view'])
        if re.compile("'all'").search(privacy):
            listAlbum.append(album+'_'+size)
    return listAlbum

def GET_CHAT_TITLE(object):
    get_items_chat = vk.messages.getConversationsById(peer_ids=object)
    for chats in get_items_chat['items']:
        chat_title = chats['chat_settings']['title']
        return chat_title

def RandomMember(peer):
    userID = random.choice((GetMembers(peer)[0]))
    username = vk.users.get(user_id=userID)
    first_name = username[0]['first_name']
    last_name = username[0]['last_name']
    user = str(first_name + " " + last_name)
    randMember = '@id' + str(userID)
    name_in_id = str(randMember + '(' + user + ')')
    return name_in_id
################################ TELEGRAM TOOLS ##############################################
def SendTG(adress,TB):
    bot.send_message(adress, TB)
    logging.info(TB)