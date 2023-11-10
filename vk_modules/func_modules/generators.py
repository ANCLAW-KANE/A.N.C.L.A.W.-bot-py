from database_module.markov_repo import MarkovRepository
from markov.generators import Generator
from markov.generator_settings_manager import GenerateSettings
from vkbottle import PhotoMessageUploader
from sessions_vk import vb
from tools import check_index


class Generate:
    def __init__(self) -> None:
        self.mRepo = MarkovRepository(self.peer)
    
    async def _data(self):
        data = await self.mRepo.get_history()
        return Generator(data,self.peer)
    
    async def gen(self):
        g = await self._data()
        self.send_msg.msg = await g.generate_text()

    async def lgen(self):
        g = await self._data()
        txt = await g.generate_long_text() 
        if not txt: txt = "Мало данных для генерации"
        self.send_msg.msg = txt

    async def dgen(self):
        g = await self._data()
        photo = await g.generate_demotivator()
        upload = PhotoMessageUploader(vb.api)
        self.send_msg.attachment = await upload.upload(file_source=photo,peer_id = self.peer)

    async def dlgen(self):
        g = await self._data()
        photo = await g.generate_big_demotivator(square=True)
        if not photo:
            self.send_msg.msg = "Мало данных для генерации "
            return
        upload = PhotoMessageUploader(vb.api)
        self.send_msg.attachment = await upload.upload(file_source=photo,peer_id = self.peer)
    
    async def settings(self):
        gen = GenerateSettings(self.peer,len_index=3,arg_index=2)
        g_set = {
            't': (gen.set_gen,(self.list_args,)),
            'd': (gen.set_dem,(self.list_args,)),
            'dl': (gen.set_gdl,(self.list_args,)),
            'stck': (gen.set_stck,(self.list_args,)),
            'show': (gen.show,()),
            None: (gen.help,())
        }
        key = g_set.get(check_index(self.list_args,1))
        if key is not None:
            text = await key[0](*key[1])
            self.send_msg.msg = text
    
    async def check_g(self):
        gens = {
            None:self.gen,
            'l':self.lgen,
            'd':self.dgen,
            'dl':self.dlgen,
            's': self.settings,
        }
        key = gens.get(check_index(self.list_args,0))
        if key: await key()
        