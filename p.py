
"""
cl = []
for i in range(0, 256): 
    cl.append(f'\x1b[38;5;{i}m')
for _ in range(0,101):
    for z in cl:
        print(f"■{z}",end='')
"""



"""class Params:
    def __init__(self, peer_id, man1, man2, man1name, man2name, allow, await_state):
        self.peer_id = peer_id
        self.man1 = man1
        self.man2 = man2
        self.man1name = man1name
        self.man2name = man2name
        self.allow = allow
        self.await_state = await_state

from typing import Optional

def params_marry_control() -> Optional[Params]:
        params = {
            "peer_id": 12412412,
            "man1" : 34634634634,
            "man2": 5475745754,
            "man1name": "asfasfas",
            "man2name": "bmldslmbldsmbdfs",
            "allow": 1,
            "await_state": 0
            }
        
        if params: return Params(**params)
        else: return Params(...)

a = params_marry_control() 
print(a.peer_id)"""

