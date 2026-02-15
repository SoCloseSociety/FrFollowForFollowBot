from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.texts import Texts

router = Router(name="help")


@router.message(Command("aide"))
async def cmd_aide(message: Message, **kwargs) -> None:
    await message.answer(Texts.HELP, parse_mode="HTML")
