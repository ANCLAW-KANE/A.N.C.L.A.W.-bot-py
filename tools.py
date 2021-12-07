import json
from PIL import Image

################################ TOOLS ##############################################

def to_tuple(object):
    return str(list(object)).replace('[','').replace(']','')

def write_file(name,getfile):
    with open(name, 'bw') as f:
        f.write(getfile)

def read_file_json(name):
    with open(name, "r") as f:
        data = json.load(f)
    return data

def write_file_json(name,data):
    with open(name, "w") as f:
        json.dump(data, f)

def BD_COUNT(get_,on_index):
    count = get_.fetchall()
    num = []
    for n in count:
        num.append(n[on_index])
    if not num: num.append(0)
    return num

def BD_LIST(get_):
    ss = ''
    for word in get_:
        s = ''
        for ii in word:
            s += f" - {ii}"
        ss += f"{s}\n"
    if ss == '': ss = 'Ничего нет'
    return ss

def reverse_dict(get_dict):
    reverse = []
    for key in get_dict.keys():
        reverse.append((get_dict[key], key))
    getreverse = dict(reverse)
    return getreverse

def convert_img(input,output_name,convert_to):
    ipng = Image.open(input).convert()
    ipng.save(output_name,convert_to)

def get_BD_list(obj,query):
    obj.execute(query)
    list_words = obj.fetchall()
    ss = BD_LIST(list_words)
    return ss

#def TGS_TO_GIF(in_,out):
#    pylottie.convertMultLottie2GIF(in_,out)