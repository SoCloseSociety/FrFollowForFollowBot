from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from database.queries import create_user, get_user_by_telegram_id, update_telegram_username
from utils.helpers import generate_referral_code
from utils.texts import Texts

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        telegram_user = data.get("event_from_user")
        if telegram_user is None:
            return await handler(event, data)

        user = await get_user_by_telegram_id(telegram_user.id)

        if user is None:
            referral_code = generate_referral_code(telegram_user.id)
            await create_user(
                telegram_id=telegram_user.id,
                referral_code=referral_code,
                telegram_username=telegram_user.username,
            )
            user = await get_user_by_telegram_id(telegram_user.id)
        elif telegram_user.username and user.get("telegram_username") != telegram_user.username:
            await update_telegram_username(user["id"], telegram_user.username)
            user["telegram_username"] = telegram_user.username

        # Block banned users
        if user and user.get("is_banned"):
            logger.info(f"Blocked banned user: telegram_id={telegram_user.id}")
            if isinstance(event, Message):
                await event.answer(Texts.ERROR_BANNED, parse_mode="HTML")
            elif isinstance(event, CallbackQuery):
                await event.answer(Texts.ERROR_BANNED, show_alert=True)
            return  # Stop processing

        data["db_user"] = user
        return await handler(event, data)
