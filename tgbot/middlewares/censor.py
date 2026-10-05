from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from infrastructure.database.models.users import User
from infrastructure.database.repo.requests import RequestsRepo


class CensorMiddleware(BaseMiddleware):
    def __init__(self):
        pass

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        repo: RequestsRepo = data["repo"]
        bad_words = ["русня", "русорез", "москаль", "москали", "рашисты", "рашист", "путлер", "путинист", "рашка",
                     "оккупанты", "московит", "москальчик", "москалев", "москалин", "москаленок", "москаленький",
                     "москалька", "москальчиха", "москальша", "москальчик", "москальчище", "москальчишка",
                     "москальчишко", "кремлебот", "кремлёбот", "кремлевский", "свинорус", "руснявый", "парашка",
                     "русню", "русских", "москалей", "рашистов", "рашку", "рашки", "парашки", "руснявых",
                     "кацап", "кафир", "кацапов", "орки", "орков", "орк ", "кацапы"]
        for word in bad_words:
            if word in event.text.lower():
                await event.reply("<b>Вы подозреваетесь в русофобии и были заблокированы в боте!\n"
                                  "Если Вы считаете, что это ошибка - пишите в лс менеджеру @supremacismo</b>")
                await repo.users.ban_user(event.from_user.id)
                return

        return await handler(event, data)
