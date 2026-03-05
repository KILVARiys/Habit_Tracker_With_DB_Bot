import asyncio
import logging
import aiosqlite

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

#CLASS
class HabitsStatus(StatesGroup):
    waiting_habit_name = State()

#DEFS
async def weekly_stat(user_id, habit_name):
    async with aiosqlite.connect('habits.db') as db:
        cursor = await db.execute(
            "SELECT id FROM habits WHERE user_id = ? AND name = ?",
            (user_id, habit_name)
        )
        habit = await cursor.fetchone()

        if not habit:
            return None

        habit_id = habit[0]

        cursor = await db.execute(
            '''SELECT COUNT(*) FROM habits_completions WHERE habit_id = ? AND completion_date >= date('now', '-7 days')''',
            (habit_id,)
            )
        
        count = await cursor.fetchone()
        complete_days = count[0] if count else 0

        percentage = (complete_days/7) * 100
        return percentage

def create_progress_bar(percentage: float):
    filled = int(percentage / 10)
    empty = 10 - filled
    return "█" * filled + "░" * empty

async def regist_user(telegram_id: int, username: str = None):
    async with aiosqlite.connect('habits.db') as db:
        cursor = await db.execute(
            'SELECT id FROM users WHERE telegram_id = ?',
            (telegram_id,)
        )
        user = await cursor.fetchone()

        if user is None:
            await db.execute(
                'INSERT INTO users (telegram_id, username) VALUES (?, ?)',
                (telegram_id, username)
            )
            await db.commit()

async def check_habit(user_id: int, habit_name):
    async with aiosqlite.connect('habits.db') as db:
        cursor = await db.execute(
            'SELECT id FROM habits WHERE user_id = ? AND name = ?',
            (user_id, habit_name)
        )
        result = await cursor.fetchone()

        return result is not None

async def complete_habit(user_id: int, habit_id):
    async with aiosqlite.connect('habits.db') as db:
        cursor = await db.execute(
            "SELECT id FROM habits_completions WHERE habit_id = ? AND completion_date = date('now')",
            (habit_id,)
        )
        existing = await cursor.fetchone()

        if existing:
            return False
        
        await db.execute(
            "INSERT INTO habits_completions (habit_id, completion_date) VALUES (?, date('now'))",
            (habit_id,)
        )
        await db.commit()
        return True

async def get_user_habits(user_id:int):
    async with aiosqlite.connect('habits.db') as db:
        cursor = await db.execute(
            'SELECT id, name FROM habits WHERE user_id = ?',
            (user_id,)
        )
        habits = await cursor.fetchall()
        return habits

#DB
async def init_db():
    async with aiosqlite.connect('habits.db') as db:
        #CREATE TABLE USERS
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                username TEXT
            )
        ''')

        #CREATE TABLE HABITS
        await db.execute('''
            CREATE TABLE IF NOT EXISTS habits(
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                name TEXT,
                created_date DATE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        #CREATE TABLE HABITS_COMPLETE
        await db.execute('''
            CREATE TABLE IF NOT EXISTS habits_completions(
                id INTEGER PRIMARY KEY,
                habit_id INTEGER,
                completion_date DATE,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )
        ''')
        await db.commit()

#Bot
TOKEN = '8267885107:AAGNjEtRr2GDjH97bNqSX8XPz3PXqE9JepQ'
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username

    await init_db()

    await regist_user(telegram_id, username)

    await message.answer(text=f'''
Привет {message.from_user.first_name}
Чтобы увидеть меню взаимодействия напиши /menu
''')

@dp.message(Command('menu'))
async def menu_handler(message: types.Message):
    menu_keyboard = InlineKeyboardMarkup(
        inline_keyboard = [
            [
                InlineKeyboardButton(text='Добавить прывычку', callback_data='Add_Habit'),
                InlineKeyboardButton(text='Отметить выполнение прывычки', callback_data='Mark_Habit'),
                InlineKeyboardButton(text='Просмотреть статистику', callback_data='Check_Stat')
            ]
        ]
    )
    await message.answer(
        text='Выберите действие:',
        reply_markup=menu_keyboard
    )

@dp.callback_query(F.data == 'Add_Habit')
async def Add_Habit(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите название привычки')
    await state.set_state(HabitsStatus.waiting_habit_name)
    await callback.answer()

@dp.message(HabitsStatus.waiting_habit_name)
async def habit_name_select(message: types.Message, state: FSMContext):
    habit_name = message.text
    telegram_id = message.from_user.id
    user_id = telegram_id

    if await check_habit(user_id, habit_name):
        await message.answer('Такая прывычка уже есть')
    else:
        async with aiosqlite.connect('habits.db') as db:
            await db.execute(
                'INSERT INTO habits (user_id, name, created_date) VALUES (?, ?, date("now"))',
                (user_id, habit_name)
            )
            await db.commit()
            await message.answer(text=f'Прывычка {habit_name} добавлена!')

    await state.clear()

@dp.callback_query(F.data == 'Mark_Habit')
async def Mark_Habit(callback: CallbackQuery):
    user_habits = await get_user_habits(user_id=callback.from_user.id)
    if user_habits:
        buttons = []
        for habit_id, habit_name in user_habits:
            button = InlineKeyboardButton(
                text=habit_name,
                callback_data=f'complete_{habit_id}'
            )
            buttons.append([button])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.message.answer(
            text='Выберите прывычку, которую выполнили',
            reply_markup=keyboard
            )
    else:
        await callback.message.answer('У тебя нет прывычек!')
    
    await callback.answer()

@dp.callback_query(F.data.startswith('complete_'))
async def process_habit_completion(callback: CallbackQuery):
    habit_id = int(callback.data.split('_')[1])

    success = await complete_habit(user_id=callback.from_user.id, habit_id=habit_id)

    if success:
        await callback.message.answer('Прывычка отмечена')
    else:
        await callback.message.answer('Ты уже отмечал эту привычку сегодня')

    await callback.answer()

@dp.callback_query(F.data == 'Check_Stat')
async def Check_Stat(callback: CallbackQuery):
    user_habits = await get_user_habits(callback.from_user.id)

    if not user_habits:
        await callback.message.answer(text='У тебя еще нет привычек')
        await callback.answer()
        return

    stats_text = "Статистика за неделю:\n\n"
    
    for habit_id, habit_name in user_habits:
        percentage = await weekly_stat(callback.from_user.id, habit_name)
        if percentage is not None:
            bar = create_progress_bar(percentage)
            stats_text += f"• {habit_name}: {percentage:.1f}%\n{bar}\n\n"
    
    await callback.message.answer(stats_text)
    await callback.answer()

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())