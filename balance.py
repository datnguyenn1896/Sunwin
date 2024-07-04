import asyncio
import websockets
import json
import certifi
import ssl
import logging
import tracemalloc
from websockets.exceptions import InvalidStatusCode
import argparse
import argparse

tracemalloc.start()

class WebSocketClient:
    def __init__(self, login_data):
        self.old_data = None
        self.dict_result = {}
        self.previous_session = None
        self.gold = 0
        self.data_status = {}
        self.previous_gold = None
        self.login_data = login_data

        # Tắt toàn bộ logging
        logging.basicConfig(level=logging.CRITICAL)

    def write_data(self,path, data):
        with open(path + '.txt', 'w', encoding='utf-8') as file:
            file.write(data)

    async def send_ping(self, websocket):
        while True:
            try:
                await websocket.ping()
            except websockets.ConnectionClosed:
                break
            await asyncio.sleep(1)

    async def connect_and_communicate(self, uri, name, username, option, site, path):
        try:
            self.data_status[username] = {
                "status": "wait_end_session",
                "prev_session": None,
                "prev_bet": 0,
                "prev_session_rs": True,
                "session_bet": None,
                "current_session": None,
                "current_betTypeResult": None,
                "current_bet": 0,
                "next_session": None,
                "next_betTypeResult": None,
                "next_bet": 0,
                "gold": 0,
                "total": 0,
                "total_win": 0,
                "total_lose": 0,
                "lose_strick": 0,
                "time_live": 35,
                "time_normal": 50
            }

            while True:
                try:
                    ssl_context = ssl.create_default_context(cafile=certifi.where())
                    async with websockets.connect(uri, ping_interval=2, ssl=ssl_context, ping_timeout=15) as websocket:
                        payload = self.login_data[username][name]
                        await websocket.send(json.dumps(payload))

                        while True:
                            message = await websocket.recv()
                            try:
                                data = json.loads(message)
                                if name == "balance":
                                    if site == "sunwin":
                                        data_get_balance = json.dumps([6, "Simms", "channelPlugin", {"cmd": 310}])
                                    elif site == "hitclub":
                                        data_get_balance = json.dumps([6, "Simms", "channelPlugin", {"cmd": 310}])
                                    await websocket.send(data_get_balance)
                                    if data[0] == 5 and data[1]["cmd"] == 310:
                                        current_gold = int(data[1]["As"]["gold"])
                                        if current_gold != self.previous_gold:
                                            self.write_data(path, str(round(current_gold)))
                                        #     # print("đã ghi")
                                        # else:
                                        #     print("ko thay đổi")
                                        self.previous_gold = current_gold
                                await asyncio.sleep(1)
                            except json.JSONDecodeError as e:
                                print(f"Failed to decode JSON: {e}")
                except InvalidStatusCode as e:
                    print(f"Server từ chối kết nối WebSocket: {e}. Thử lại...")
                    await asyncio.sleep(5)
                except websockets.ConnectionClosed as e:
                    await asyncio.sleep(1)
                    continue

        except asyncio.CancelledError:
            print("Main has been cancelled")

    async def main(self, login_data):
        tasks = []
        username = list(login_data.keys())[0]
        if login_data[username]["status"] == True:
            option = login_data[username]["option"]
            site = login_data[username]["site"]
            path = login_data[username]["path"]
            if site == "sunwin":
                balance = "wss://websocket.azhkthg1.net/websocket4"
                await self.connect_and_communicate(balance, "balance", username, option, site, path)
            elif site == "hitclub":
                balance = "wss://carkgwaiz.hytsocesk.com/websocket"
                await self.connect_and_communicate(balance, "balance", username, option, site, path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--data', type=str, required=True, help='an integer for the balance amount')
    args = parser.parse_args()
    params = json.loads(args.data)
    client = WebSocketClient(params)
    asyncio.run(client.main(params))