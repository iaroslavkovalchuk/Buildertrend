from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.Utils.database_handler import get_main_table
from database import AsyncSessionLocal
import asyncio

router = APIRouter()

# Dependency to get the database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            # Query the database
            main_table_data = await get_main_table(db)
            # Convert data to a list of dictionaries with specific conditions
            data_list = [
                {
                    "id": item.id,
                    "num_sent": item.num_sent
                }
                for item in main_table_data
                if item.num_sent != len(item.phone_numbers) and item.message_status == 1
            ]
            
            data_to_send = {
                "type": "CLIENT_UPDATE",
                "data": data_list
            }
            # Send the data back to the client
            await websocket.send_json(data_to_send)
            # Add a delay to control the frequency of updates
            await asyncio.sleep(1)  # Adjust the sleep time as needed
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        await websocket.close()
