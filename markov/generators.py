from asyncio import create_task, get_event_loop
from os import listdir
import random
from time import time
from loguru import logger
from markovify import NewlineText, Text, combine
from textwrap import shorten
from images_editor.image_gen import Image_generator
from CONFIG import path_img
from enums import treb_mems
from database_module.peer_repo import PeerRepository

MAX_MSG_LENGTH = 4096



class Generator:
    def __init__(self, msg, obj=None):
        self.msg = msg
        self.obj = obj

    
    def make_short_sent(self, text_model: NewlineText, size):
        return text_model.make_short_sentence(max_chars=size, tries=60)

    def _gen_model_(self,text:str,state:int):
        return Text(
                input_text=text, state_size=state, well_formed=False,retain_original=False
            )

    async def generate_text(self, size=MAX_MSG_LENGTH, state=1, split=False,custom=False) -> str:
        if custom:
            state = (await PeerRepository(self.obj).get_params_peer())['g_text_state']
        len_data = len(self.msg)
        text = "\n".join(random.choices(self.msg, k=3000 
                if len_data > 3000 
                else len_data)
            ) if not split else random.choices(self.msg, k=360)
        start_time = time()
        loop = get_event_loop()
        text_model = loop.run_in_executor(None,self._gen_model_,text,state)
        end_time = time()
        result = loop.run_in_executor(None,self.make_short_sent,await text_model, size)
        logger.warning(f"gen text model {end_time - start_time}")
        return await result or random.choice(text)
    
    
    async def _async_generator(self, num, size, state):
        for _ in range(num):
            task = create_task(self.generate_text(size, state, split=True))
            yield await task
        

    
    async def generate_text_list(self, num, size, state):
        start_time = time()
        strings = []
        g = self._async_generator(num, size, state)
        async for value in g:
            strings.append(value)
        end_time = time()
        logger.warning(f"txts :gen: {end_time - start_time}")
        
        return strings

    
    async def generate_long_text(
        self, max_length=False, iter=4, state_size= 1,custom = False
    ) -> str | None:
        if len(self.msg) < 500:
            return None
        if custom:
            state_size = (await PeerRepository(self.obj).get_params_peer())['g_long_text_state']
        text_models = [
            Text(
                state_size=state_size,
                input_text="\n".join(random.sample(self.msg, random.randint(350, 500))),
                well_formed=True,
                retain_original=False
            )
            for _ in range(iter)
        ]
        res = combine(
            text_models, [random.randint(1, 4) for _ in range(iter)]
        )
        target_length = random.randint(3, 6) if not max_length else 50
        t = [
            res.make_short_sentence(
                max_chars=MAX_MSG_LENGTH, min_words=10, max_words=100
            )
            for _ in range(target_length)
        ]
        new_list = [i for i in t if i]
        long = " ".join(new_list)
        width = random.randint(200, 300) if not max_length else random.randint(600, 800)
        
        return shorten(long, width=width, placeholder="")

    
    async def _get_random_file(self, dir=None, num=1):
        dir_name = dir if dir else self.obj
        f = listdir(f"{path_img}{dir_name}/")
        if f:
            files = random.sample(f, num)
            
            return (
                [f"{path_img}{dir_name}/{i}" for i in files]
                if len(files) > 1
                else f"{path_img}{dir_name}/{files[0]}"
            )

    
    async def generate_demotivator(self):
        start_time = time()
        f = await self._get_random_file(num=random.randint(1, 2))
        if f:
            texts = await self.generate_text_list(num=6, size=400, state=1)
            g = Image_generator(self.obj, f, texts)
            task = create_task(g.gen())
            data = await task
            end_time = time()
            logger.warning(f"gd :gen: {end_time - start_time}")
            return data

    
    async def generate_big_demotivator(
        self, file_static=None, color=None, square=None, new_height=800
    ):
        start_time = time()
        file = (
            await self._get_random_file(num=random.randint(1, 2))
            if file_static == None
            else [f"{path_img}{self.obj}/{file_static}"]
        )
        txt = await self.generate_long_text(max_length=True, iter=8)
        if not file or not txt:
            return None
        g = Image_generator(self.obj, file, txt)
        task = create_task(
            g.big_gen(color=color, square=square, new_height=new_height)
        )
        data = await task
        end_time = time()
        logger.warning(f"gdl :gen: {end_time - start_time}")
        
        return data

    
    async def gen_mem(self, dir="default"):
        start_time = time()
        f = await self._get_random_file(dir)
        g = Image_generator(self.obj, f)
        texts = await self.generate_text_list(num=2, size=200, state=1)
        task = create_task(g.mem(texts, dir, treb_mems))
        data = await task
        end_time = time()
        logger.warning(f"gtr :gen: {end_time - start_time}")
        
        return data
