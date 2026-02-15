import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from config import settings
from database import queries
from keyboards.callbacks import MenuCallback
from keyboards.inline import back_to_menu_keyboard
from utils.texts import Texts

logger = logging.getLogger(__name__)
router = Router(name="referral")


async def _send_referral(db_user: dict, send_func, bot_username: str) -> None:
    try:
        if not db_user["is_registered"]:
            await send_func(Texts.ERROR_NOT_REGISTERED, parse_mode="HTML")
            return

        user = await queries.get_user_by_id(db_user["id"])
        if user is None:
            await send_func(Texts.ERROR_GENERIC, parse_mode="HTML")
            return

        stats = await queries.get_referral_stats(db_user["id"])

        link = f"https://t.me/{bot_username}?start=ref_{user['referral_code']}"

        text = Texts.REFERRAL_INFO.format(
            link=link,
            signup_bonus=settings.etoiles_per_referral,
            mission_bonus=settings.etoiles_referral_first_mission,
            count=stats["count"],
            earned=stats["earned"],
        )

        await send_func(text, reply_markup=back_to_menu_keyboard(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Referral error: {e}", exc_info=True)
        try:
            await send_func(Texts.ERROR_GENERIC, parse_mode="HTML")
        except Exception:
            pass


@router.message(Command("parrainage"))
async def cmd_referral(message: Message, db_user: dict, bot, **kwargs) -> None:
    me = await bot.get_me()
    await _send_referral(db_user, message.answer, me.username)


@router.callback_query(MenuCallback.filter(lambda c: c.action == "referral"))
async def cb_referral(callback: CallbackQuery, db_user: dict, bot, **kwargs) -> None:
    await callback.answer()
    me = await bot.get_me()
    await _send_referral(db_user, callback.message.answer, me.username)
