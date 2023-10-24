from database_module.markov_repo import MarkovRepository
from markov.generators import Generator
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
        self.send_msg.msg = await g.generate_long_text()

    async def dgen(self):
        g = await self._data()
        photo = await g.generate_demotivator()
        upload = PhotoMessageUploader(vb.api)
        self.send_msg.attachment = await upload.upload(file_source=photo,peer_id = self.peer)

    async def dlgen(self):
        g = await self._data()
        photo = await g.generate_big_demotivator()
        upload = PhotoMessageUploader(vb.api)
        self.send_msg.attachment = await upload.upload(file_source=photo,peer_id = self.peer)
        
    async def check_g(self):
        gens = {
            None:self.gen,
            'l':self.lgen,
            'd':self.dgen,
            'dl':self.dlgen
        }
        key = gens.get(check_index(self.list_args,0))
        if key: await key()