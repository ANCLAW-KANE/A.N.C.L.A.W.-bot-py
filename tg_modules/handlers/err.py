import traceback
from aiogram import Router
from aiogram.types import ErrorEvent
from loguru import logger

router = Router()

@router.error()
async def error_handler(event: ErrorEvent):
    logger.error(f"Critical error caused by {event.exception}")
    traceback_str = traceback.format_exc()
    print(traceback_str)
    pass