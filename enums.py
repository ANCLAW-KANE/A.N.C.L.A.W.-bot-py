from enum import Enum

class Commands(Enum):

    role_create  = ('role' , (5, 2), 'create')
    role_delete  = ('role' , (2, 2), 'delete')
    role_kill    = ('role' , (1, 2),   'kill')
    role_update  = ('role' , (5, 2), 'update')
    role_list    = ('role' , (1, 2),   'list')

    words_create = ('word', (3, 2), 'create')
    words_delete = ('word', (2, 2), 'delete')
    words_kill   = ('word', (1, 2),   'kill')
    words_update = ('word', (2, 3), 'update')
    words_list   = ('word', (1, 2),   'list')

    settings_wrq = ('word','role')
    settings_count = 'count'
    settings_chat = 'chat'
    settings_marry = ('marry','брак')
    settings_words = 'words'
    
    mem = ('мем','mem','мемас','мемчик')
    cabal = 'cabal'
    settings = ('settings','set','s','настройки')
    info = ('i','info')
    gen = ('g','г','gen','ген')
    mute = ('мут','mute','заткнуть','заткнись')
    ban = ('кик','kick','ban','бан')
    deleted = ('собак', 'удаленные')
    leaves = 'вышедших'

class Timestamp(Enum):
    minute = ('минута','минуты','минут','мин','м')
    hour = ('час','часа','часов','ч')
    day = ('день','дня','дней','д')
    month = ('месяц','месяца','месяцев','мес')
    year = ('год','года','лет','л')
    
class ColorsRGB:
    class default(Enum):
        white = (255, 255, 255)
        black = (5, 5, 5)
    
    class Colors(Enum):
        red = (224, 74, 47)
        light_blue = (142, 250, 246)
        light_blue_deep = (36,193,255)
        light_blue_1 = (92,192,242)
        purple = (190, 115, 217)
        green = (175, 224, 110)
        orange = (255, 176, 66)
        brown = (112,109,55)
        light_gray = (209,209,209)

size_values = list("smxopqryzw")
max_user_id = 2000000000
              

platforms = {
    1: 'мобильная версия сайта',
    2: 'iPhone',
    3: 'iPad',
    4: 'Android',
    5: 'Windows Phone',
    6: 'Windows 10',
    7: 'полная версия сайта'
}

treb_mems = {
     '1': [((340,75),(465,155)),((520,190),(680,300))],
     '2': [((160,70),(300,160)),((575,55),(710,140))],
     '3': [((460,315),(690,470)),((650,690),(890,850))],
     '4': [((545,200),(765,340))],
     '5': [((520,190),(680,300))],
     '6': [((460,315),(690,470))],
     '7': [((570,70),(730,170))],
     '8': [((300,110),(490,240))],
     '9': [((625,80),(890,260))],
    '10': [((745,85),(950,215))],
    '11': [((545,135),(790,300))],
    '12': [((410,110),(620,250))],
    '13': [((575,55),(710,140))],
    '14': [((580,105),(815,260))],
    '15': [((670,340),(860,470))]
}