from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import User
from infrastructure.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    async def update_or_create_user(
        self,
        user_id: int,
        full_name: str,
        language_code: str,
        username: str | None = None,
    ) -> User:
        now = datetime.now()
        statement = select(User).from_statement(
            insert(User)
            .values(
                user_id=user_id,
                username=username,
                full_name=full_name,
                language_code=language_code,
                active=True,
                last_active=now,
            )
            .returning(User)
            .on_conflict_do_update(
                index_elements=[User.user_id],
                set_={
                    "username": username,
                    "full_name": full_name,
                    "language_code": language_code,
                    "active": True,
                    "last_active": now,
                },
            )
        )
        result = await self.session.execute(statement)
        await self.session.commit()
        return result.scalar_one()

    async def ban_user(self, user_id: int) -> bool:
        user = await self.session.scalar(select(User).where(User.user_id == user_id))
        if user is None:
            return False
        user.banned = True
        await self.session.commit()
        return True

    async def unban_user(self, user_id: int) -> bool:
        user = await self.session.scalar(select(User).where(User.user_id == user_id))
        if user is None:
            return False
        user.banned = False
        await self.session.commit()
        return True

    async def active_user(self, user_id: int, active: bool) -> bool:
        user = await self.session.scalar(select(User).where(User.user_id == user_id))
        if user is None:
            return False
        user.active = active
        await self.session.commit()
        return True

    async def do_user_exists(self, user_id: int) -> bool:
        return (
            await self.session.scalar(select(User.user_id).where(User.user_id == user_id))
            is not None
        )

    async def users_count(self, only_active: bool = False) -> int:
        query = select(func.count()).select_from(User)
        if only_active:
            query = query.where(User.active.is_(True))
        return int((await self.session.execute(query)).scalar_one())

    async def get_active_users(self, count: int | None = None, random: bool = True) -> list[int]:
        query = select(User.user_id).where(User.active.is_(True))
        query = query.order_by(func.random() if random else User.created_at.desc())
        if count is not None:
            query = query.limit(count)
        users = await self.session.execute(query)
        return list(users.scalars().all())

    async def get_new_users_count_by_days(self, days: int) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(User)
            .where(func.date(User.created_at) > date.today() - timedelta(days=days))
        )
        return int(result.scalar_one())

    async def get_last_active_users_count_by_days(self, days: int) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(User)
            .where(func.date(User.last_active) > date.today() - timedelta(days=days))
        )
        return int(result.scalar_one())

    async def get_all_users_ids(self) -> list[int]:
        users = await self.session.execute(select(User.user_id))
        return list(users.scalars().all())

    async def get_banned_users_count(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.banned.is_(True))
        )
        return int(result.scalar_one())
