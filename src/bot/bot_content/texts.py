from dataclasses import dataclass
from src.bot.bot_content.basics import Commands, Modes


@dataclass
class VariousBotText:
    story_tell: str
    greeting: str
    all_commands: str
    cancel_all: str

    get_question_skill: str
    get_question_ai_question: str
    ai_answer: str

    profile: str

    change_skill: str
    changed_skill: str

    change_mode: str
    changed_mode: str

    choose_one_or_cancel: str

    successful_payment: str


actual_texts = VariousBotText(
    story_tell=
    '<b>Зачем поддерживать проект и оформлять подписку?</b>'
    '\n\nБазовая функциональность всегда <b>доступна в бесплатно</b>. '
    'Но в AI-интервьювере есть дополнительные функции, '
    'которые <b>расходуют больше ресурсов</b>, но делают подготовку гораздо комфортнее. '
    '\n\nЭто:'
    '\n— Генерация ответа на вопрос с помощью AI.'
    '\n— Установка кастомного навыка для прокачки (в разработке).'
    '\n— Обработка ответов в виде голосовых (в разработке).'
    '\n\nЧтобы активировать новые фичи и поддержать развитие бота, я добавил недорогую подписку. '
    'Она позволяет <b>покрыть расходы на содержание</b> и, надеюсь, еще на пару чашек кофе :)'
    '\n\n👇 Поддержи проект, получи плюсик в карму и доступ к новым фичам в числе первых.',

    greeting='Привет, {user_id}! Я бот-интервьюер. Я могу задавать вопросы по программированию на Python. ',

    all_commands=f'❓ /{Commands.get_question_command}, чтобы получить вопрос собеседования.\n\n'
                 f'⚙️ /{Commands.change_mode_command}, чтобы выбрать, как ИИ будет задавать вопросы '
                 f'(все темы, конкретная тема, слабые темы).\n\n'
                 f'💪 /{Commands.change_skills_command}, чтобы выбрать конкретный навык, если хочешь подтянуть '
                 f'конкретную тему.\n\n'
                 f'👤 /{Commands.profile_command}, чтобы посмотреть карту навыков, режим тренировки и статус AI+.\n\n'
                 f'✨ /{Commands.get_subscribe_command}, чтобы получить все возможности AI+ и поддержать проект.\n\n'
                 f'Если что-то пошло не так, пиши @genius_paulo.',

    cancel_all=f'Окей, отменяем.'
               f'\n\nЕсли захочешь продолжить, нажми:\n',

    get_question_skill='Вопрос на тему: {skill}',

    get_question_ai_question='{ai_question}',

    ai_answer='{ai_answer}\n\n'
              'Оценка навыка изменилась: {old_score} → {new_score}.',

    profile='👤 <b>{average_score}/10</b> — средний балл карты навыков. Чем выше оценка у навыка, тем лучше.'
            '\n\n⚙️ <b>{user_mode}</b> — режим работы ИИ'
            '\n(all — все темы, specific — конкретная тема, worst — темы с самой низкой оценкой).'
            '\n\n💪 <b>{user_skill}</b> — навык для тренировки в режиме specific.'
            '\n\n✨ AI+: {sub_status}',

    change_skill='Какую тему хочешь подтянуть?',

    changed_skill=f'Тема для тренировок  в режиме {Modes().specific} обновлена. '
                  'Теперь ИИ будет задавать вопросы по теме: «{skill}».'
                  f'\n\nНажми «{Commands.get_question_text}», чтобы ИИ сгенерировал новый вопрос.',

    choose_one_or_cancel=f"Выбери один из вариантов или нажми {Commands.cancel_text}",

    change_mode='По каким темам ИИ должен задавать вопросы:'
                '\n\n🔀 all — все темы в случайном порядке;'
                f'\n\n1️⃣ specific — конкретную тему (можно указать, выбрав «{Commands.change_skills_text}» в меню; '
                f'\n\n⬇️ worst — темы с самой низкой оценкой (можно посмотреть, выбрав «{Commands.profile_text}» в меню).',

    changed_mode='Режим тренировок обновлен на {current_mode}.',

    successful_payment=f"Спасибо за поддержку!"
                       "\n\nПлатеж на сумму {total_amount} {currency} принят. "
                       "Расширенные функции активированы до {end_date}. "
                       "Автор пошел оплачивать сервера и покупать себе кофе."
                       f"\n\nНажми /{Commands.get_question_command} и попробуй сгенерировать ответ на вопрос :)"
)
