from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

# Global dictionary to store players by room
players_by_room = {}

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'
        
        logging.info(f"Connecting to group: {self.room_group_name}")

        # Initialize players list for the room if it doesn't exist
        if self.room_group_name not in players_by_room:
            players_by_room[self.room_group_name] = []

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logging.info(f"Player connected: {self.channel_name}")

    async def disconnect(self, close_code):
        # Remove player from the global players list
        if hasattr(self, 'username') and self.username in players_by_room[self.room_group_name]:
            players_by_room[self.room_group_name].remove(self.username)
            logging.info(f"Player disconnected: {self.username}")
            # Notify remaining players if necessary
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'player_disconnected',
                    'username': self.username,
                }
            )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        self.username = data['username']  # Save the username for this connection

        # Add player to the global list if not already added
        if self.username not in players_by_room[self.room_group_name]:
            players_by_room[self.room_group_name].append(self.username)
            logging.info(f"Added player: {self.username}, players: {players_by_room[self.room_group_name]}")

        if len(players_by_room[self.room_group_name]) == 2:  # Check if there are 2 players
            # Notify both players to start the game
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'start_game',
                    'players': players_by_room[self.room_group_name],
                }
            )

    async def start_game(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': 'Game is starting!',
            'players': event['players'],
        }))
        logging.info(f"Game started for players: {event['players']}")

    async def player_disconnected(self, event):
        # Notify players about the disconnection
        await self.send(text_data=json.dumps({
            'message': f"{event['username']} has disconnected.",
        }))
        logging.info(f"Player disconnected: {event['username']}")
