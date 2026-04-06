# api.py
from fastapi import FastAPI, HTTPException, Header
from database import get_user_habits, weekly_stat, add_habit, check_habit
import uvicorn

app = FastAPI()

API_TOKEN = "habit_tracker_api"

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/stats/{telegram_id}")
async def get_statistics(telegram_id: int, authorization: str = Header(None)):
    verify_token(authorization)

    habits = await get_user_habits(telegram_id)

    stats = []
    for habit_id, habit_name in habits:
        percentage = await weekly_stat(telegram_id, habit_name)
        stats.append({
            "habit_name": habit_name,
            "completion_percentage": percentage
        })
    return {"user_id": telegram_id, "statistics": stats}

@app.post("/habits")
async def create_habit(habit_data: dict, authorization: str = Header(None)):
    verify_token(authorization)
    
    telegram_id = habit_data.get('telegram_id')
    habit_name = habit_data.get('habit_name')

    if not telegram_id or not habit_name:
        raise HTTPException(status_code=400, detail="Missing telegram_id or habit_name")
    
    if await check_habit(user_id=telegram_id, habit_name=habit_name):
        raise HTTPException(status_code=400, detail="Habit already exists")

    await add_habit(telegram_id, habit_name)

    return {'status': 'success', 'message': f"Habit '{habit_name}' added"}