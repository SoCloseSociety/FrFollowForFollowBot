from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.callbacks import (
    AutoModeCallback,
    LeaderboardCallback,
    MenuCallback,
    MissionCallback,
    SettingsCallback,
    VerifyCallback,
)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Nouvelle Mission", callback_data=MenuCallback(action="mission").pack())
    builder.button(text="✅ Vérifier", callback_data=MenuCallback(action="verify").pack())
    builder.button(text="👤 Mon Profil", callback_data=MenuCallback(action="profile").pack())
    builder.button(text="🏆 Classement", callback_data=MenuCallback(action="leaderboard").pack())
    builder.button(text="🔗 Parrainage", callback_data=MenuCallback(action="referral").pack())
    builder.button(text="🚀 Mode Auto", callback_data=MenuCallback(action="auto").pack())
    builder.adjust(2)
    return builder.as_markup()


def mission_keyboard(batch_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ J'ai suivi ! Vérifier",
        callback_data=VerifyCallback(batch_id=batch_id).pack(),
    )
    builder.button(
        text="❌ Annuler la mission",
        callback_data=MissionCallback(action="cancel").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def auto_mode_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 Activer",
        callback_data=AutoModeCallback(action="activate").pack(),
    )
    builder.button(
        text="↩️ Retour",
        callback_data=AutoModeCallback(action="cancel").pack(),
    )
    builder.adjust(2)
    return builder.as_markup()


def leaderboard_keyboard(active: str = "etoiles") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    labels = {
        "etoiles": "⭐ Étoiles",
        "follows": "👥 Follows",
        "referrals": "🔗 Parrainages",
    }
    for key, label in labels.items():
        text = f"• {label} •" if key == active else label
        builder.button(text=text, callback_data=LeaderboardCallback(board_type=key).pack())
    builder.adjust(3)
    return builder.as_markup()


def settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📸 Changer Instagram",
        callback_data=SettingsCallback(action="change_ig").pack(),
    )
    builder.button(
        text="🔔 Notifications",
        callback_data=SettingsCallback(action="notifications").pack(),
    )
    builder.button(
        text="🗑 Supprimer mon compte",
        callback_data=SettingsCallback(action="delete").pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


def confirm_delete_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⚠️ Oui, supprimer",
        callback_data=SettingsCallback(action="confirm_delete").pack(),
    )
    builder.button(
        text="↩️ Annuler",
        callback_data=SettingsCallback(action="cancel").pack(),
    )
    builder.adjust(2)
    return builder.as_markup()


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="↩️ Menu principal", callback_data=MenuCallback(action="menu").pack())
    builder.adjust(1)
    return builder.as_markup()
