import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database import queries
from keyboards.callbacks import SettingsCallback
from keyboards.inline import confirm_delete_keyboard, main_menu_keyboard, settings_keyboard
from utils.helpers import clean_instagram_username, is_valid_instagram_username
from utils.texts import Texts

logger = logging.getLogger(__name__)
router = Router(name="settings")


class SettingsStates(StatesGroup):
    waiting_for_new_instagram = State()


@router.message(Command("parametres"))
async def cmd_settings(message: Message, db_user: dict, **kwargs) -> None:
    if not db_user["is_registered"]:
        await message.answer(Texts.ERROR_NOT_REGISTERED, parse_mode="HTML")
        return
    await message.answer(Texts.SETTINGS_MENU, reply_markup=settings_keyboard(), parse_mode="HTML")


@router.callback_query(SettingsCallback.filter(lambda c: c.action == "change_ig"))
async def cb_change_ig(callback: CallbackQuery, state: FSMContext, **kwargs) -> None:
    await callback.answer()
    await callback.message.edit_text(Texts.SETTINGS_CHANGE_IG_PROMPT, parse_mode="HTML")
    await state.set_state(SettingsStates.waiting_for_new_instagram)


@router.message(SettingsStates.waiting_for_new_instagram, F.text)
async def process_new_ig(message: Message, state: FSMContext, db_user: dict, **kwargs) -> None:
    username = clean_instagram_username(message.text)

    if not is_valid_instagram_username(username):
        await message.answer(Texts.INSTAGRAM_INVALID_FORMAT, parse_mode="HTML")
        return

    existing = await queries.get_user_by_instagram_username(username)
    if existing and existing["id"] != db_user["id"]:
        await message.answer(Texts.INSTAGRAM_ALREADY_TAKEN, parse_mode="HTML")
        return

    await message.answer(
        Texts.INSTAGRAM_VERIFYING.format(username=username), parse_mode="HTML"
    )

    try:
        from services.instagram import ig_service

        ig_info = await ig_service.verify_account_exists(username)
    except Exception as e:
        logger.error(f"Instagram verification error: {e}")
        await message.answer(Texts.ERROR_INSTAGRAM_SERVICE, parse_mode="HTML")
        return

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

    await queries.update_instagram_info(
        user_id=db_user["id"],
        ig_username=ig_info["username"],
        ig_pk=str(ig_info["pk"]),
    )
    await state.clear()
    await message.answer(
        Texts.SETTINGS_IG_UPDATED.format(username=ig_info["username"]),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(SettingsCallback.filter(lambda c: c.action == "notifications"))
async def cb_notifications(callback: CallbackQuery, db_user: dict, **kwargs) -> None:
    await callback.answer()
    user = await queries.get_user_by_id(db_user["id"])
    if user is None:
        return
    new_enabled = not user["notifications_enabled"]
    await queries.update_notifications(db_user["id"], new_enabled)

    text = Texts.SETTINGS_NOTIFICATIONS_ON if new_enabled else Texts.SETTINGS_NOTIFICATIONS_OFF
    try:
        await callback.message.edit_text(text, reply_markup=settings_keyboard(), parse_mode="HTML")
    except Exception:
        pass


@router.callback_query(SettingsCallback.filter(lambda c: c.action == "delete"))
async def cb_delete(callback: CallbackQuery, **kwargs) -> None:
    await callback.answer()
    await callback.message.edit_text(
        Texts.SETTINGS_DELETE_CONFIRM,
        reply_markup=confirm_delete_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(SettingsCallback.filter(lambda c: c.action == "confirm_delete"))
async def cb_confirm_delete(callback: CallbackQuery, db_user: dict, state: FSMContext, **kwargs) -> None:
    await callback.answer()
    await queries.delete_user(db_user["id"])
    await state.clear()
    await callback.message.edit_text(Texts.SETTINGS_DELETED, parse_mode="HTML")


@router.callback_query(SettingsCallback.filter(lambda c: c.action == "cancel"))
async def cb_cancel_settings(callback: CallbackQuery, state: FSMContext, **kwargs) -> None:
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        Texts.SETTINGS_MENU, reply_markup=settings_keyboard(), parse_mode="HTML"
    )
