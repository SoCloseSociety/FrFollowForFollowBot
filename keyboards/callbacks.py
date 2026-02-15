from aiogram.filters.callback_data import CallbackData


class MissionCallback(CallbackData, prefix="mission"):
    action: str  # "new", "cancel"


class VerifyCallback(CallbackData, prefix="verify"):
    batch_id: str


class AutoModeCallback(CallbackData, prefix="auto"):
    action: str  # "activate", "cancel"


class SettingsCallback(CallbackData, prefix="settings"):
    action: str  # "change_ig", "notifications", "delete", "confirm_delete", "cancel"


class LeaderboardCallback(CallbackData, prefix="lb"):
    board_type: str  # "etoiles", "follows", "referrals"


class MenuCallback(CallbackData, prefix="menu"):
    action: str  # "mission", "verify", "profile", "leaderboard", "referral", "auto"
