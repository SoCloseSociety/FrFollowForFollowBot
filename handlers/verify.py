import os
from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from config import settings
from database import queries
from keyboards.callbacks import MenuCallback, VerifyCallback
from services.gamification import award_etoiles, process_referral_first_mission
from utils.helpers import utcnow
from utils.texts import Texts

logger = logging.getLogger(__name__)
router = Router(name="verify")

VERIFY_COOLDOWN_SECONDS = 60

async def _run_verification(db_user: dict, send_func, bot: Bot) -> None:
    """Core verification logic shared by command and callback."""
    try:
        if not db_user["is_registered"]:
            await send_func(Texts.MISSION_NOT_REGISTERED, parse_mode="HTML")
            return

        active = await queries.get_active_mission_batch(db_user["id"])
        if not active:
            await send_func(Texts.VERIFY_NO_ACTIVE_MISSION, parse_mode="HTML")
            return

        # Cooldown check
        user = await queries.get_user_by_id(db_user["id"])
        if user is None:
            await send_func(Texts.ERROR_GENERIC, parse_mode="HTML")
            return

        if user["last_verification_at"]:
            try:
                last_verify = datetime.fromisoformat(user["last_verification_at"])
                elapsed = (utcnow() - last_verify).total_seconds()
                if elapsed < VERIFY_COOLDOWN_SECONDS:
                    remaining = int(VERIFY_COOLDOWN_SECONDS - elapsed)
                    await send_func(
                        Texts.VERIFY_COOLDOWN.format(seconds=remaining), parse_mode="HTML"
                    )
                    return
            except (ValueError, TypeError):
                pass  # Invalid date format, continue

        # Check Instagram service availability
        from services.instagram import ig_service

        if not ig_service.is_available:
            await send_func(Texts.ERROR_INSTAGRAM_SERVICE, parse_mode="HTML")
            return

        # Send initial message
        status_msg = await send_func(Texts.VERIFY_STARTING, parse_mode="HTML")
        await queries.update_last_verification(db_user["id"])

        pending = [m for m in active if m["status"] == "pending"]
        total = len(pending)

        if total == 0:
            await send_func(
                "✅ Tous les follows de cette mission sont déjà vérifiés !\nTape /mission pour une nouvelle mission.",
                parse_mode="HTML",
            )
            return

        verified_count = 0
        missing_usernames = []
        follower_pk = user["instagram_user_pk"]

        if not follower_pk:
            await send_func(Texts.ERROR_GENERIC, parse_mode="HTML")
            return

        for i, mission in enumerate(pending, 1):
            # Update progress message
            try:
                if status_msg:
                    await status_msg.edit_text(
                        Texts.VERIFY_PROGRESS.format(current=i, total=total),
                        parse_mode="HTML",
                    )
            except Exception:
                pass  # Message edit can fail if too fast, non-critical

            try:
                is_following = await ig_service.check_follow(
                    follower_ig_pk=follower_pk,
                    target_username=mission["target_instagram_username"],
                )
            except Exception as e:
                logger.error(f"Verification error for @{mission['target_instagram_username']}: {e})
                missing_usernames.append(mission["target_instagram_username"])
                continue

            if is_following:
                verified_count += 1
                await queries.update_mission_status(mission["id"], "verified")

                # Record follow and award points
                if mission["target_user_id"]:
                    try:
                        await queries.record_follow(
                            follower_id=db_user["id"],
                            followed_id=mission["target_user_id"],
                            mission_id=mission["id"],
                        )
                        await queries.increment_follows_given(db_user["id"])
                        await queries.increment_follows_received(mission["target_user_id"])

                        # Award Etoiles to the followed user
                        await award_etoiles(
                            mission["target_user_id"],
                            settings.etoiles_per_follow_received,
                            "follow_received",
                        )

                        # Notify the followed user (non-blocking)
                        try:
                            followed_user = await queries.get_user_by_id(mission["target_user_id"])
                            if followed_user and followed_user.get("notifications_enabled"):
                                await bot.send_message(
                                    chat_id=followed_user["telegram_id"],
                                    text=Texts.NOTIFICATION_NEW_FOLLOWER,
                                    parse_mode="HTML",
                                )
                        except Exception as notify_err:
                            logger.debug(f"Notification send failed: {notify_err}")
                    except Exception as follow_err:
                        logger.error(f"Follow recording error: {follow_err}")
            else:
                missing_usernames.append(mission["target_instagram_username"])

        # Award Etoiles to the verifier
        etoiles_earned = 0
        if verified_count > 0:
            etoiles_earned = verified_count * settings.etoiles_per_follow_given
            await award_etoiles(db_user["id"], etoiles_earned, "follow_given")

            # Check for full batch completion using fresh DB data
            try:
                fresh_batch = await queries.get_missions_by_batch(active[0]["batch_id"])
                all_verified = all(m["status"] == "verified" for m in fresh_batch)
                if all_verified:
                    completed_count = await queries.get_completed_mission_count(db_user["id"])
                    if completed_count <= 1:
                        await process_referral_first_mission(db_user["id"])
            except Exception as e:
                logger.error(f"Mission completion check error: {e}")

        # Format response
        updated_user = await queries.get_user_by_id(db_user["id"])
        if updated_user is None:
            updated_user = user  # fallback

        if verified_count == total and not missing_usernames:
            text = Texts.VERIFY_SUCCESS_ALL.format(
                etoiles=etoiles_earned,
                total=updated_user["etoiles"],
                level=updated_user["level"],
                level_emoji=Texts.LEVEL_EMOJIS.get(updated_user["level"], "🌱"),
            )
        elif verified_count > 0:
            missing_text = \"
".join(f"  • @{u}" for u in missing_usernames)
            text = Texts.VERIFY_PARTIAL.format(
                verified=verified_count,
                total=total,
                missing=missing_text,
            )
        else:
            text = Texts.VERIFY_NONE

        try:
            if status_msg:
                await status_msg.edit_text(text, parse_mode="HTML")
            else:
                await send_func(text, parse_mode="HTML")
        except Exception:
            try:
                await send_func(text, parse_mode="HTML")
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Verification error: {e}", exc_info=True)
        try:
            await send_func(Texts.ERROR_GENERIC, parse_mode="HTML")
        except Exception:
            pass

@router.message(Command("verifier"))
async def cmd_verify(message: Message, db_user: dict, bot: Bot, **kwargs) -> None:
    await _run_verification(db_user, message.answer, bot)

@router.callback_query(MenuCallback.filter(lambda c: c.action == "verify"))
async def cb_verify_menu(callback: CallbackQuery, db_user: dict, bot: Bot, **kwargs) -> None:
    await callback.answer()
    await _run_verification(db_user, callback.message.answer, bot)

@router.callback_query(VerifyCallback.filter())
async def cb_verify_batch(
    callback: CallbackQuery, callback_data: VerifyCallback, db_user: dict, bot: Bot, **kwargs
) -> None:
    await callback.answer()
    await _run_verification(db_user, callback.message.answer, bot)
