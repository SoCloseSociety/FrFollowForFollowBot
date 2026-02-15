import logging
from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from config import settings
from database import queries
from keyboards.callbacks import AutoModeCallback, MenuCallback
from keyboards.inline import auto_mode_keyboard, back_to_menu_keyboard
from services.gamification import award_etoiles
from utils.helpers import format_relative_time_fr, utcnow
from utils.texts import Texts

logger = logging.getLogger(__name__)
router = Router(name="auto_mode")


async def _send_auto_info(db_user: dict, send_func) -> None:
    try:
        if not db_user["is_registered"]:
            await send_func(Texts.ERROR_NOT_REGISTERED, parse_mode="HTML")
            return

        user = await queries.get_user_by_id(db_user["id"])
        if user is None:
            await send_func(Texts.ERROR_GENERIC, parse_mode="HTML")
            return

        # Check if already active
        if user["auto_mode_until"]:
            try:
                until = datetime.fromisoformat(user["auto_mode_until"])
                if until > utcnow():
                    await send_func(
                        Texts.AUTO_MODE_ALREADY_ACTIVE.format(
                            until=format_relative_time_fr(user["auto_mode_until"])
                        ),
                        reply_markup=back_to_menu_keyboard(),
                        parse_mode="HTML",
                    )
                    return
            except (ValueError, TypeError):
                pass

        text = Texts.AUTO_MODE_INFO.format(
            cost=settings.auto_mode_cost,
            current=user["etoiles"],
        )
        await send_func(text, reply_markup=auto_mode_keyboard(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Auto mode info error: {e}", exc_info=True)
        try:
            await send_func(Texts.ERROR_GENERIC, parse_mode="HTML")
        except Exception:
            pass


@router.message(Command("auto"))
async def cmd_auto(message: Message, db_user: dict, **kwargs) -> None:
    await _send_auto_info(db_user, message.answer)


@router.callback_query(MenuCallback.filter(lambda c: c.action == "auto"))
async def cb_auto_menu(callback: CallbackQuery, db_user: dict, **kwargs) -> None:
    await callback.answer()
    await _send_auto_info(db_user, callback.message.answer)


@router.callback_query(AutoModeCallback.filter(lambda c: c.action == "activate"))
async def cb_activate_auto(callback: CallbackQuery, db_user: dict, **kwargs) -> None:
    await callback.answer()

    try:
        user = await queries.get_user_by_id(db_user["id"])
        if user is None:
            await callback.message.edit_text(Texts.ERROR_GENERIC, parse_mode="HTML")
            return

        cost = settings.auto_mode_cost

        if user["etoiles"] < cost:
            await callback.message.edit_text(
                Texts.AUTO_MODE_NOT_ENOUGH.format(cost=cost, current=user["etoiles"]),
                parse_mode="HTML",
            )
            return

        # Deduct Etoiles
        await award_etoiles(db_user["id"], -cost, "auto_mode_purchase")

        # Set auto mode
        until = (utcnow() + timedelta(hours=settings.auto_mode_duration_hours)).isoformat()
        await queries.set_auto_mode(db_user["id"], until)

        # Grant achievement
        await queries.grant_achievement(db_user["id"], "auto_mode_first")

        await callback.message.edit_text(
            Texts.AUTO_MODE_ACTIVATED,
            reply_markup=back_to_menu_keyboard(),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Auto mode activate error: {e}", exc_info=True)
        try:
            await callback.message.edit_text(Texts.ERROR_GENERIC, parse_mode="HTML")
        except Exception:
            pass


@router.callback_query(AutoModeCallback.filter(lambda c: c.action == "cancel"))
async def cb_cancel_auto(callback: CallbackQuery, **kwargs) -> None:
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
