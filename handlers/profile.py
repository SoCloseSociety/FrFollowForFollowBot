import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from database import queries
from keyboards.callbacks import MenuCallback
from keyboards.inline import back_to_menu_keyboard
from utils.helpers import format_datetime_fr
from utils.texts import Texts

logger = logging.getLogger(__name__)
router = Router(name="profile")


async def _send_profile(db_user: dict, send_func) -> None:
    try:
        if not db_user["is_registered"]:
            await send_func(Texts.ERROR_NOT_REGISTERED, parse_mode="HTML")
            return

        user = await queries.get_user_by_id(db_user["id"])
        if user is None:
            await send_func(Texts.ERROR_GENERIC, parse_mode="HTML")
            return

        achievements = await queries.get_user_achievements(db_user["id"])

        if achievements:
            badge_names = []
            for a in achievements:
                defn = Texts.ACHIEVEMENT_DEFINITIONS.get(a["achievement_type"])
                if defn:
                    badge_names.append(defn[0])
            badges_text = " | ".join(badge_names) if badge_names else Texts.NO_BADGES
        else:
            badges_text = Texts.NO_BADGES

        text = Texts.PROFILE.format(
            instagram=user["instagram_username"] or "—",
            level=user["level"],
            level_emoji=Texts.LEVEL_EMOJIS.get(user["level"], "🌱"),
            etoiles=user["etoiles"],
            given=user["total_follows_given"],
            received=user["total_follows_received"],
            streak=user["current_streak"],
            longest_streak=user["longest_streak"],
            since=format_datetime_fr(user["created_at"]),
            badges=badges_text,
        )

        await send_func(text, reply_markup=back_to_menu_keyboard(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Profile error: {e}", exc_info=True)
        try:
            await send_func(Texts.ERROR_GENERIC, parse_mode="HTML")
        except Exception:
            pass


@router.message(Command("profil"))
async def cmd_profile(message: Message, db_user: dict, **kwargs) -> None:
    await _send_profile(db_user, message.answer)


@router.callback_query(MenuCallback.filter(lambda c: c.action == "profile"))
async def cb_profile(callback: CallbackQuery, db_user: dict, **kwargs) -> None:
    await callback.answer()
    await _send_profile(db_user, callback.message.answer)
