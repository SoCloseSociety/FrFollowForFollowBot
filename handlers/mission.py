import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from database import queries
from keyboards.callbacks import MenuCallback, MissionCallback
from keyboards.inline import main_menu_keyboard, mission_keyboard
from services.mission_engine import MissionEngine
from utils.texts import Texts

logger = logging.getLogger(__name__)
router = Router(name="mission")


async def _send_mission(target, db_user: dict, send_func) -> None:
    """Shared logic for sending a mission (command or callback)."""
    try:
        if not db_user["is_registered"]:
            await send_func(Texts.MISSION_NOT_REGISTERED, parse_mode="HTML")
            return

        # Check for active mission
        active = await queries.get_active_mission_batch(db_user["id"])
        if active:
            batch_id = active[0]["batch_id"]
            text = Texts.MISSION_ALREADY_ACTIVE + "\n\n"
            text += _format_mission(active, batch_id)
            await send_func(text, reply_markup=mission_keyboard(batch_id), parse_mode="HTML")
            return

        # Generate new mission
        result = await MissionEngine.generate_mission(db_user["id"])
        if result is None:
            await send_func(Texts.MISSION_NO_POOL, parse_mode="HTML")
            return

        targets, batch_id = result
        missions = await queries.get_missions_by_batch(batch_id)
        text = _format_mission(missions, batch_id)
        await send_func(text, reply_markup=mission_keyboard(batch_id), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Mission error: {e}", exc_info=True)
        try:
            await send_func(Texts.ERROR_GENERIC, parse_mode="HTML")
        except Exception:
            pass


def _format_mission(missions: list, batch_id: str) -> str:
    text = Texts.MISSION_HEADER.format(
        batch_num=batch_id[:4].upper(),
        count=len(missions),
    )
    for i, m in enumerate(missions, 1):
        status = "✅" if m["status"] == "verified" else f"{i}."
        text += f"  {status} 📸 <b>@{m['target_instagram_username']}</b>\n"
    text += Texts.MISSION_FOOTER
    return text


@router.message(Command("mission"))
async def cmd_mission(message: Message, db_user: dict, **kwargs) -> None:
    await _send_mission(message, db_user, message.answer)


@router.callback_query(MenuCallback.filter(lambda c: c.action == "mission"))
async def cb_mission(callback: CallbackQuery, db_user: dict, **kwargs) -> None:
    await callback.answer()
    await _send_mission(callback, db_user, callback.message.answer)


@router.callback_query(MissionCallback.filter(lambda c: c.action == "cancel"))
async def cb_cancel_mission(callback: CallbackQuery, db_user: dict, **kwargs) -> None:
    await callback.answer()
    try:
        active = await queries.get_active_mission_batch(db_user["id"])
        if active:
            for m in active:
                await queries.update_mission_status(m["id"], "expired")
        await callback.message.edit_text(
            "❌ Mission annulée.\nTape /mission pour une nouvelle mission.",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Cancel mission error: {e}", exc_info=True)
        try:
            await callback.message.edit_text(Texts.ERROR_GENERIC, parse_mode="HTML")
        except Exception:
            pass
