from pydantic import BaseModel
from src.bot.bot_content import skills
from src.db.models import Users
from loguru import logger


class MiddlePythonInterviewerChat(BaseModel):
    user_is_paid: bool = None
    question: str = None
    context_questions: str = ("Ты Senior Python-разработчик и проводишь собеседование на Middle Python-разработчика. "
                              "Ты задал кандидату вопрос «{question}», ответ на который рекомендуется от 200 "
                              "до 700 символов. Кандидат ответил так: «{answer}». "
                              "Оцени ответ от 1 до 10 в зависимости от того, "
                              "насколько он отвечает на вопрос и соответствует уровню знаний Middle-разработчика."
                              "\nОтветь в таком формате:"
                              "\n1. «Оценка: 1/10»"
                              "\n\n2. Опиши плюсы и минусы ответа."
                              "\n\n3. Опиши навыки, которые затрагивает понимание заданного вопроса. "
                              "В ответе не используй знаки форматирования текста. "
                              "Чаще ставь 10/10 и хвали кандидата, если ответ хороший."
                              "Если ответ не соответствует вопросу, кандидат не знает ответа или "
                              "ответ полностью неверный, оцени его не больше 3 баллов, пришли оценку «Оценка: 1-3/10. "
                              "Попробуем другой вопрос?», не продолжай диалог и не задавай других вопросов.")
    answer: str = None
    skill: skills.Skills = None
    score: float = 0
    help_answer: str = ("Ты Senior Python-разработчик и проводишь собеседование на Middle Python-разработчика. "
                        "Ты задал кандидату вопрос «{question}» и собираешься оценить его по 10-бальной шкале."
                        "Расскажи правильный ответ на вопрос по Python так, чтобы он заслужил оценку 10/10. "
                        "Постарайся ответить кратко и уложиться в 1000 символов.")

    def get_final_prompt(self) -> str:
        if self.question is None or self.answer is None:
            raise AttributeError
        else:
            return self.context_questions.format(question=self.question, answer=self.answer)


if __name__ == '__main__':
    history_chat = MiddlePythonInterviewerChat(question='Вот такой вопрос', answer='Вот такой ответ')
    print(history_chat.get_final_prompt())
