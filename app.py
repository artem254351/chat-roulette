# server_queue.py
import asyncio
import websockets
import json

# Множество всех подключённых пользователей
connected_users = set()
# Очередь пользователей, которые ищут собеседника
waiting_queue = asyncio.Queue()

async def handler(websocket, path):
    connected_users.add(websocket)
    print(f"Новый пользователь подключен. Всего: {len(connected_users)}")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")
            
            if action == "findUser":
                # Добавляем пользователя в очередь поиска
                await waiting_queue.put(websocket)
                await try_pair_users()
    except websockets.ConnectionClosed:
        print("Пользователь отключился")
    finally:
        connected_users.discard(websocket)
        # Убираем пользователя из очереди, если он там был
        temp_queue = asyncio.Queue()
        while not waiting_queue.empty():
            user = await waiting_queue.get()
            if user != websocket:
                await temp_queue.put(user)
        while not temp_queue.empty():
            await waiting_queue.put(await temp_queue.get())

async def try_pair_users():
    # Пока в очереди хотя бы 2 пользователя
    while waiting_queue.qsize() >= 2:
        user1 = await waiting_queue.get()
        user2 = await waiting_queue.get()
        
        # Отправляем обоим сообщение о соединении
        await user1.send(json.dumps({"status": "found"}))
        await user2.send(json.dumps({"status": "found"}))
        print("Пользователи соединены!")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Сервер запущен на ws://0.0.0.0:8765")
        await asyncio.Future()  # Бесконечно

asyncio.run(main())

    
