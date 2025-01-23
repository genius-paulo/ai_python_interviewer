import io
from loguru import logger
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram.types.message import ContentType

from src.bot.states import Form, PaymentStates
from src.giga_chat.models import MiddlePythonInterviewerChat
from src.giga_chat import giga_chat
from src.bot.keyboards import (main_keyboard,
                               question_keyboard,
                               get_answer_keyboard,
                               skills_keyboard,
                               mode_keyboard,
                               cancel_keyboard)
from src.bot.bot_content.basics import Commands
from src.bot.bot_content.skills import Skills
from src.bot.bot_content.texts import actual_texts

from aiogram.utils.markdown import hspoiler
from src.bot import keyboards
from src.config import settings

from src.db import db
from src.bot import utils
from src.db.cache.cache import cache

# TODO: Нужно разделить функции в хэнделерах по категориям и вынести,
#  сейчас они все намешаны здесь, их тяжело читать и поддерживать

async def start(message: types.Message, state: FSMContext):
    """Отправляем стартовое сообщение"""
    await state.finish()  # на всякий случай заканчивай все состояния
    logger.info(f'Пользователь {message.from_user.id} запустил бота.')

    await db.create_user(message.from_user.id)
    logger.info(f'Пользователь c Telegram ID {message.from_user.id} создан')

    final_text = actual_texts.greeting.format(user_id=message.from_user.first_name) + actual_texts.all_commands
    await message.answer(text=final_text, reply_markup=await main_keyboard())


async def cancel(message: types.Message, state: FSMContext):
    """Отменяем состояние"""
    logger.info('Отменяем состояние')

    final_text = actual_texts.cancel_all + actual_texts.all_commands
    await message.answer(text=final_text, reply_markup=await main_keyboard())

    await state.finish()


async def get_question(message: types.Message, state: FSMContext):
    """Получаем вопрос от ИИ и передаем пользователю"""

    # Получаем пользователя из базы и получаем объект его скилла
    user = await db.get_user(tg_id=message.from_user.id)
    user_skill_obj = await utils.get_skill_by_category(user)
    user_skill_score = getattr(user, user_skill_obj.short_name)
    user_is_paid = await db.check_paid_status(user)

    """Создаем объект истории чата и сохраняем в нем:
    1. Навык в зависимости от режима.
    2. Старую оценку.
    3. Вопрос пользователю в зависимости от навыка.
    """
    history_chat = MiddlePythonInterviewerChat(
        user_is_paid=user_is_paid,
        skill=user_skill_obj,
        score=user_skill_score,
        # TODO: Пока что задаем рандомный вопрос,
        #  желательно сделать так, чтобы вопросы не повторялись
        question=user_skill_obj.get_random_question())

    logger.info(f'Создали историю чата для пользователя {message.from_user.username} ({message.from_user.id}): {history_chat.model_dump()}')

    # Передаем объект истории в состояние
    async with state.proxy() as data:
        data['history_chat'] = history_chat
        # Отправляем вопрос пользователю
        await message.reply(text=actual_texts.get_question_skill.format(skill=history_chat.skill.short_description),
                            reply_markup=await question_keyboard())
        await message.bot.send_message(chat_id=message.from_user.id,
                                       text=f'*{actual_texts.get_question_ai_question}*'.format(
                                           ai_question=history_chat.question),
                                       reply_markup=await get_answer_keyboard(),
                                       parse_mode=types.ParseMode.MARKDOWN)
        # Устанавливаем состояние вопроса
        await Form.question.set()


async def get_answer_the_question(callback_query: types.CallbackQuery, state: FSMContext):
    """Дополняем сообщение ответом"""
    logger.info(f'Дополняем сообщение ответом для пользователя '
                f'{callback_query.from_user.username} ({callback_query.from_user.id}).')
    # Получаем пользователя из history_chat
    async with (state.proxy() as data):
        history_chat = data['history_chat']
        user_is_paid = history_chat.user_is_paid

        process_text = f'<b>{callback_query.message.text}</b>' + '\n\nГенерирую ответ...'
        await callback_query.message.edit_text(text=process_text,
                                               parse_mode=types.ParseMode.HTML,
                                               reply_markup=types.InlineKeyboardMarkup())

        logger.debug(f'Пользователь {callback_query.from_user.username} '
                     f'({callback_query.from_user.id}) хочет платную подсказку. '
                     f'У него есть подписка? {user_is_paid}')
        # меняем сообщение в зависимости от статуса подписки
        await get_paid_hint(callback_query, user_is_paid)


