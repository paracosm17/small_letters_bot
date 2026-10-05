import asyncio
import logging

from aiogram import Bot, exceptions

from infrastructure.database.repo.requests import RequestsRepo

logger = logging.getLogger(__name__)


async def send_chat_action(
    bot: Bot,
    user_id: int | str,
    repo: RequestsRepo,
) -> bool:
    try:
        await bot.send_chat_action(user_id, "typing")
        await repo.users.active_user(int(user_id), active=True)
    except exceptions.TelegramForbiddenError:
        logger.warning("Target [ID:%s]: forbidden", user_id)
        await repo.users.active_user(int(user_id), active=False)
    except exceptions.TelegramRetryAfter as exc:
        logger.warning("Target [ID:%s]: flood wait %s seconds", user_id, exc.retry_after)
        await asyncio.sleep(exc.retry_after)
        return await send_chat_action(bot, user_id, repo)
    except (exceptions.TelegramBadRequest, exceptions.TelegramAPIError) as exc:
        logger.warning("Target [ID:%s]: API error: %s", user_id, exc.message)
        await repo.users.active_user(int(user_id), active=False)
    else:
        return True
    return False


async def check_active_users(
    bot: Bot,
    users: list[int | str],
    repo: RequestsRepo,
) -> int:
    count = 0
    for user_id in users:
        if await send_chat_action(bot, user_id, repo):
            count += 1
        await asyncio.sleep(0.05)
    logger.info("%d users are active", count)
    return count
