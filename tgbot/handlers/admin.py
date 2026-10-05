from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.admin import AdminFilter

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command("ban", "unban"))
async def ban_user(message: Message, command: CommandObject, repo: RequestsRepo):
    arg = command.args
    if not arg or not arg.isdigit():
        await message.reply("Введите id пользователя. /ban some_id")
        return

    user_id = int(arg)
    if user_id > 9223372036854775807:
        await message.reply("Слишком большой id.")
        return

    if command.command == "ban":
        changed = await repo.users.ban_user(user_id)
        await message.reply("Успешно забанен." if changed else "В боте нет такого пользователя.")
        return

    changed = await repo.users.unban_user(user_id)
    await message.reply("Успешно разбанен." if changed else "В боте нет такого пользователя.")


@admin_router.message(Command("bot"))
async def admin_stats(message: Message, repo: RequestsRepo):
    await message.reply(
        f"""Всего пользователей: {await repo.users.users_count()}
Из них активных: {await repo.users.users_count(only_active=True)}
Забаненных: {await repo.users.get_banned_users_count()}

Активность:
За день: {await repo.users.get_last_active_users_count_by_days(1)}
За неделю: {await repo.users.get_last_active_users_count_by_days(7)}
За месяц: {await repo.users.get_last_active_users_count_by_days(31)}
За год: {await repo.users.get_last_active_users_count_by_days(365)}

Новые пользователи:
За день: {await repo.users.get_new_users_count_by_days(1)}
За неделю: {await repo.users.get_new_users_count_by_days(7)}
За месяц: {await repo.users.get_new_users_count_by_days(31)}
За год: {await repo.users.get_new_users_count_by_days(365)}
"""
    )