async def recreate_question(message: types.Message, state: FSMContext):
    """Пересоздаем вопрос"""
    logger.info(f'Пересоздаем вопрос '
                f'для пользователя {message.from_user.username} ({message.from_user.id})')
    await state.finish()
    await get_question(message, state)


async def process_question(message: types.Message, state: FSMContext):
    """Обрабатываем ответ на вопрос"""
    # Получаем объект истории чата
    async with (state.proxy() as data):
        try:
            history_chat = data['history_chat']

            # Дополняем промпт ответом пользователя
            history_chat.answer = message.text
            logger.info(f'Пользователь {message.from_user.username} ({message.from_user.id}) ответил: '
                        f'{history_chat.answer} на вопрос ИИ: {history_chat.question}')
            final_prompt = history_chat.get_final_prompt()
            logger.info(f'Получили финальный промпт для пользователя '
                        f'{message.from_user.username} ({message.from_user.id})')

            # Получаем оценку ответа от нейросети
            # TODO: Функция иногда отдает ошибку,
            #  тогда юзер получает понижение, нужно исправить
            ai_answer = await giga_chat.get_assessment_of_answer(final_prompt)
            # Рассчитываем экспоненциальное сглаживание,
            # получаем финальную оценку, чтобы именно ее вставить в базу
            ai_answer_score = utils.parse_score_from_ai_answer(ai_answer)
            logger.info(f'Получили оценку от нейросети: {ai_answer_score}')
            expo_score = utils.get_new_skill_rating(current_rating=history_chat.score,
                                                    new_score=ai_answer_score)
            # Забиваем оценку в базу
            await db.update_skill_rating(tg_id=message.from_user.id,
                                         skill=history_chat.skill.short_name,
                                         rating=expo_score)

            # Отсылаем стикер в зависимости от оценки
            await message.answer_sticker(sticker=utils.get_sticker_by_score(ai_answer_score))

            # Создаем финальное сообщение с изменением оценки
            final_text = actual_texts.ai_answer.format(ai_answer=ai_answer,
                                                       old_score=history_chat.score,
                                                       new_score=expo_score)
            await message.answer(final_text, reply_markup=await main_keyboard())
            # Завершаем состояния
            await state.finish()

        except Exception as e:
            logger.error(f'Ошибка при получении оценки от нейросети: {e}. Берем среднюю оценку, чтобы не портить результат.')
            # Отсылаем стикер в зависимости от оценки:
            # маленькая — грустный, большая — веселый
            await message.answer_sticker(sticker=utils.basics.Stickers().get_confused_sticker())
            final_text = ('Ответ сбил с толку AI-интервьюера. Он все обдумает и вернется позже.'
                          '\n\nА пока попробуй сгенерировать новый вопрос :)')
            await message.answer(final_text, reply_markup=await main_keyboard())
            # Завершаем состояния
            await state.finish()
            raise e


async def start_payment(message: types.Message, state: FSMContext):
    """Начинаем процесс оплаты и обработки подписки"""
    # На всякий случай завершаем все состояния
    await state.finish()
    logger.info(f'Начинаем платеж для пользователя {message.from_user.id}')
    await message.bot.send_message(chat_id=message.from_user.id,
                                   text=actual_texts.story_tell,
                                   parse_mode='HTML',
                                   reply_markup=await main_keyboard())
    user_id = message.from_user.id

    # Создаем объект платежа и отправляем его
    invoice = giga_chat.XTRInvoiceOneMonth(
        chat_id=message.from_user.id,
        payload=f'user_{user_id}'
    )
    result = await invoice.send(message.bot)
    logger.info(f'Платеж отправлен: {result}')


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    """Получаем запрос от Telegram на проверку корректности заказа"""
    logger.info(f'Получил pre_checkout_query: {pre_checkout_query}')
    # Всегда подтверждайте pre_checkout_query, если все параметры корректны
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    await PaymentStates.waiting_for_payment.set()


