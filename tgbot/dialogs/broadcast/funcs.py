import logging

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd.button import Button

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.dialogs.broadcast.states import BroadcastStates
from tgbot.filters.admin import AdminFilter
from tgbot.services.broadcaster import broadcast_by_copy
from tgbot.services.construct_markup import construct_markup
from tgbot.services.tasks import spawn

logger = logging.getLogger(__name__)

broadcast_router = Router()
broadcast_router.message.filter(AdminFilter())


@broadcast_router.message(Command("broadcast"))
async def start_broadcast(
    message: Message,
    dialog_manager: DialogManager,
    repo: RequestsRepo,
):
    await dialog_manager.start(
        BroadcastStates.count_state,
        data={"users_count": await repo.users.users_count(only_active=True)},
    )


async def count_input(message: Message, _: MessageInput, manager: DialogManager):
    repo: RequestsRepo = manager.middleware_data["repo"]
    active_users_count = await repo.users.users_count(only_active=True)

    if not message.text or not message.text.isdigit():
        return
    if int(message.text) > active_users_count:
        return

    manager.dialog_data["users_to_send_count"] = int(message.text)
    await manager.switch_to(BroadcastStates.random_or_last_state)


async def all_selected(_: CallbackQuery, __: Button, manager: DialogManager):
    repo: RequestsRepo = manager.middleware_data["repo"]
    manager.dialog_data["users_to_send_count"] = await repo.users.users_count(only_active=True)
    manager.dialog_data["random"] = False
    await manager.switch_to(BroadcastStates.message_state)


async def random_selected(_: CallbackQuery, __: Button, manager: DialogManager):
    manager.dialog_data["random"] = True
    await manager.switch_to(BroadcastStates.message_state)


async def last_selected(_: CallbackQuery, __: Button, manager: DialogManager):
    manager.dialog_data["random"] = False
    await manager.switch_to(BroadcastStates.message_state)


async def message_input(message: Message, _: MessageInput, manager: DialogManager):
    await message.bot.copy_message(
        chat_id=message.from_user.id,
        from_chat_id=message.from_user.id,
        message_id=message.message_id,
        reply_markup=message.reply_markup,
    )
    manager.dialog_data["message_for_send_id"] = message.message_id
    manager.dialog_data["message_for_send_reply_markup"] = (
        message.reply_markup.model_dump() if message.reply_markup else None
    )
    await manager.switch_to(BroadcastStates.apply_state)


async def _run_broadcast(
    callback: CallbackQuery,
    users: list[int],
    message_id: int,
    reply_markup,
) -> None:
    count = await broadcast_by_copy(
        callback.bot,
        users,
        callback.from_user.id,
        message_id,
        reply_markup,
    )
    await callback.bot.send_message(callback.from_user.id, f"{count} сообщений разослано!")


async def send_messages(callback: CallbackQuery, _: Button, manager: DialogManager):
    await callback.answer()
    await callback.message.answer("Запускаю рассылку в фоне...")

    repo: RequestsRepo = manager.middleware_data["repo"]
    users = list(
        await repo.users.get_active_users(
            manager.dialog_data["users_to_send_count"],
            random=manager.dialog_data.get("random", False),
        )
    )
    message_id = manager.dialog_data["message_for_send_id"]
    markup = construct_markup(manager.dialog_data["message_for_send_reply_markup"])

    spawn(
        _run_broadcast(callback, users, message_id, markup),
        name=f"broadcast-{callback.from_user.id}",
    )
    logger.info("Broadcast queued by admin=%s recipients=%d", callback.from_user.id, len(users))
    await manager.done()
