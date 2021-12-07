from tools import read_file_json
################# API-ключи ###############################

vktokenGroup=""
vktokenUser= ''
teletoken=""
full_permission_user_token = ""

################## основное для работы ###############################
IdGroupVK=
ADMIN_JSON_CONFIG = []
config_file_json = 'CONFIG.json'

#///////////////////////изменяемые данные///////////////////////#
################## Адреса ###############################
idGroupTelegram =  read_file_json(config_file_json)['idGroupTelegram'] # Общий канал для незарегестрированных чатов
PEER_CRUSH_EVENT =  read_file_json(config_file_json)['PEER_CRUSH_EVENT']
CAPTCHA_EVENT =  read_file_json(config_file_json)['PEER_CRUSH_EVENT']
OWNER_ALBUM_PHOTO =  read_file_json(config_file_json)['PEER_CRUSH_EVENT']
################## Списки и строки ###############################
users_list_warn = read_file_json(config_file_json)['users_list_warn'] #теги оповещения в вк о падении
EVIL_GODS = read_file_json(config_file_json)['EVIL_GODS']
#///////////////////////изменяемые данные///////////////////////#


###################### MIME типы файлов для отправки в вк (документы) ####################
types = {
'vnd.openxmlformats-officedocument.wordprocessingml.document' : 'docx',
'vnd.openxmlformats-officedocument.spreadsheetml.sheet' : 'xlsx',
'plain' : 'txt',
}