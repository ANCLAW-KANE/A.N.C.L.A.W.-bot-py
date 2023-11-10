
from PIL import Image, ImageFont
import random
from io import BytesIO
from images_editor.tools_img import draw_multiple_line_text, multi_images,draw_multiple_line_text_in_textbox
from enums import ColorsRGB

white = ColorsRGB.default.white.value
black  = ColorsRGB.default.black.value
colors = list(ColorsRGB.Colors)

class Image_generator:

    def __init__(self, peer, file:str | list,text :str | None = None ):
        self.peer = peer
        self.text = text
        self.file = file

    async def read(self,obj:Image.Image):
        image_content = BytesIO()
        obj.seek(0)
        obj.save(image_content, format='JPEG')
        image_content.seek(0)
        return image_content.read()

    async def _one_line_dem(self,background_image:Image.Image,font: ImageFont.FreeTypeFont):
        text_y =  background_image.height - 145
        text_width = 50
        text_line = 4
        randColor = random.choice(colors).value
        await draw_multiple_line_text(background_image, random.choice(self.text), font, 
                    randColor, text_y, text_width, text_line)

    async def _two_line_dem(self,background_image:Image.Image,font: ImageFont.FreeTypeFont):
        first_text_y = background_image.height - 165
        first_text_width = 45
        first_text_line = 2
        second_text_y = background_image.height - 89
        second_text_width = 50
        second_text_line = 2
        await draw_multiple_line_text(background_image, random.choice(self.text), font, 
                                      random.choice(colors).value, 
                                      first_text_y, first_text_width, first_text_line)
        await draw_multiple_line_text(background_image, random.choice(self.text), font, 
                                      random.choice(colors).value, 
                                      second_text_y, second_text_width, second_text_line)
        
    async def _paste_img_big_gen(self,resized_image,set_y_height,step,background_image:Image.Image,max_width=2048,ord=1024):
        if len(resized_image) == 2 and (sum(image[1] for image in resized_image) < max_width):
            left_image, right_image = resized_image
            left_x = ord - step - left_image[1]
            right_x = ord + step
            background_image.paste(left_image[0], (left_x, set_y_height))
            background_image.paste(right_image[0], (right_x, set_y_height))
        else:
            res_image, width_image = resized_image[0]
            x = int((max_width - width_image) / 2)
            background_image.paste(res_image, (x, set_y_height))
    
    async def gen(self)->bytes:
        max_width = 1024 if isinstance(self.file, str) else 1678
        size = 25 if isinstance(self.file, str) else 31
        if isinstance(self.file,str):
            max_width = 1024
            size = 25
        if isinstance(self.file,list):
            max_width = 1678
            size = 31
        background = Image.new("RGB", (max_width, 1024))
        resized_image = await multi_images(self,ord=839, new_height=724, indent=60, square=True)
        await self._paste_img_big_gen(resized_image=resized_image, set_y_height=100, step=30,
                                    background_image=background, max_width=max_width, ord=839)
        r = random.randint(0,2)
        if not isinstance(self.file,list) or not r == 0:
            font = ImageFont.truetype("./fonts/better-vcr4.0.ttf", size=size)
            if r == 1 or r == 0:
                await self._one_line_dem(background,font)
            if r == 2:
                await self._two_line_dem(background,font)
        image = await self.read(background)
        return image

    async def big_gen(self,new_height,color=None,square=None)->bytes:
        background = Image.new("RGB", (2048, 2048))
        text_place_height = 950 # высота с которой начинается текст
        set_y_height = 70 #отступ от верхней границы фона
        step = 50 #отступ изображений от середины
        width_line = 55 # длина строки
        num_line = 16 # количество строк
        font = ImageFont.truetype("./fonts/better-vcr4.0.ttf", size=45)
        text_y = background.height - (background.height - text_place_height - set_y_height) # с учетом отступа и изображения
        resized_image = await multi_images(self,new_height = new_height ,ord= 1024, indent = 100,square=square)
        color_text = color if color else random.choice(colors).value
        await self._paste_img_big_gen(resized_image=resized_image,set_y_height=set_y_height,step=step,background_image=background)
        await draw_multiple_line_text(background, self.text, font,color_text , text_y, width_line, num_line)
        image = await self.read(background)
        return image
    
    async def mem(self,texts,theme='default',arr=None)-> bytes:
        ff = self.file.replace(f'./images_editor/images/{theme}/','')
        num_text_box = arr.get(ff)
        image = Image.open(self.file)
        font_size = 10
        font = 'roboto-medium.ttf'
        for i in range(len(num_text_box)):
            await draw_multiple_line_text_in_textbox(image,texts[i],font_size , black,num_text_box[i],font)
        img = await self.read(image)
        return img

