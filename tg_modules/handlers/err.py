import traceback
from aiogram import Router
from aiogram.types import ErrorEvent
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import ExceptionTypeFilter
from loguru import logger


router = Router()


@router.error(ExceptionTypeFilter(TelegramAPIError))
async def error_handler(event: TelegramAPIError):
    logger.error(f"Critical error caused by {event}")
    pass


@router.error()
async def error_handler(event: ErrorEvent):
    logger.error(f"Critical error caused by {event.exception}")
    traceback_str = traceback.format_exc()
    print(traceback_str)
    pass