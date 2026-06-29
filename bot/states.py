from aiogram.fsm.state import State, StatesGroup

class RegistrationState(StatesGroup):
    waiting_for_name = State()

class DailyState(StatesGroup):
    waiting_for_description = State()
    waiting_for_exercise = State()

class ExerciseState(StatesGroup):
    waiting_for_answer = State()