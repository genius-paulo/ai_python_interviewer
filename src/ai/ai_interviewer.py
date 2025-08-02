import asyncio
import certifi
from abc import ABC, abstractmethod
from typing import Optional

from gigachat import GigaChat
from openai import OpenAI
from loguru import logger

from src.config import settings


class AIInterviewerBase(ABC):
    """Базовый класс для AI-интервьюеров с инкапсулированной логикой"""

    def __init__(self, prompt: str, max_tokens: Optional[int] = None):
        """
        :param prompt: Текст промпта для AI
        :param max_tokens: Максимальное количество токенов в ответе
        """
        self.messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt}
        ]
        self.max_tokens = max_tokens or settings.max_tokens_assessment

    @abstractmethod
    async def _send_api_request(self):
        """Абстрактный метод для отправки запроса к API"""
        pass

    async def _request_with_retries(self):
        """Обертка для запросов с повторными попытками"""
        for attempt in range(settings.max_request_attempts):
            try:
                return await self._send_api_request()
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{settings.max_request_attempts} failed: {e}")
                if attempt == settings.max_request_attempts - 1:
                    logger.error(f'Final attempt failed: {e}')
                    raise
                await asyncio.sleep(1 + attempt)

    async def assess_answer(self) -> str:
        """
        Оценить ответ пользователя
        :return: Текст оценки от AI
        """
        response = await self._request_with_retries()
        return self._extract_message_content(response)

    async def generate_answer(self) -> str:
        """
        Сгенерировать ответ на вопрос
        :return: Текст ответа от AI
        """
        response = await self._request_with_retries()
        return self._extract_message_content(response)

    @staticmethod
    def _extract_message_content(response) -> str:
        """Извлечение контента из ответа API"""
        # Реализация зависит от структуры ответа конкретного API
        if hasattr(response, 'choices'):
            return response.choices[0].message.content
        elif hasattr(response, 'messages'):
            return response.messages[0].content
        return str(response)


class GigaAIInterviewer(AIInterviewerBase):
    """Реализация интервьюера для GigaChat API"""

    def __init__(self, prompt: str, max_tokens: Optional[int] = None):
        super().__init__(prompt, max_tokens)
        self.model = GigaChat(
            credentials=settings.gigachat_api_token,
            ca_bundle_file=certifi.where(),
            scope="GIGACHAT_API_PERS",
            model="GigaChat-Pro",
        )

    async def _send_api_request(self):
        return await self.model.achat({
            "messages": self.messages,
            "max_tokens": self.max_tokens
        })


class DeepAIInterviewer(AIInterviewerBase):
    """Реализация интервьюера для DeepSeek API"""

    def __init__(self, prompt: str, max_tokens: Optional[int] = None):
        super().__init__(prompt, max_tokens)
        self.model = OpenAI(
            api_key=settings.deepseek_api_token,
            base_url="https://api.deepseek.com"
        )

    async def _send_api_request(self):
        return self.model.chat.completions.create(
            model="deepseek-chat",
            messages=self.messages,
            stream=False,
            max_tokens=self.max_tokens,
            temperature=0.3,
        )

interviewer = GigaAIInterviewer
