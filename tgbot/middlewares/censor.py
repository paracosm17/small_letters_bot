from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from infrastructure.database.repo.requests import RequestsRepo

BAD_WORDS = (
    "русня",
    "русорез",
    "москаль",
    "москали",
    "рашисты",
    "рашист",
    "путлер",
    "путинист",
    "рашка",
    "оккупанты",
    "московит",
    "москальчик",
    "москалев",
    "москалин",
    "москаленок",
    "москаленький",
    "москалька",
    "москальчиха",
    "москальша",
    "москальчище",
    "москальчишка",
    "москальчишко",
    "кремлебот",
    "кремлёбот",
    "кремлевский",
    "свинорус",
    "руснявый",
    "парашка",
    "русню",
    "русских",
    "москалей",
    "рашистов",
    "рашку",
    "рашки",
    "парашки",
    "руснявых",
    "кацап",
    "кафир",
    "кацапов",
    "орки",
    "орков",
    "орк ",
    "кацапы",
)


class CensorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if not event.text or event.from_user is None:
            return await handler(event, data)

        text = event.text.lower()
        if not any(word in text for word in BAD_WORDS):
            return await handler(event, data)

        repo: RequestsRepo = data["repo"]
        await event.reply(
            "<b>Вы подозреваетесь в русофобии и были заблокированы в боте!\n"
            "Если Вы считаете, что это ошибка - пишите в лс менеджеру @supremacismo</b>"
        )
        await repo.users.ban_user(event.from_user.id)
        return None
