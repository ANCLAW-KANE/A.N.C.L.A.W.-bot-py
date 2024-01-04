from database_module.peer_repo import PeerRepository
from tools import Patterns

class GenerateSettings:
    def __init__(self,chat,fromid=None,arg_index=0,len_index=1) -> None:
        self.peerRepo = PeerRepository(chat,fromid)
        self.failure = "Ошибка в аргументах! Не указан аргумент или он не является целым числом. Укажите шанс в диапазоне 0-100"
        self.param_chance = arg_index
        self.len_index = len_index

    async def _check_rule(self, args):
        return args and len(args) >= self.len_index and Patterns.pattern_bool(args[self.param_chance], [Patterns.chance_pattern])

    async def _set_chance(self, args, method_name,desc = ''):
        if await self._check_rule(args):
            await getattr(self.peerRepo, method_name)(args[self.param_chance])
            return f"{desc} с значением {args[self.param_chance]}"
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
    
    async def set_state(self, args):
        return await self._set_chance(args, "g_text_state",'Калибровка для генерации текста')
    
    async def set_lstate(self, args):
        return await self._set_chance(args, "g_long_text_state",'Калибровка для генерации длинного текста')   

    async def show(self):
        params = await self.peerRepo.get_params_peer()
        if params:
            return f"Шансы генерации :\n"\
                f" Текст - {params['g_txt']}\n"\
                f" Демотиватор - {params['g_dem']}\n"\
                f" Большой дем. - {params['g_ldem']}\n"\
                f" Стикеры - {params['g_stck']}\n"\
                f" Элементов в цепи для текста - {params['g_text_state']}\n"\
                f" Элементов в цепи для длинного текста - {params['g_long_text_state']}\n"\
            
    async def help(self):
        return "Возможные настройки генерации:\n"\
            "t - текст\n"\
            "d - демотиватор\n"\
            "dl - большой демотиватор\n"\
            "stck - стикер\n"\
            "show - показать все текущие настройки\n"\
            "state - Калибровка для генерации текста\n"\
            "lstate - Калибровка для генерации длинного текста\n"\
            "Пример: /gset t 1\n"
            
    
    