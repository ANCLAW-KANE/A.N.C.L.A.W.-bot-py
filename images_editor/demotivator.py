from PIL import Image, ImageDraw, ImageFont
import textwrap
from io import BytesIO


async def draw_multiple_line_text(image, text, font, text_color, text_start_height):
    draw = ImageDraw.Draw(image)
    image_width, _ = image.size
    y_text = text_start_height
    lines = textwrap.wrap(text, width=65,max_lines=4)
    for line in lines:
        bbox = font.getbbox(line)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        draw.text(
            ((image_width - line_width) / 2, y_text),
            line, font=font, fill=text_color)
        y_text += line_height


class Demotivator_generator:

    def __init__(self,peer,file,text=""):
        self.peer = peer
        self.text = text
        self.file = file
        
    async def gen(self):
        background = Image.new("RGB", (1024, 1024))
        image = Image.open(self.file).resize(size=(724, 724))
        background.paste(image, (150,150))
        font = ImageFont.truetype("./fonts/Lobster-Regular.ttf", size=30)
        await draw_multiple_line_text(background, self.text, font, (255, 255, 255), background.height - 145 )
        image_content = BytesIO()
        background.seek(0)
        background.save(image_content, format='JPEG')
        image_content.seek(0)
        return image_content.read()
