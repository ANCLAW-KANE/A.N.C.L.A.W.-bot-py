import asyncio
import os
import random
import time
from loguru import logger
import markovify
import textwrap
from images_editor.image_gen import Image_generator
from CONFIG import path_img
from enums import treb_mems


MAX_MSG_LENGTH = 4096

"""tag_pattern = re.compile(r"\[(id\d+?)\|.+?\]")
def clean_text(text: str) -> str:
    text = tag_pattern.sub(r"@\1", text) # Преобразование [id1|@d] в @id1
    return text.lower()"""


class Generator:

    def __init__(self,msg,obj=None):
        self.msg = msg
        self.obj = obj

    async def make_short_sent(self,text_model: markovify.NewlineText,size):
        return text_model.make_short_sentence(
            max_chars=size, tries=60
        )
    
    async def generate_text(self,size = MAX_MSG_LENGTH,state = 2,split = False) -> str:
        text = "\n".join(self.msg) if split == False else random.choices(self.msg,k=360)
        text_model = markovify.NewlineText(
            input_text=text, state_size=state, well_formed=False
        )
        return await self.make_short_sent(text_model,size) or random.choice(text)
    
    async def _async_generator(self,num,size,state):
        for _ in range(num):
            task = asyncio.create_task(self.generate_text(size,state,split=True))
            yield await task
    
    async def generate_text_list(self,num,size,state):
        start_time = time.time()
        strings = []
        g = self._async_generator(num,size,state)
        async for value in g: 
            strings.append(value)
        end_time = time.time()
        logger.warning(f"txts :gen: {end_time - start_time}")
        return strings
    
    async def generate_long_text(self,max_length=False,iter=4,state_size=2) -> str | None:
        if len(self.msg) < 500: return None
        text_models = [
            markovify.Text(
                state_size=state_size,
                input_text="\n".join(random.sample(self.msg, random.randint(350, 500))),
                well_formed=True
            ) for _ in range(iter)
        ]
        res = markovify.combine(text_models, [random.randint(1, 4) for _ in range(iter)])
        target_length = random.randint(3, 6) if not max_length else 50
        t = [res.make_short_sentence(max_chars=MAX_MSG_LENGTH ,min_words=10, max_words=100) for _ in range(target_length)]
        new_list = [i for i in t if i]
        long = ' '.join(new_list)
        width = random.randint(200 , 300) if not max_length else random.randint(600 , 800)
        return textwrap.shorten(long, width=width, placeholder="")
    
    async def _get_random_file(self,dir=None,num=1):
        dir_name = dir if dir else self.obj 
        f = os.listdir(f"{path_img}{dir_name}/")
        if f:
            files = random.sample(f,num)
            return [f"{path_img}{dir_name}/{i}" for i in files] if len(files) > 1 else f"{path_img}{dir_name}/{files[0]}"
    
    async def generate_demotivator(self):
        start_time = time.time()
        f = await self._get_random_file(num=random.randint(1,2))
        if f:
            texts = await self.generate_text_list(num=12,size=400,state=1)
            g = Image_generator(self.obj,f,texts)
            task = asyncio.create_task(g.gen())
            data = await task
            end_time = time.time()
            logger.warning(f"gd :gen: {end_time - start_time}")
            return data
        
    async def generate_big_demotivator(self,file_static=None,color = None,square=None,new_height=800):
        start_time = time.time()
        file = await self._get_random_file(num=random.randint(1,2)) if file_static == None\
            else [f"{path_img}{self.obj}/{file_static}"] 
        txt = await self.generate_long_text(max_length=True,iter=16)
        if not file or not txt:
            return None
        g = Image_generator(self.obj,file,txt)
        task = asyncio.create_task(g.big_gen(color=color,square=square,new_height=new_height))
        data = await task
        end_time = time.time()
        logger.warning(f"gdl :gen: {end_time - start_time}")
        return data
        
    async def gen_mem(self,dir='default'):
        start_time = time.time()
        f = await self._get_random_file(dir)
        g = Image_generator(self.obj,f)
        texts = await self.generate_text_list(num=2,size=200,state=1)
        task = asyncio.create_task(g.mem(texts,dir,treb_mems))
        data = await task
        end_time = time.time()
        logger.warning(f"gtr :gen: {end_time - start_time}")
        return data