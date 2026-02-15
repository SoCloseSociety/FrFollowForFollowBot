import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from database import queries
from keyboards.callbacks import LeaderboardCallback, MenuCallback
from keyboards.inline import leaderboard_keyboard
from utils.texts import Texts

logger = logging.getLogger(__name__)
router = Router(name="leaderboard")


async def _format_leaderboard(board_type: str, db_user: dict) -> str:
    board_labels = {
        "etoiles": "Étoiles ⭐",
        "follows": "Follows 👥",
        "referrals": "Parrainages 🔗",
    }

    if board_type == "etoiles":
        rows = await queries.get_etoiles_leaderboard()
        value_key = "etoiles"
        value_suffix = " ⭐"
    elif board_type == "follows":
        rows = await queries.get_follows_leaderboard()
        value_key = "total_follows_given"
        value_suffix = " follows"
    else:
        rows = await queries.get_referral_leaderboard()
        value_key = "referral_count"
        value_suffix = " filleuls"

    text = Texts.LEADERBOARD_HEADER.format(board_type=board_labels.get(board_type, board_type))

    if not rows:
        text += Texts.LEADERBOARD_EMPTY
        return text

    for i, row in enumerate(rows, 1):
        medal = Texts.MEDALS.get(i, "  ")
        username = row.get("instagram_username") or row.get("telegram_username") or "Anonyme"
        value = row.get(value_key, 0)
        text += Texts.LEADERBOARD_ROW.format(
            medal=medal,
            rank=i,
            username=username,
            value=f"{value}{value_suffix}",
        )

    # User's own rank
    if board_type == "etoiles":
        rank = await queries.get_user_rank(db_user["id"])
        text += Texts.LEADERBOARD_YOUR_RANK.format(rank=rank)

    return text


@router.message(Command("classement"))
async def cmd_leaderboard(message: Message, db_user: dict, **kwargs) -> None:
    try:
        text = await _format_leaderboard("etoiles", db_user)
        await message.answer(
            text, reply_markup=leaderboard_keyboard("etoiles"), parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Leaderboard error: {e}", exc_info=True)
        await message.answer(Texts.ERROR_GENERIC, parse_mode="HTML")


@router.callback_query(MenuCallback.filter(lambda c: c.action == "leaderboard"))
async def cb_leaderboard_menu(callback: CallbackQuery, db_user: dict, **kwargs) -> None:
    await callback.answer()
    try:
        text = await _format_leaderboard("etoiles", db_user)
        await callback.message.answer(
            text, reply_markup=leaderboard_keyboard("etoiles"), parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Leaderboard menu error: {e}", exc_info=True)
        try:
            await callback.message.answer(Texts.ERROR_GENERIC, parse_mode="HTML")
        except Exception:
            pass


@router.callback_query(LeaderboardCallback.filter())
async def cb_leaderboard_switch(
    callback: CallbackQuery, callback_data: LeaderboardCallback, db_user: dict, **kwargs
) -> None:
    await callback.answer()
    try:
        text = await _format_leaderboard(callback_data.board_type, db_user)
        await callback.message.edit_text(
            text,
            reply_markup=leaderboard_keyboard(callback_data.board_type),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Leaderboard switch error: {e}", exc_info=True)
