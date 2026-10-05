import html

from aiogram import F, Router
from aiogram.filters import KICKED, MEMBER, ChatMemberUpdatedFilter, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated, Message

from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.upwords import make
from tgbot.misc.states import UpWords

user_router = Router()


@user_router.message(Command("help", "start"))
async def user_start(message: Message, state: FSMContext):
    await message.reply(
        f"Привет, {html.escape(message.from_user.full_name)}!\n\n"
        "Этот бот позволяет написать маленький текст сверху над большим, например:\n"
        "оⷭтⷣлⷷиⷧчⷶнⷮаꙺя  мꙷыⷬсⷪлⷦьꙵ\n\n"
        "Иногда тебе может понадобится сделать такую надпись:\n"
        "красивая ⷧ ꙷ ⷩ ⷶ\n\n"
        "Вместо такой:\n"
        "кⷧрꙷаⷩсⷶивая\n\n"
        "Для этого поставь * после нижнего слова, тогда верхняя надпись сместится и будет после слова\n"
        "<i>нижняя фраза: красивая*\n"
        "верхняя фраза: луна</i>\n\n"
        "По любым вопросам обращайся сюда: @supremacismo"
    )
    await message.answer("Отправь текст, который будет снизу!")
    await state.clear()
    await state.set_state(UpWords.downtext)


@user_router.message(F.text, StateFilter(UpWords.downtext))
async def receive_downtext(message: Message, state: FSMContext):
    await state.set_data({"down": message.text})
    await message.reply("Теперь отправь текст который будет сверху")
    await state.set_state(UpWords.uptext)


@user_router.message(F.text, StateFilter(UpWords.uptext))
async def receive_uptext(message: Message, state: FSMContext):
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
