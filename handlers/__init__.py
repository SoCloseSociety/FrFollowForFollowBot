from aiogram import Router

from .start import router as start_router
from .mission import router as mission_router
from .verify import router as verify_router
from .profile import router as profile_router
from .leaderboard import router as leaderboard_router
from .referral import router as referral_router
from .auto_mode import router as auto_mode_router
from .settings import router as settings_router
from .help import router as help_router
from .admin import router as admin_router

main_router = Router(name="main")
main_router.include_routers(
    start_router,
    mission_router,
    verify_router,
    profile_router,
    leaderboard_router,
    referral_router,
    auto_mode_router,
    settings_router,
    help_router,
    admin_router,
)