async def process_successful_payment(message: types.Message, state: FSMContext):
    """Обрабатываем успешный платеж"""
    logger.info(f'Получил успешный платеж: {message}')

    payment_info = message.successful_payment
    user_id = message.from_user.id

    # Обновляем количество дней подписки у пользователя в базе данных
    user_subscription = await db.update_subscription(user_id, days_count=31)

    # Отправляем радостный стикер
    # TODO: Это тупой костыль, надо исправить (заменить получение стикера на что-то, не относящееся к оценке)
    await message.answer_sticker(sticker=utils.get_sticker_by_score(10))

    # Сообщаем пользователю о новой дате подписки в формате день, месяц, год, где месяц написан текстом
    await message.answer(
        text=actual_texts.successful_payment.format(
            total_amount=payment_info.total_amount,
            currency=payment_info.currency,
            end_date=user_subscription.end_date.strftime('%d.%m.%Y')
        ))
    await message.bot.send_message(chat_id=settings.admin_chat_id,
                                   text=f'❗️ Пользователь {message.from_user.first_name} '
                                        f'{message.from_user.last_name} оформил подписку.')
    await state.finish()


async def change_skills(message: types.Message, state: FSMContext):
    """"Изменяем навыки, на основе которых модель будет генерировать вопросы"""
    logger.info('Изменяем навыки пользователя')
    # Устанавливаем состояние изменения навыков
    await Form.skills.set()
    logger.debug(f'Изменили состояние: {state}')
    # Отправляем вопрос пользователю
    await message.reply(text=actual_texts.change_skill,
                        reply_markup=await skills_keyboard())
    await message.reply(text=actual_texts.choose_one_or_cancel,
                        reply_markup=await cancel_keyboard())


async def process_skill_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор скилла"""
    logger.info('Обрабатываем выбор скилла')
    # Сохраняем выбранный скилл пользователя
    skill = callback_query.data
    user = await db.update_skill(callback_query.from_user.id, skill)
    # Завершаем состояния и отвечаем юзеру
    await state.finish()

    await callback_query.message.answer(text=actual_texts.changed_skill
                                        .format(skill=Skills
                                                .get_skill_by_name(user.skill)
                                                .short_description),
                                        reply_markup=await main_keyboard())


async def change_mode(message: types.Message, state: FSMContext):
    """"Изменяем режим тренировок, на основе которого модель будет
    присылать вопросы по одной, по всем или только по слабым темам"""
    logger.info('Изменяем режим тренировок пользователя')
    # Устанавливаем состояние изменения навыков и отправляем вопрос пользователю
    await Form.mode.set()
    await message.reply(text=actual_texts.change_mode,
                        reply_markup=await mode_keyboard())
    await message.reply(text=actual_texts.choose_one_or_cancel,
                        reply_markup=await cancel_keyboard())


async def process_mode_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор режима"""
    logger.info('Обрабатываем выбор навыка')
    # Сохраняем выбранный скилл пользователя и отправляем сообщение
    current_mode = callback_query.data
    await db.update_mode(tg_id=callback_query.from_user.id, mode=current_mode)
    await callback_query.message.answer(text=actual_texts.changed_mode.format(current_mode=current_mode),
                                        reply_markup=await main_keyboard())
    # Завершаем состояние
    await state.finish()


async def get_profile(message: types.Message):
    """Получаем профиль"""
    logger.info('Получаем профиль')
    # Получаем объект пользователя из базы
    user = await db.get_user(tg_id=message.from_user.id)

    # Генерируем среднюю оценку по скиллам
    average_score = utils.get_average_skill_score(user)

    # Получаем ключ для кэша и название для файла
    image_cache_key = utils.get_skill_map_name(user, mode='key')
    image_filename = utils.get_skill_map_name(user, mode='file')

    # Проверяем наличие кэша в Redis
    file_id = await cache.get(image_cache_key)

    # Создаем текст сообщения
    final_text = actual_texts.profile.format(average_score=average_score,
                                             user_mode=user.mode,
                                             user_skill=user.skill,
                                             sub_status=await db.get_paid_status_for_profile(user))

    if file_id is None:
        logger.debug(f"Создаем карту навыков: {image_filename}. "
                     f"Отправляем ее пользователю и загружаем в кэш.")
        # Если кэша нет, создаем картинку со скиллами пользователя
        bytes_skill_map = await utils.create_skill_map(user)
        # Создаем объект InputFile из массива байтов
        skill_map_file = types.InputFile(io.BytesIO(bytes_skill_map), filename=image_filename)
        # Отправляем карту пользователю
        msg = await message.reply_photo(skill_map_file,
                                        caption=final_text,
                                        parse_mode='HTML')
        # Получаем идентификатор файла
        file_id = msg.photo[-1].file_id
        # Сохраняем идентификатор файла в Redis
        await cache.set(image_cache_key, file_id)
    else:
        logger.debug(f"Отправляем кэш карты навыков: {file_id.decode('utf-8')}")
        # Отправляем файл пользователю
        await message.reply_photo(file_id.decode('utf-8'),
                                  caption=final_text,
                                  parse_mode='HTML')


