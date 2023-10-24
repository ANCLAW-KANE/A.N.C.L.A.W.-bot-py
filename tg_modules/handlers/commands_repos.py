from database_module.peer_repo import PeerRepository
from tools import Patterns

class GenerateSettings:
    def __init__(self,chat,fromid=None) -> None:
        self.peerRepo = PeerRepository(chat,fromid)
        self.failure = f"Ошибка в аргументах! Не указан аргумент или он не является целым числом. Укажите шанс в диапазоне 0-100"

    async def _check_rule(self, args, n=1):
        return args and len(args) >= n and Patterns.pattern_bool(args[0], [Patterns.chance_pattern])

    async def _set_chance(self, args, method_name,desc = ''):
        if await self._check_rule(args):
            await getattr(self.peerRepo, method_name)(args[0])
            return f"{desc} с шансом {args[0]}"
        else:
            return self.failure

    async def set_gen(self, args):
        return await self._set_chance(args, "g_txt",'Генерация текста')

    async def set_dem(self, args):
        return await self._set_chance(args, "g_dem",'Генерация демотиватора')

    async def set_gdl(self, args):
        return await self._set_chance(args, "g_ldem",'Генерация большого дем.')

    async def set_stck(self, args):
        return await self._set_chance(args, "g_stck",'Отправка стикера')
       

    async def show(self):
        params = await self.peerRepo.get_params_peer()
        if params:
            return f"Шансы генерации :\n"\
                f" Текст - {params['g_txt']}\n"\
                f" Демотиватор - {params['g_dem']}\n"\
                f" Большой дем. - {params['g_ldem']}\n"\
                f" Стикеры - {params['g_stck']}\n"
            
    async def help(self):
        return f"Возможные настройки генерации:\n"\
            f"t - текст\n"\
            f"d - демотиватор\n"\
            f"dl - большой демотиватор\n"\
            f"stck - стикер\n"\
            f"show - показать все текущие настройки\n"\
            f"Пример: /gset t 1\n"
            
    
    