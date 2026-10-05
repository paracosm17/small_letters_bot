import html

from aiogram.filters import CommandStart, ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters import CommandStart, ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated
from aiogram.types import Message

from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.upwords import make
from tgbot.misc.states import UpWords

user_router = Router()


@user_router.message(Command("help", "start"))
async def user_start(message: Message, state: FSMContext):
    await message.reply(f"Привет, {html.escape(message.from_user.full_name)}!\n\n"
                        f"Этот бот позволяет написать маленький текст сверху над большим, например:\n"
                        f"оⷭтⷣлⷷиⷧчⷶнⷮаꙺя  мꙷыⷬсⷪлⷦьꙵ\n\n"
                        f"Иногда тебе может понадобится сделать такую надпись:\n"
                        f"красивая ⷧ ꙷ ⷩ ⷶ\n\n"
                        f"Вместо такой:\n"
                        f"кⷧрꙷаⷩсⷶивая\n\n"
                        f"Для этого поставь * после нижнего слова, тогда верхняя надпись сместится и будет после слова\n"
                        f"<i>нижняя фраза: красивая*\n"
                        f"верхняя фраза: луна</i>\n\n"
                        f"По любым вопросам обращайся сюда: @supremacismo")
    await message.answer("Отправь текст, который будет снизу!")
    await state.clear()
    await state.set_state(UpWords.downtext)


@user_router.message(F.text, StateFilter(UpWords.downtext))
async def user_start(message: Message, state: FSMContext):
    await state.set_data({"down": message.text})
    await message.reply(f"Теперь отправь текст который будет сверху")
    await state.set_state(UpWords.uptext)


@user_router.message(F.text, StateFilter(UpWords.uptext))
async def user_start(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.reply(make(data["down"], message.text))
    await message.answer("Отправь текст который будет снизу")
    await state.clear()
    await state.set_state(UpWords.downtext)


@user_router.message(Command("id"))
async def user_id(message: Message):
    await message.reply(f"<code>{message.from_user.id}</code>")


@user_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated, repo: RequestsRepo):
    await repo.users.active_user(event.from_user.id, active=False)


@user_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated, repo: RequestsRepo):
    await repo.users.active_user(event.from_user.id, active=True)
