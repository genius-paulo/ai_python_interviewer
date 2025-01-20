from aiogram.dispatcher.filters.state import State, StatesGroup


# Создаем класс состояний
class Form(StatesGroup):
    question = State()
    skills = State()
    mode = State()


class PaymentStates(StatesGroup):
    waiting_for_payment = State()
