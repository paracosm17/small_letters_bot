from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def construct_markup(value: dict | None) -> InlineKeyboardMarkup | None:
    if value is None:
        return None

    for row in value["inline_keyboard"]:
        for index, button in enumerate(row):
            row[index] = InlineKeyboardButton.model_construct(**button)

    return InlineKeyboardMarkup.model_construct(**value)
