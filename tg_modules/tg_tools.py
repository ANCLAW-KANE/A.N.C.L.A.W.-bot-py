from database_module.markov_repo import MarkovRepository
from markov.generators import Generator


async def get_max_photo_id(photos):
    ids = [idfile.file_id for idfile in photos]
    sizes = [size.file_size for size in photos]
    max_size = sorted(sizes)[-1]
    urldict = dict(zip(sizes, ids))
    return urldict.get(max_size)

async def get_data_markov(chat):
    mRepo = MarkovRepository(chat)
    return Generator(msg = await mRepo.get_history(),obj=chat)


