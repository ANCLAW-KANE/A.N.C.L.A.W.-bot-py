﻿################# API-ключи ###############################

vktokenGroup=""

teletoken=""



################## id групп ###############################
IdGroupVK=

############################## Точки:источник-адресат для отправки из вк в телеграм #################################

Nodes = {# составлять по схеме ->
         # идентификтор чата (peer_id){узнать можно через /idchat} : (telegram_id){узнать можно через
         # стороннего бота @getmy_idbot }
	 # peer_id - номера бесед (создается при приглашении в бота в чат
	 # и обычно выдаются по порядку начиная с 2000000001

	#Первые 2 чата, перед добавлением (после :) id вашего телеграм канала  уберите # перед значением
        #2000000001: ,
        #2000000002: ,
    }

idGroupTelegram= # Общий канал для незарегистрированных чатов (которых нет в Nodes)

################## Адреса для уведомлений о падении и тд ###############################
PEER_CRUSH_EVENT = 
CAPTCHA_EVENT = 
#2000000001
############################### Списки и строки ###############################
users_list_warn = " @  " #теги оповещения в вк о падении

count_period = 25

################################# Словарь для слово-ответ ################################№
command = {
    '1'   : '1',
    '2': '2',
    '3': '3',
}

###################### MIME типы файлов для отправки в вк (документы) ####################
types = {
'vnd.openxmlformats-officedocument.wordprocessingml.document' : 'docx',
'vnd.openxmlformats-officedocument.spreadsheetml.sheet' : 'xlsx',
'plain' : 'txt',
}