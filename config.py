from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Telegram
    telegram_bot_token: str = ""

    # Instagram
    instagram_username: str = ""
    instagram_password: str = ""
    instagram_proxy: str = ""

    # Database
    database_path: str = "data/bot.db"

    # Gamification
    etoiles_per_follow_given: int = 3
    etoiles_per_follow_received: int = 1
    etoiles_per_referral: int = 10
    etoiles_referral_first_mission: int = 5
    etoiles_daily_login: int = 2
    etoiles_streak_7_days: int = 15
    etoiles_welcome_bonus: int = 5
    auto_mode_cost: int = 50
    auto_mode_duration_hours: int = 24
    mission_size: int = 5

    # Rate limiting
    instagram_request_delay_min: int = 5
    instagram_request_delay_max: int = 15
    max_verifications_per_hour: int = 20

    # Admin
    admin_telegram_ids: str = ""

    @property
    def admin_ids(self) -> list[int]:
        if not self.admin_telegram_ids:
            return []
        return [int(x.strip()) for x in self.admin_telegram_ids.split(",") if x.strip()]


settings = Settings()
