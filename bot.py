import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import settings
from database.db import close_db, init_db
from handlers import main_router
from keyboards.callbacks import MenuCallback
from keyboards.inline import main_menu_keyboard
from middlewares.auth import AuthMiddleware
from services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot) -> None:
    """Set the bot commands menu in French."""
    commands = [
        BotCommand(command="start", description="Inscription / Accueil"),
        BotCommand(command="mission", description="Recevoir une nouvelle mission"),
        BotCommand(command="verifier", description="Vérifier tes follows"),
        BotCommand(command="profil", description="Voir ton profil et tes stats"),
        BotCommand(command="classement", description="Classement des joueurs"),
        BotCommand(command="parrainage", description="Lien de parrainage"),
        BotCommand(command="auto", description="Activer le mode automatique"),
        BotCommand(command="parametres", description="Paramètres"),
        BotCommand(command="aide", description="Aide"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    if not settings.telegram_bot_token or settings.telegram_bot_token.startswith("your-"):
        logger.error("TELEGRAM_BOT_TOKEN is not set in .env — cannot start bot.")
        sys.exit(1)

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Middleware
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Routers
    dp.include_router(main_router)

    # Menu callback handler (back to menu)
    @dp.callback_query(MenuCallback.filter(lambda c: c.action == "menu"))
    async def cb_back_to_menu(callback, db_user: dict, **kwargs):
        await callback.answer()
        try:
            from database import queries
            from utils.texts import Texts

            if db_user["is_registered"]:
                user = await queries.get_user_by_id(db_user["id"])
                if user is None:
                    await callback.message.edit_text(Texts.WELCOME, reply_markup=main_menu_keyboard())
                    return
                text = Texts.WELCOME_BACK.format(
                    username=user["instagram_username"] or "—",
                    etoiles=user["etoiles"],
                    level=user["level"],
                    level_emoji=Texts.LEVEL_EMOJIS.get(user["level"], "🌱"),
                    streak=user["current_streak"],
                )
            else:
                text = Texts.WELCOME
            await callback.message.edit_text(text, reply_markup=main_menu_keyboard())
        except Exception as e:
            logger.error(f"Menu callback error: {e}", exc_info=True)

    # Lifecycle
    async def on_startup() -> None:
        logger.info("Starting FollowBoost FR bot...")

        # Database init — MANDATORY
        try:
            await init_db()
            logger.info("Database initialized")
        except Exception as e:
            logger.critical(f"Database initialization failed: {e}", exc_info=True)
            sys.exit(1)

        # Instagram login (optional — bot works without it but verification is disabled)
        if settings.instagram_username and settings.instagram_password:
            try:
                from services.instagram import ig_service
                await ig_service.login()
                logger.info("Instagram service ready")
            except Exception as e:
                logger.error(f"Instagram login failed: {e}")
                logger.warning("Bot will start without Instagram verification — /verifier will be unavailable")
        else:
            logger.warning("Instagram credentials not set — verification disabled")

        start_scheduler()
        await set_bot_commands(bot)
        logger.info("FollowBoost FR bot started!")

    async def on_shutdown() -> None:
        logger.info("Shutting down...")
        stop_scheduler()
        await close_db()
        logger.info("Shutdown complete")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Starting polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
