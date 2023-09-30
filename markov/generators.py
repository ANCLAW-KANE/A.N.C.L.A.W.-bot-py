import os
import random
import markovify
from images_editor.demotivator import Demotivator_generator
from CONFIG import path_img
MAX_MSG_LENGTH = 4096

"""tag_pattern = re.compile(r"\[(id\d+?)\|.+?\]")
def clean_text(text: str) -> str:
    text = tag_pattern.sub(r"@\1", text) # Преобразование [id1|@durov] в @id1
    return text.lower()"""

class Generator:

    def __init__(self,msg,obj=None):
        self.msg = msg
        self.obj = obj

    async def generate_text(self,size = MAX_MSG_LENGTH,state = 1) -> str:
        text_model = markovify.NewlineText(
            input_text="\n".join(self.msg), state_size=state, well_formed=False
        )
        return text_model.make_short_sentence(
            max_chars=size, tries=100
        ) or random.choice(self.msg)
    
    async def generate_long_text(self) -> str:
        r = random.sample(self.msg, random.randint(15, 100))
        text_models = []
        for _ in range(4): 
            text_model_long = markovify.Text(input_text="\n".join(r), well_formed=False)
            text_models.append(text_model_long)
        res = markovify.combine(text_models, [1, 2, 1, 2])
        t = []
        for _ in range(random.randint(3, 6)):
            if res:
                t.append(res.make_sentence(min_words=10, max_words=100))
            else:
                t.append(text_model_long.make_sentence(min_words=10, max_words=100))
        new_list = [i for i in t if i]
        if not new_list:
            return ' '.join(random.sample(self.msg, random.randint(6 , 10)))
        else:
            return ' '.join(new_list)
    
    async def _get_random_file(self): 
        f = os.listdir(f"{path_img}{self.obj}/")
        if f: return f"{path_img}{self.obj}/{random.choice(f)}"
    
    async def generate_demotivator(self):
        f = await self._get_random_file()
        if f: 
            g = Demotivator_generator(self.obj,f,await self.generate_text(size=400,state=2))
            return await g.gen()