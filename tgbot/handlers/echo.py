from aiogram import types, Router, F
from aiogram.utils.markdown import hcode
from aiogram.fsm.context import FSMContext

echo_router = Router()


@echo_router.message(F.text)
async def bot_echo_all(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("---> /start <---")
