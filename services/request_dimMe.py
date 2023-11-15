
from hashlib import md5
import asyncio
import base64
import json,datetime
from aiohttp import ClientSession
from uuid import uuid4
from fake_useragent import UserAgent


userAgent = 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36'
#UserAgent().random
#"Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0"
#'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
url = 'https://ai.tu.qq.com/trpc.shadow_cv.ai_processor_cgi.AIProcessorCgi/Process'


protocol = 'http'
ip = '182.92.73.106'
port = '80'
pr = f'{protocol}://{ip}:{port}' 
#pr ='http://185.200.119.90:8443'

async def proxy_set():
       pass

async def sign_get(json_head)-> str:

       data = f'https://h5.tu.qq.com{str(len(json_head))}HQ31X02e'
       print(data)
       return md5(data.encode()).hexdigest()


async def post_image(image_bytes:bytes):
       different_dimension_me_img_entry = json.dumps({
          'busiId': 'ai_painting_anime_img_entry',#'',
          'extra': json.dumps({'version': 2,'platform': 'web',}),
          'images': [base64.b64encode(image_bytes).decode()]
          #'language':'en',
          #'data_report':json.dumps({'parent_trace_id':str(uuid4()),'root_channel':'qq_sousuo','level': 0})
          })
       with open('ddm.txt','w') as e : e.writelines(different_dimension_me_img_entry)
       sign = await sign_get(different_dimension_me_img_entry)
       print(sign)
       print(userAgent)
       headers = {
                     'x-sign-value': sign,
                     'x-sign-version': 'v1',
                     'Content-Type': 'application/json',
                     'Accept': 'application/json, text/plain, */*',
                     'Accept-Encoding': 'gzip, deflate, br',
                     "Sec-Fetch-Dest": "empty",
                     "Sec-Fetch-Mode": "no-cors",
                     "Sec-Fetch-Site": "same-site",
                     'Accept-Language': 'ru,uk-UA;q=0.8,uk;q=0.6,en-US;q=0.4,en;q=0.2',
                     'Host': 'ai.tu.qq.com',
                     'Origin': 'https://h5.tu.qq.com',
                     "Referer": "https://h5.tu.qq.com/",
                     'User-Agent': userAgent,
                     'platform':'web'
                 }
       
       async with ClientSession() as session:
              async with session.post(url, data=different_dimension_me_img_entry, headers=headers,proxy=pr) as response:
                     #print(await response.read())
                     r = await response.json()
                     with open('ddm1.txt','w') as e : e.writelines(r)
                     print(r)
                     s = r['extra']
                     ss = json.loads(s)
                     sa = ss['img_urls'][1]
                     print(sa)
                     ssss = await session.get(sa)
                     print(ssss)
              await session.close()
       return sa
                            #if response.status == 200:
                            #    with open('received_image.jpg', 'wb') as received_file:
                            #        received_image_data = await response.read()
                            #        received_file.write(received_image_data)
                            #    print('Изображение получено успешно')
                            #else:
                            #    print(f'Ошибка: {response.status}')
async def get_image(url):
       async with ClientSession() as session:
              print(await session.get(url))
              async with session.get(url) as f:
                     total = int(f.headers.get('content-length', 0))
                     print(total)
                     print(await f.read())


with open('services/1.jpg','rb') as f:
       aa = f.read()

u = asyncio.run(post_image(aa))
asyncio.run(get_image(u))

