from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from tgbot.config import Config


class AdminFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: TelegramObject, config: Config) -> bool:
        from_user = getattr(obj, "from_user", None)
        is_admin = from_user is not None and from_user.id in config.tg_bot.admin_ids
        return is_admin == self.is_admin
