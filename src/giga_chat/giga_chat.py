import certifi
import asyncio
from gigachat import GigaChat
from src.config import settings
from loguru import logger
from aiogram import types


# TODO: Здесь нужна фабрика, чтобы уйти от конкретной реализации
#  AI-помощника и сделать его легко заменяемым
class AIInterviewer:
    def __init__(self, final_prompt: str,
                 api_token: str = settings.gigachat_api_token,
                 max_tokens: int = settings.max_tokens_assessment):
        self.model = GigaChat(
            credentials=api_token,
            ca_bundle_file=certifi.where(),
            scope="GIGACHAT_API_PERS",
            model="GigaChat",
        )
        self.messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": final_prompt}
        ]
        self.max_tokens = max_tokens

    async def send_request(self):
        # Делаем несколько попыток в случае исключения и получения "status":429,"message":"Too Many Requests"
        for attempt in range(settings.max_request_attempts):
            try:
                response = await self.model.achat({
                    "messages": self.messages,
                    "max_tokens": self.max_tokens
                })
                return response
            except Exception as e:
                logger.error(f"Попытка {attempt + 1}/{settings.max_request_attempts} запроса к GigaChat не удалась: {e}.")
                if attempt == settings.max_request_attempts - 1:
                    logger.error(f'GigaChat выдал ошибку: {e}.')
                    raise e
                await asyncio.sleep(1)


# TODO: Тоже сильно привязываемся к конкретной авторизации, исправить
# TODO: Не знаю, почему перенес модель инвойса сюда,
#  она не совсем относится к гигачату, перенести в другое место
class XTRInvoiceOneMonth:
    """Объект платежа на 1 месяц в звездах телеграмма"""

    def __init__(self, chat_id, payload):
        self.chat_id = chat_id
        self.title = 'Подписка AI+'
        self.description = 'Расширенные возможности AI-интервьюера — 1 мес.'
        self.payload = payload
        self.currency = 'XTR'
        self.provider_token = ''
        self.prices = [types.LabeledPrice(label='Подписка AI+ на 1 мес.', amount=25)]

    async def send(self, bot):
        await bot.send_invoice(
            chat_id=self.chat_id,
            title=self.title,
            description=self.description,
            payload=self.payload,
            currency=self.currency,
            provider_token=self.provider_token,
            prices=self.prices,
        )


# TODO: Возможно, промпт лучше инкапсулировать прямо здесь?
#  Логичнее передавать вопрос и ответ сюда, а не все подробности сразу
async def get_assessment_of_answer(final_prompt: str) -> str:
    # Создаем экземпляр интервьюера и отправляем запрос
    interviewer = AIInterviewer(final_prompt=final_prompt)
    try:
        response = await interviewer.send_request()
    except Exception as e:
        logger.error(f'GigaChat пытался обработать ответ и выдал ошибку: {e}.')
        raise e

    return response.choices[0].message.content


async def get_answer_the_question(final_prompt: str) -> str:
    # Создаем экземпляр интервьюера и отправляем запрос
    interviewer = AIInterviewer(final_prompt=final_prompt,
                                max_tokens=settings.max_tokens_answer)
    try:
        response = await interviewer.send_request()
        logger.debug(f'Получаем подсказку ответа от GigaChat: {response}')
    except Exception as e:
        logger.error(f'Ошибка при получении подсказки от GigaChat: {e}')
        return "Ошибка при получении подсказки от AI"

    return response.choices[0].message.content
