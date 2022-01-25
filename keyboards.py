from respond_who import WHO
from tools import to_list
import json

class keyboard_event(object):
    def __init__(self,pay,msg = None):
        self.msg = msg
        self.pay = dict(json.loads(pay))
        self.pay_key_sep = str(list(self.pay.keys())[0]).split("_",1)
        self.pay_val = to_list(list(self.pay.values()))
        self.pay_val_ = self.pay_val.append(self.pay_key_sep[1])


    def check(self):
        #print(self.pay_key_sep, "///", self.pay_val )
        pay = {
            'M':WHO(fromid=int(self.msg['user_id']),peer=int(self.msg['peer_id']),
                kb=[int(self.pay_val[0]),int(self.pay_val[1]),int(self.pay_val[2]),self.pay_val[3]]).marry_control
        }
        if self.pay_key_sep[0] in pay:
            if self.pay_key_sep[0] is not None:
                pay.get(self.pay_key_sep[0])()