async def get_paid_hint(callback_query: types.CallbackQuery, user_is_paid: bool) -> None:
    # Извлекаем текст вопроса из сообщения
    question_text = callback_query.message.text
    # Заранее определяем пустую клавиатуру
    inline_keyboard = types.InlineKeyboardMarkup()

    # Проверяем активна ли подписка у пользователя
    if user_is_paid:

        # Отправляем текст вопроса на нейросеть и получаем ответ
        answer_text = await giga_chat.get_answer_the_question(question_text)
        # Дополняем исходное сообщение ответом от нейросети
        final_text = f'<b>{question_text}</b>' + hspoiler('\n\n' + f'{answer_text}')
        # Клавиатуру оставляем пустой
    else:
        final_text = (f'<b>{question_text}</b>'
                      + '\n\nЧтобы генерировать подсказки, нужен AI+. '
                        'Попробуй ответить самостоятельно или оформи AI+, '
                        'чтобы получать подсказки прямо здесь :)')
        # Меняем клавиатуру на предложение оформить подписку
        inline_keyboard = await keyboards.get_subscribe_keyboard()

    # Отправляем получившееся сообщение
    await callback_query.message.edit_text(text=final_text,
                                           parse_mode=types.ParseMode.HTML,
                                           reply_markup=inline_keyboard)


async def register_handlers(dp: Dispatcher):
    """Регистрируем хэндлеры"""
    # Хэндлеры старта и отмены
    dp.register_message_handler(start, commands=[Commands.start])
    dp.register_message_handler(cancel, Text(Commands.cancel_text), state='*')

    # Хэндлеры получения, пересоздания вопроса или получения подсказки
    dp.register_message_handler(recreate_question, Text(Commands.another_question_text), state=Form.question)
    dp.register_message_handler(get_question, Text(Commands.get_question_text))
    dp.register_message_handler(get_question, commands=[Commands.get_question_command])
    dp.register_callback_query_handler(get_answer_the_question,
                                       lambda c: c.data == Commands.get_answer_command,
                                       state=Form.question)

    # Хэндлеры для изменения скиллов
    dp.register_message_handler(change_skills, Text(Commands.change_skills_text))
    dp.register_message_handler(change_skills, commands=[Commands.change_skills_command])
    dp.register_callback_query_handler(process_skill_selection, state=Form.skills)

    # Хэндлеры для изменения режима
    dp.register_message_handler(change_mode, Text(Commands.change_mode_text))
    dp.register_message_handler(change_mode, commands=[Commands.change_mode_command])
    dp.register_callback_query_handler(process_mode_selection, state=Form.mode)

    # Хэндлеры для просмотра профиля
    dp.register_message_handler(get_profile, Text(Commands.profile_text), )
    dp.register_message_handler(get_profile, commands=[Commands.profile_command])

    # Хэндлеры обработки ответа на вопрос
    dp.register_message_handler(process_question, state=Form.question)

    # Хэндлеры для обработки подписки
    dp.register_callback_query_handler(start_payment,
                                       lambda c: c.data == Commands.get_subscribe_command,
                                       state='*')
    dp.register_message_handler(start_payment, commands=[Commands.get_subscribe_command])
    dp.register_pre_checkout_query_handler(process_pre_checkout_query)
    dp.register_message_handler(process_successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT,
                                state=PaymentStates.waiting_for_payment)


if __name__ == '__main__':
    logger.debug(Skills.get_skill_by_name('efficiency').short_description)
