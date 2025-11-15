# tbot/app/core/websocket_manager.py
from fastapi import WebSocket
from typing import List, Dict
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, event: str, payload: Dict):
        """
        Broadcasts a message to all active WebSocket connections.
        """
        message = {"event": event, "payload": payload}
        message_json = json.dumps(message)

        for connection in self.active_connections:
            await connection.send_text(message_json)

# Create a single, globally accessible instance of the manager
manager = ConnectionManager()
