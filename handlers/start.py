import logging

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config import settings
from database import queries
from keyboards.inline import main_menu_keyboard
from services.gamification import award_etoiles, process_daily_checkin, process_referral_signup
from utils.helpers import clean_instagram_username, is_valid_instagram_username
from utils.texts import Texts

logger = logging.getLogger(__name__)
router = Router(name="start")


class RegistrationStates(StatesGroup):
    waiting_for_instagram = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db_user: dict, bot: Bot) -> None:
    try:
        # Parse referral code from deep link: /start ref_ABCD1234
        args = message.text.split(maxsplit=1)
        referral_code = None
        if len(args) > 1 and args[1].startswith("ref_"):
            referral_code = args[1][4:]

        if db_user["is_registered"]:
            await state.clear()
            checkin = await process_daily_checkin(db_user["id"])
            user = await queries.get_user_by_id(db_user["id"])
            if user is None:
                await message.answer(Texts.ERROR_GENERIC, parse_mode="HTML")
                return

            text = Texts.WELCOME_BACK.format(
                username=user["instagram_username"] or "—",
                etoiles=user["etoiles"],
                level=user["level"],
                level_emoji=Texts.LEVEL_EMOJIS.get(user["level"], "🌱"),
                streak=user["current_streak"],
            )

            if checkin is not None:
                text += "\n\n" + Texts.DAILY_CHECKIN.format(
                    etoiles=checkin["etoiles_awarded"],
                    streak=checkin["streak_count"],
                )
                if checkin.get("streak_bonus", 0) > 0:
                    text += "\n" + Texts.DAILY_CHECKIN_STREAK_BONUS.format(
                        days=checkin["streak_count"],
                        bonus=checkin["streak_bonus"],
                    )

            await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")
            return

        # New user - start registration
        if referral_code:
            await state.update_data(referral_code=referral_code)

        await message.answer(Texts.WELCOME, parse_mode="HTML")
        await state.set_state(RegistrationStates.waiting_for_instagram)

    except Exception as e:
        logger.error(f"Error in cmd_start: {e}", exc_info=True)
        await message.answer(Texts.ERROR_GENERIC, parse_mode="HTML")


@router.message(RegistrationStates.waiting_for_instagram, F.text)
async def process_instagram_username(
    message: Message, state: FSMContext, db_user: dict, bot: Bot
) -> None:
    try:
        username = clean_instagram_username(message.text)

        if not is_valid_instagram_username(username):
            await message.answer(Texts.INSTAGRAM_INVALID_FORMAT, parse_mode="HTML")
            return

        # Check if already taken
        existing = await queries.get_user_by_instagram_username(username)
        if existing and existing["id"] != db_user["id"]:
            await message.answer(Texts.INSTAGRAM_ALREADY_TAKEN, parse_mode="HTML")
            return

        # Verify on Instagram
        await message.answer(
            Texts.INSTAGRAM_VERIFYING.format(username=username), parse_mode="HTML"
        )

        try:
            from services.instagram import ig_service

            if not ig_service.is_available:
                await message.answer(Texts.ERROR_INSTAGRAM_SERVICE, parse_mode="HTML")
                return  # Stay in state so user can retry later

            ig_info = await ig_service.verify_account_exists(username)
        except Exception as e:
            logger.error(f"Instagram verification error: {e}")
            await message.answer(Texts.ERROR_INSTAGRAM_SERVICE, parse_mode="HTML")
            return  # Stay in state so user can retry

        if ig_info is None:
            await message.answer(
                Texts.INSTAGRAM_NOT_FOUND.format(username=username), parse_mode="HTML"
            )
            return

        if ig_info["is_private"]:
            await message.answer(
                Texts.INSTAGRAM_PRIVATE.format(username=username), parse_mode="HTML"
            )
            return

        # Register
        await queries.update_instagram_info(
            user_id=db_user["id"],
            ig_username=ig_info["username"],
            ig_pk=str(ig_info["pk"]),
        )

        # Welcome bonus
        bonus = settings.etoiles_welcome_bonus
        await award_etoiles(db_user["id"], bonus, "welcome_bonus")

        # Process referral
        fsm_data = await state.get_data()
        referral_code = fsm_data.get("referral_code")
        if referral_code:
            try:
                referrer = await queries.get_user_by_referral_code(referral_code)
                if referrer and referrer["id"] != db_user["id"]:
                    await process_referral_signup(referrer["id"], db_user["id"])
                    await message.answer(
                        Texts.REFERRAL_WELCOME_BONUS.format(bonus=settings.etoiles_per_referral),
                        parse_mode="HTML",
                    )
            except Exception as e:
                logger.error(f"Referral processing error: {e}")

        # Clear state AFTER everything succeeds
        await state.clear()

        await message.answer(
            Texts.INSTAGRAM_REGISTERED.format(username=ig_info["username"], bonus=bonus),
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )

    except Exception as e:
        logger.error(f"Error in process_instagram_username: {e}", exc_info=True)
        await message.answer(Texts.ERROR_GENERIC, parse_mode="HTML")
