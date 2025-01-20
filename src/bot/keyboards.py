from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from src.bot.bot_content import basics, skills


async def main_keyboard() -> ReplyKeyboardMarkup:
    kb_list = [
        [KeyboardButton(text=basics.Commands.get_question_text),
         KeyboardButton(text=basics.Commands.change_skills_text)],
        [KeyboardButton(text=basics.Commands.profile_text),
         KeyboardButton(text=basics.Commands.change_mode_text)],
        ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True)
    return keyboard


async def question_keyboard() -> ReplyKeyboardMarkup:
    kb_list = [
        [KeyboardButton(text=basics.Commands.another_question_text),
         KeyboardButton(text=basics.Commands.cancel_text)],
        ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True)
    return keyboard


async def get_answer_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=basics.Commands.get_answer_text,
                                      callback_data=basics.Commands.get_answer_command))
    return keyboard


async def get_subscribe_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=basics.Commands.get_subscribe_text,
                                      callback_data=basics.Commands.get_subscribe_command))
    return keyboard


async def cancel_keyboard() -> ReplyKeyboardMarkup:
    kb_list = [
        [KeyboardButton(text=basics.Commands.cancel_text)]]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True)
    return keyboard


async def skills_keyboard():
    skills_list = skills.Skills.get_all_skills()
    keyboard = InlineKeyboardMarkup()
    for skill in skills_list:
        keyboard.add(InlineKeyboardButton(text=skill().short_description, callback_data=skill().short_name))
    return keyboard


async def mode_keyboard():
    mode_dict = basics.Modes().model_dump()
    keyboard = InlineKeyboardMarkup()
    for skill_name, skill_value in mode_dict.items():
        keyboard.add(InlineKeyboardButton(text=skill_value, callback_data=skill_name))
    return keyboard


if __name__ == '__main__':
    import asyncio

    async def main():
        print(skills.Skills.get_all_skills())
        keyboard = await skills_keyboard()
        print(keyboard)

    asyncio.run(main())
