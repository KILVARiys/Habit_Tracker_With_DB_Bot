import aiosqlite

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

async def check_habit(user_id: int, habit_name):
    async with aiosqlite.connect('habits.db') as db:
        cursor = await db.execute(
            'SELECT id FROM habits WHERE user_id = ? AND name = ?',
            (user_id, habit_name)
        )
        result = await cursor.fetchone()

        return result is not None

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

async def add_habit(user_id, habit_name):
    async with aiosqlite.connect('habits.db') as db:
        await db.execute(
            'INSERT INTO habits (user_id, name, created_date) VALUES (?, ?, date("now"))',
            (user_id, habit_name)
        )
        await db.commit()