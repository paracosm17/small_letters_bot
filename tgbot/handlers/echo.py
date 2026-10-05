from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

echo_router = Router()


@echo_router.message(F.text)
async def bot_echo_all(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("---> /start <---")
