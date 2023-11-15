from sqlalchemy import insert, select
from database_module.Tables import DBexec,hashDB,HashAudio

async def add_data_hash_audio(data):
    block_data = [HashAudio(md5hash=i['md5hash'],url=i['url'],name_audio=i['name_audio']) for i in data]
    await DBexec(hashDB,block_data).dbedit()

async def get_url(hash_md5: str):
    return await DBexec(hashDB,select(HashAudio.url,HashAudio.name_audio).where(HashAudio.md5hash == hash_md5)).dbselect(DBexec.FETCH_LINE)
