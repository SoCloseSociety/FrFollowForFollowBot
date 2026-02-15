from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from database import queries
from utils.texts import Texts

logger = logging.getLogger(__name__)
router = Router(name="admin")


def _is_admin(telegram_id: int) -> bool:
    return telegram_id in settings.admin_ids


@router.message(Command("admin_stats"))
async def cmd_admin_stats(message: Message, db_user: dict, **kwargs) -> None:
    if not _is_admin(message.from_user.id):
        return

    try:
        total_users = await queries.get_total_users()
        active_missions = await queries.get_active_missions_count()
        total_follows = await queries.get_total_verified_follows()
        auto_users = await queries.get_active_auto_mode_users()

        text = Texts.ADMIN_STATS.format(
            total_users=total_users,
            active_missions=active_missions,
            total_follows=total_follows,
            auto_mode_count=len(auto_users),
        )
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Admin stats error: {e}", exc_info=True)
        await message.answer("Erreur lors de la recuperation des statistiques.", parse_mode="HTML")


@router.message(Command("admin_seed"))
async def cmd_admin_seed(message: Message, db_user: dict, **kwargs) -> None:
    """Add a seed Instagram account to the follow pool.
    Usage: /admin_seed username
    """
    if not _is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /admin_seed <instagram_username>", parse_mode="HTML")
        return

    username = parts[1].strip().lstrip("@")

    try:
        # Check if already exists
        existing = await queries.get_user_by_instagram_username(username)
        if existing:
            await message.answer(f"Le compte @{username} est deja dans le pool.", parse_mode="HTML")
            return

        # Verify on Instagram
        ig_info = None
        try:
            from services.instagram import ig_service

            if ig_service.is_available:
                ig_info = await ig_service.verify_account_exists(username)
                if ig_info is None:
                    await message.answer(Texts.ADMIN_SEED_FAIL, parse_mode="HTML")
                    return
                if ig_info["is_private"]:
                    await message.answer(f"Le compte @{username} est prive.", parse_mode="HTML")
                    return
        except Exception as e:
            logger.warning(f"Instagram check failed for seed, adding anyway: {e}")

        if ig_info is None:
            ig_info = {"pk": "0", "username": username}

        # Create a virtual user for this seed account
        from utils.helpers import generate_referral_code

        referral_code = generate_referral_code(0)
        seed_user_id = await queries.create_user(
            telegram_id=-abs(hash(username)) % 10**9,
            referral_code=referral_code,
        )
        await queries.update_instagram_info(
            user_id=seed_user_id,
            ig_username=ig_info["username"],
            ig_pk=str(ig_info["pk"]),
        )

        await message.answer(
            Texts.ADMIN_SEED_SUCCESS.format(username=ig_info["username"]),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Admin seed error: {e}", exc_info=True)
        await message.answer(f"Erreur: {e}", parse_mode="HTML")


@router.message(Command("admin_ban"))
async def cmd_admin_ban(message: Message, db_user: dict, **kwargs) -> None:
    """Ban/unban a user. Usage: /admin_ban <telegram_id>"""
    if not _is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /admin_ban <telegram_id>", parse_mode="HTML")
        return

    try:
        target_telegram_id = int(parts[1].strip())
    except ValueError:
        await message.answer("ID invalide.", parse_mode="HTML")
        return

    try:
        target = await queries.get_user_by_telegram_id(target_telegram_id)
        if not target:
            await message.answer("Utilisateur introuvable.", parse_mode="HTML")
            return

        if target["is_banned"]:
            await queries.set_user_banned(target["id"], False)
            await message.answer(Texts.ADMIN_UNBAN_SUCCESS, parse_mode="HTML")
        else:
            await queries.set_user_banned(target["id"], True)
            await message.answer(Texts.ADMIN_BAN_SUCCESS, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Admin ban error: {e}", exc_info=True)
        await message.answer(f"Erreur: {e}", parse_mode="HTML")
