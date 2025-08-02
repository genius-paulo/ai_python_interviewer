from aiogram import types

class XTRInvoiceOneMonth:
    """Объект платежа на 1 месяц в звездах телеграмма"""

    def __init__(self, chat_id, payload):
        self.chat_id = chat_id
        self.title = 'Подписка AI+'
        self.description = 'Расширенные возможности AI-интервьюера — 1 мес.'
        self.payload = payload
        self.currency = 'XTR'
        self.provider_token = ''
        self.prices = [types.LabeledPrice(label='Подписка AI+ на 1 мес.', amount=1)]

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
