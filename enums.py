from enum import Enum

class Commands(Enum):
    quote_create = ('quote', (2, 2), 'create')
    quote_delete = ('quote', (2, 2), 'delete')
    quote_kill   = ('quote', (1, 2),   'kill')
    quote_update = ('quote', (2, 3), 'update')
    quote_list   = ('quote', (1, 2),   'list')

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

    settings_wrq = ('word','role','quote')
    settings_count = 'count'
    settings_chat = 'chat'
    settings_marry = ('marry','брак')
    settings_words = 'words'
    settings_quotes = 'quotes'
    
    mem = ('мем','mem','мемас','мемчик')
    cabal = 'cabal'
    settings = ('settings','set','s','настройки')
    info = ('i','info')

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
    