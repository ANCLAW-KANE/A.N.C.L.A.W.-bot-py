import json,random,string,logging
from PIL import Image
from CONFIG import config_file_json
################################ TOOLS ##############################################
def to_tuple(obj):#li
    return str(list(obj)).replace('[','').replace(']','')
############################################################################
def write_file(name,getfile):
    with open(name, 'bw') as f:
        f.write(getfile)
############################################################################
def read_file_json(name):
    with open(name, "r") as f:
        data = json.load(f)
    return data
############################################################################
def write_file_json(name,data):
    with open(name, "w") as f:
        json.dump(data, f)
############################################################################
def BD_COUNT(get_,on_index):
    count = get_.fetchall()
    num = []
    for n in count:
        num.append(n[on_index])
    if not num: num.append(0)
    return num
############################################################################
def BD_LIST(get_,sep):
    ss = ''
    for word in get_:
        s = ''
        for ii in range(len(word)):
            if ii == 0:
                s += f"{word[ii]}"
            else:
                s += f" {sep} {word[ii]}"
        ss += f"{s}\n"
    if ss == '': ss = 'Ничего нет'
    return ss
############################################################################
def reverse_dict(get_dict):
    reverse = []
    for key in get_dict.keys():
        reverse.append((get_dict[key], key))
    getreverse = dict(reverse)
    return getreverse
############################################################################
def convert_img(inpt,output_name,convert_to):
    ipng = Image.open(inpt).convert()
    ipng.save(output_name,convert_to)
############################################################################
def get_BD_list(obj,query,sep):
    obj.execute(query)
    list_words = obj.fetchall()
    ss = BD_LIST(list_words,sep)
    return ss
############################################################################
def join_dict_keys(arg):
    args = []
    for a in arg:
        args += list(a.keys())
    return args
############################################################################
def join_dict(arg):
    args = []
    for a in arg:
        args += list(a.items())
    return dict(args)
############################################################################
def gen_r_s(l):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(l))
    print("Random string of length", l, "is:", rand_string)
############################################################################
def logger(inf):
    file_log = logging.FileHandler('Log.log', 'a', 'utf-8')
    console_out = logging.StreamHandler()
    logging.basicConfig(handlers=(file_log, console_out), format=u'[%(asctime)s | %(levelname)s]: %(message)s',
                        datefmt='%m.%d.%Y %H:%M:%S', level=logging.INFO)
    logging.info(inf)

######################################################################################################################
class json_gen:
    def __init__(self):
        self.dictionary =  {
                'idGroupTelegram' : 0,
                'PEER_CRUSH_EVENT' : 0,
                'CAPTCHA_EVENT' : 0,
                'OWNER_ALBUM_PHOTO' : 0,
                'users_list_warn' : [],
                'EVIL_GODS' : []
            }
        self.config = {
            ################## Целое число ###############################
            'idGroupTelegram': read_file_json(config_file_json)['idGroupTelegram'],
            # Общий канал для незарегестрированных чатов
            'PEER_CRUSH_EVENT': read_file_json(config_file_json)['PEER_CRUSH_EVENT'],
            'CAPTCHA_EVENT': read_file_json(config_file_json)['CAPTCHA_EVENT'],
            'OWNER_ALBUM_PHOTO': read_file_json(config_file_json)['OWNER_ALBUM_PHOTO'],
            ################## Списки и строки ###############################
            'users_list_warn': read_file_json(config_file_json)['users_list_warn'],  # теги оповещения в вк о падении
            'EVIL_GODS': read_file_json(config_file_json)['EVIL_GODS'],
        }
    ############################################################################
    def return_json(self):
        return self.dictionary
    ############################################################################
    def return_config_file_json(self):
        return self.config
######################################################################################################################