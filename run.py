import asyncio
import uvicorn
from threading import Thread

def run_api():
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)

async def run_bot():
    from main import main
    await main()

if __name__ == "__main__":
    # Запускаем API в отдельном потоке
    api_thread = Thread(target=run_api)
    api_thread.start()
    
    # Запускаем бота
    asyncio.run(run_bot())