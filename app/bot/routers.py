from aiogram import Router

from app.bot.handlers import admin_users, birthday_flow, channel_settings, prompts, ready_posts, start


def build_router() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(birthday_flow.router)
    router.include_router(ready_posts.router)
    router.include_router(admin_users.router)
    router.include_router(prompts.router)
    router.include_router(channel_settings.router)
    return router

