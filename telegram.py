from aiogram import Bot, Dispatcher, types
import logging
from aiogram import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from Llama import get_response
from ruGPT import generate_annotation
from dotenv import load_dotenv
import os

# Загрузка модели
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Строка для обращения к GPT
prompts = "Напиши ответ для пользователя при некорректном вводе ответа в телеграмм боте, при этом не пиши ничего лишнего. Напиши, что нужно ввести корректное значение"

# Определяем уровни состояний
class QuizStates(StatesGroup):
    level1 = State()
    level2 = State()
    level3 = State()
    level4 = State()
    level5 = State()

# Начало общения
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await QuizStates.level1.set()  # Устанавливаем состояние
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Настроить доставку")
    markup.add(btn1)
    await message.answer("Приветствуем вас в нашем магазине. Здесь вы можете настроить процесс доставки заказа!", reply_markup=markup)

# Обработка сообщений на уровне 1
@dp.message_handler(state=QuizStates.level1)
async def process_level1(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Да")
    btn2 = types.KeyboardButton("Нет")
    markup.add(btn1, btn2)
    if message.text == 'Настроить доставку':
        await QuizStates.level2.set()  # Переход на уровень 2
        await message.answer("Чтобы оформить заказ, я задам вам несколько вопросов. Продолжая диалог, вы даете согласие на обработку персональных данных.", reply_markup=markup)
    else:
        await message.answer(get_response(prompts), reply_markup=markup)

# Обработка сообщений на уровне 2
@dp.message_handler(state=QuizStates.level2)
async def process_level2(message: types.Message, state: FSMContext):
    if message.text == 'Да':
        await QuizStates.level3.set()  # Переход на уровень 3
        clear = types.ReplyKeyboardRemove()
        await message.answer("Введите ваш номер заказа", reply_markup=clear)
    elif message.text == 'Нет':
        await message.answer("Нужно согласиться с поставленным условием")
    else:
        await message.answer(generate_annotation(prompts))

# Обработка сообщений на уровне 3
@dp.message_handler(state=QuizStates.level3)
async def process_level3(message: types.Message, state: FSMContext):
    await QuizStates.level4.set()  # Переход на уровень 4
    await message.answer(f"Ваш заказ {message.text}! Напишите номер телефона для связи")

# Обработка сообщений на уровне 4
@dp.message_handler(state=QuizStates.level4)
async def process_level4(message: types.Message, state: FSMContext):
        await QuizStates.level5.set()  # Переход на уровень 5
        await message.answer(f"Ваш телефон {message.text}! Напишите адрес доставки")

# Обработка сообщений на уровне 5
@dp.message_handler(state=QuizStates.level5)
async def process_level5(message: types.Message, state: FSMContext):
        await message.answer("Заказ принят в обработку!")
        await state.finish()  # Сбрасываем состояние

# Команда для выхода
@dp.message_handler(commands=['cancel'], state='*')
async def cancel_command(message: types.Message, state: FSMContext):
    await state.finish()  # Сбрасываем состояние
    await message.answer("Вы вышли из процесса. Если хотите начать заново, используйте команду /start.")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)