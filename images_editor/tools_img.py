
from PIL import Image, ImageDraw, ImageFont
import textwrap


async def draw_multiple_line_text(image: Image.Image, text, font: ImageFont.FreeTypeFont, text_color, 
                                  text_start_height,width_text,max_lines,stroke_width=None,stroke_fill=None):
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    line_spacing = 10
    y_text = text_start_height + line_spacing # начальная точка для текста
    lines = textwrap.wrap(text, width=width_text,max_lines=max_lines)
    for line in lines:
        font_size = font.size  # начальный размер шрифта
        while font_size > 0:
            font.size = font_size
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            if line_width <= image_width:
                draw.text(((image_width - line_width) / 2, y_text), line, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_fill)
                break
            """if font.size < 15:
                size = font.getlength(line)
                newline = textwrap.shorten(line,int(size))
                draw.text(((image_width - line_width) / 2, y_text), newline, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_fill)
                break"""
            font_size -= 1
        y_text += line_height + line_spacing


async def draw_multiple_line_text_in_textbox(image: Image.Image, text, font_size, text_color, xy, font):
    draw = ImageDraw.Draw(image)
    #размер текстового поля
    max_width = xy[1][0] - xy[0][0]
    max_height = xy[1][1] - xy[0][1]
    #размер шрифта
    base_font_size = font_size
    width_multiplier = max_width / base_font_size
    height_multiplier = max_height / base_font_size
    font_size = max(width_multiplier, height_multiplier)
    new_font = ImageFont.truetype(f"./fonts/{font}", int(font_size))
    #вычисление сетки текста по заданномму шрифту
    char_size = new_font.getbbox('x')
    char_width = char_size[2] - char_size[0]
    max_chars_per_line = max_width // char_width #макс длинна
                #   максимальное количество строк
    lines = textwrap.wrap(text, width=max_chars_per_line)
    line_spacing = 12 #отступы между строк
    text_height = 0
    for line in lines:
        text_box = new_font.getbbox(line)
        text_height += text_box[3] - text_box[1] + line_spacing
        if text_height <= max_height:###перепроверить
            break
        lines.pop()
    #отрисовка
    for i, line in enumerate(lines):
        line_height = i * (text_height / len(lines) + line_spacing) 
        draw.text((xy[0][0], xy[0][1] + line_height), line, font=new_font, fill=text_color)


async def resize_img(image: Image.Image ,new_height = 900,custom=False, ord= 1024):
    width, height = image.size
    if custom:
        new_width = width - int(width - ord + 100) # уменьшение ширины с учетом отступов (50 <> 50)
    else:
        new_width = int((width * new_height) / height)
    return (image.resize((new_width, new_height)),new_width)


async def multi_images(self,ord = 1024):
    if type(self.file) == list:
        imgs = []
        for img in self.file:
            image = Image.open(img)
            width, height = image.size
            if width > ord:#ширина вставляемого изображения больше середины исходного изображения
                resized_image = await resize_img(image,custom=True)
            else:
                resized_image = await resize_img(image)
            imgs.append(resized_image)
        return imgs
    else : 
        image = Image.open(self.file)
        return [await resize_img(image)]