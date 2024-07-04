import asyncio
import websockets
import json
import certifi
import ssl
import logging
from telegram import Bot
import tracemalloc
from websockets.exceptions import InvalidStatusCode
import requests
import argparse

tracemalloc.start()
# Tắt toàn bộ logging
logging.basicConfig(level=logging.CRITICAL)

class WebSocketBot:
    def __init__(self, login_data):
        self.old_data = None
        self.dict_result = {}
        self.previous_session = None
        self.gold = 0
        self.data_status = {}
        self.previous_gold = None
        self.login_data = login_data

    def initialize_data_status(self):
        return {
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

    def get_next_char(self, sequence, substring):
        sub_len = len(substring)
        if len(sequence) - sub_len == 1:
            if sequence[:sub_len] == substring:
                return sequence[sub_len]
        return None

    def append_if_data_changes(self, data):
        global old_data
        if old_data is None:
            old_data = data
        elif old_data != data:
            with open('example.txt', 'a', encoding='utf-8') as file:
                file.write(data + "\n")
            old_data = data

    def add_to_dict(self, key, value):
        self.dict_result[key] = value
        if len(self.dict_result) > 10:
            keys = list(self.dict_result.keys())
            del self.dict_result[keys[0]]

    def get_top_n_items(self, n):
        sorted_items = sorted(self.dict_result.items(), key=lambda item: item[0], reverse=True)
        top_n_items = sorted_items[:n]
        return top_n_items[::-1]

    async def send_ping(self, websocket):
        while True:
            try:
                await websocket.ping()
            except websockets.ConnectionClosed:
                break
            await asyncio.sleep(1)

    def send_message(self, chat_id, text):
        api_key = "7337195716:AAHFpNJk6OrbRZU-2vcLfRarAKyXU2mXCaI"
        url = f'https://api.telegram.org/bot{api_key}/sendMessage'
        payload = {'chat_id': chat_id, 'text': text}
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print("Error:", e)

    async def connect_and_communicate(self, uri, name, username, option, site, path):
        self.data_status[username] = self.initialize_data_status()
        while True:
            try:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                async with websockets.connect(uri, ping_interval=2, ssl=ssl_context, ping_timeout=15) as websocket:
                    await websocket.send(json.dumps(self.login_data[username][name]))
                    if name == "live":
                        time = self.data_status[username]["time_live"]
                    else:
                        time = self.data_status[username]["time_normal"]

                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        # Handle your data here...
                        try: 
                            data = json.loads(message)
                            if site == "sunwin":
                                chat_id = "-4248092135"
                            elif site == "hitclub":
                                chat_id = "-4232039520"
                            # Xử lý dữ liệu ở đây
                            if name == "balance":
                                if site == "sunwin":
                                    data_get_balance = json.dumps([6,"Simms","channelPlugin",{"cmd":310}])
                                elif site == "hitclub":
                                    data_get_balance = json.dumps([6,"Simms","channelPlugin",{"cmd":310}])
                                await websocket.send(data_get_balance)
                                if data[0] == 5 and data[1]["cmd"] == 310:
                                    self.data_status[username]["gold"] = int(data[1]["As"]["gold"])

                            # Connect server live
                            if (name == "live" or name == "normal") and data[0] == 1 and data[1] == True:
                                if site == "sunwin":
                                    if name == "live":
                                        payload_connect_tx = json.dumps([6,"Livestream","TaiXiuLivestreamPlugin",{"cmd":1950,"sC":True}])
                                    elif name == "normal":
                                        payload_connect_tx = json.dumps([6,"MiniGame","taixiuPlugin",{"cmd":1005}])
                                elif site == "hitclub":
                                    if name == "live":
                                        payload_connect_tx = json.dumps(["6","MiniGame","taiXiuLiveTipPlugin",{"cmd":7511}])
                                    elif name == "normal":
                                        payload_connect_tx = json.dumps(["6", "MiniGame", "taixiuPlugin", {"cmd": 1005}])
                                        
                                # print("Connect tài xỉu")
                                await websocket.send(payload_connect_tx)
                                # Khởi động luồng gửi ping định kỳ
                                asyncio.create_task(self.send_ping(websocket))
                                # Thêm kết quả vào dict khi nhận đc wss get lịch sử

                            if data[0] == 5 and (data[1]["cmd"] == 1957 or data[1]["cmd"] == 1008 ):
                                if data[1]["cmd"] == 1957:
                                    # print(data[1]["gi"][0])
                                    betB = f'{data[1]["bs"][3]["v"]:,}'
                                    userB = f'{data[1]["bs"][3]["uC"]:,}'

                                    betS = f'{data[1]["bs"][6]["v"]:,}'
                                    userS = f'{data[1]["bs"][6]["uC"]:,}'
                                    seasion = data[1]["sid"]
                                    seasion = data[1]["sid"]
                                elif data[1]["cmd"] == 1008:
                                    seasion = data[1]["sid"]
                                    betB = f'{data[1]["gi"][0]["B"]["tB"]:,}'
                                    userB = f'{data[1]["gi"][0]["B"]["tU"]:,}'
                                    betS = f'{data[1]["gi"][0]["S"]["tB"]:,}'
                                    userS = f'{data[1]["gi"][0]["S"]["tU"]:,}'

                                # Cập nhập seasion hiện tại
                                self.data_status[username]["current_session"] = seasion
                                self.data_status[username]["next_session"] = seasion + 1
                                if seasion:
                                    if self.previous_session is None or seasion > self.data_status[username]["current_session"]:
                                        self.previous_session = seasion
                                        self.data_status[username]["prev_session"] = self.previous_session
                                        # print(f"Đang chờ kết thúc phiên: {self.previous_session}")
                                        # Get kết quả 10 phiên gần nhất
                                        for sid in range(seasion - 10, seasion):
                                            if site == "sunwin":
                                                if name == "live":
                                                    data_get_history = json.dumps([6,"Livestream","TaiXiuLivestreamPlugin",{"cmd":1965,"sid":sid}])
                                                elif name == "normal":
                                                    data_get_history = json.dumps([6,"MiniGame","taixiuPlugin",{"cmd":1007,"sid":sid,"aid":1}])
                                            elif site == "hitclub":
                                                if name == "normal":
                                                    data_get_history = json.dumps(["6","MiniGame","taixiuPlugin",{"cmd":"1007","sid":sid,"aid":"1"}])

                                            await websocket.send(data_get_history)
                                            # print(sid)

                                    elif seasion != self.previous_session:
                                        if self.data_status[username]["status"] != "wait_result_bet":
                                            self.data_status[username]["status"] = "next_session"
                                        self.previous_session = seasion
                                        if name == "live":
                                            time = self.data_status[username]["time_live"]
                                        elif name == "normal":
                                            time = self.data_status[username]["time_normal"]

                                time -= 1
                                # Mở file ở chế độ đọc ('r')
                                with open(path + '.txt', 'r', encoding='utf-8') as file:
                                    # Đọc toàn bộ nội dung của file
                                    gold = int(file.read())
                                    # In ra nội dung đã đọc
                                    # print(gold)
                                # print(f"Phiên: #{seasion} - Thời gian: {time} TK:{username} - TÀI: Số người: {userB} / Số tiền: {betB} - XỈU: {userS} / Số tiền: {betS} - Tài khoản: {f'{gold:,}'}")
                                # print(self.data_status[username]["status"])
                            
                            # Nhận được message tin nhắn khi get kết quả (giống nhau)
                            if data[0] == 5 and (data[1]["cmd"] == 1965 or data[1]["cmd"] == 1007):
                                result = 0
                                # live
                                if data[1]["cmd"] == 1965:
                                    for a in data[1]["rs"]:
                                        result += int(a)
                                # normal
                                elif data[1]["cmd"] == 1007:
                                    result = data[1]["d1"] + data[1]["d2"] + data[1]["d3"]

                                if option == "livetx" or option == "normal":
                                    if result >= 11:
                                        resultB = "T"
                                    else:
                                        resultB = "X"
                                elif option == "livecl":
                                    if result % 2 == 0:
                                        resultB = "T"
                                    else:
                                        resultB = "X"

                                sid = data[1]["sid"]
                                self.add_to_dict(sid, resultB)
                                # print("chạy vào đây", sid)
                                if sid == self.data_status[username]["prev_session"]:
                                    # self.data_status[username]["status"] = "next_session"
                                    self.data_status[username]["next_session"] = sid + 1
                                self.data_status[username]["prev_session_rs"] = True

                                

                            # Nhận được message tin nhắn trả kết quả phiên trước (Giống nhau)
                            if data[0] == 5 and (data[1]["cmd"] == 1956 or data[1]["cmd"] == 1004):
                                # live
                                if data[1]["cmd"] == 1956:
                                    if option == "livetx":
                                        result = str(data[1]["betTypeResult"]).split(",")[0]
                                        if result == "BIG" :
                                            resultB = "T"
                                        else:
                                            resultB = "X"
                                    elif option == "livecl":
                                        result = str(data[1]["betTypeResult"]).split(",")[1]
                                        if result == "EVEN" :
                                            resultB = "T"
                                        else:
                                            resultB = "X"
                                    sid = data[1]["sessionId"]
                                # normal
                                elif data[1]["cmd"] == 1004:
                                    result = data[1]["d1"] + data[1]["d2"] + data[1]["d3"]
                                    if result >= 11:
                                        resultB = "T"
                                    else:
                                        resultB = "X"
                                    sid = seasion

                                self.add_to_dict(sid, resultB)
                                if sid == self.data_status[username]["prev_session"]:
                                    # self.data_status[username]["status"] = "next_session"
                                    self.data_status[username]["next_session"] = sid + 1
                                self.data_status[username]["prev_session_rs"] = True

                            if name != "balance" and self.data_status[username]["status"] == "wait_result_bet" and (self.data_status[username]["session_bet"] in self.dict_result):
                                session_bet = self.data_status[username]["session_bet"]
                                # Dự đoán
                                current_betTypeResult = self.data_status[username]["current_betTypeResult"]
                                current_bet = self.data_status[username]["current_bet"]
                        
                                # Mở file ở chế độ đọc ('r')
                                with open(path + '.txt', 'r', encoding='utf-8') as file:
                                    # Đọc toàn bộ nội dung của file
                                    gold = int(file.read())
                                    # In ra nội dung đã đọc
                                    # print(gold)

                                # Kết quả
                                betTypeResult = self.dict_result[self.data_status[username]["session_bet"]]
                                self.data_status[username]["total"] += 1
                                if current_betTypeResult == betTypeResult:
                                    status = "\U0001F525 WIN"
                                    self.data_status[username]["total_win"] += 1
                                    self.data_status[username]["lose_strick"] = 0
                                    gold += current_bet + current_bet * 99/100
                                else:
                                    status = "\U0001F32A LOSE"
                                    self.data_status[username]["total_lose"] += 1
                                    self.data_status[username]["lose_strick"] += 1
                                    gold -= current_bet

                                total = self.data_status[username]["total"]
                                total_win = self.data_status[username]["total_win"]
                                total_lose = self.data_status[username]["total_lose"]

                                if current_betTypeResult == "T" and option == "livecl":
                                    type_bet = "C"
                                elif current_betTypeResult == "X" and option == "livecl":
                                    type_bet = "L"
                                else:
                                    type_bet = current_betTypeResult


                                message = f"\U0001F680 #{session_bet} - TK: {username} - BET: {type_bet} - {f'{current_bet:,}'} - KQ: {betTypeResult} - {status} - TOTAL: {total} - WIN: {total_win} - LOSE: {total_lose} - \U0001F4B5: {f'{gold:,}'}"
                                print(message)
                                self.send_message(chat_id, message)
                                # asyncio.run(send_test_message(chat_id, message))

                                self.data_status[username]["status"] = "next_session"
                                self.data_status["prev_session_rs"] = True

                                self.data_status[username]["session_bet"] = None
                                self.data_status[username]["current_betTypeResult"] = None
                                self.data_status[username]["current_bet"] = None

                            elif self.data_status[username]["session_bet"] != None and self.data_status[username]["current_session"] > self.data_status[username]["session_bet"] and name != "balance":
                                await asyncio.sleep(1)
                                if site == "sunwin":
                                    if name == "live":
                                        data_get_history = json.dumps([6,"Livestream","TaiXiuLivestreamPlugin",{"cmd":1965,"sid":self.data_status[username]["session_bet"]}])
                                    elif name == "normal":
                                        data_get_history = json.dumps([6,"MiniGame","taixiuPlugin",{"cmd":1007,"sid":self.data_status[username]["session_bet"],"aid":1}])
                                elif site == "hitclub":
                                    if name == "normal":
                                        data_get_history = json.dumps(["6","MiniGame","taixiuPlugin",{"cmd":"1007","sid":self.data_status[username]["session_bet"],"aid":"1"}]	)

                                await websocket.send(data_get_history)

                            # Dự đoán phiên tiếp theo
                            if self.data_status[username]["status"] == "next_session" and self.data_status[username]["prev_session_rs"]:
                                history = ""
                                for line in str(self.login_data[username]["fortune"]).split(","):
                                    line = line.strip()
                                    count = len(line) - 1
                                    top_items = self.get_top_n_items(count)
                                    # In kết quả
                                    for key, value in top_items:
                                        # print(f"{key}: {value}")
                                        history += value
                                    # print(history)
                                    result_next_seesion = self.get_next_char(line, history)
                                    history = ""
                                    lose_strick = self.data_status[username]["lose_strick"]

                                    if lose_strick == len(self.login_data[username]["fund"].split(",")):
                                        self.data_status[username]["lose_strick"] = 0
                                        lose_strick = 0
                                        monneyB = int(self.login_data[username]["fund"].split(",")[lose_strick])
                                    else:
                                        monneyB = int(self.login_data[username]["fund"].split(",")[lose_strick])

                                    # # In kết quả
                                    if result_next_seesion:
                                        self.data_status[username]["status"] = "wait_bet"
                                        self.data_status[username]["next_betTypeResult"] = result_next_seesion
                                        self.data_status[username]["next_bet"] = monneyB
                                        # print(f"Dự đoán phiên tiếp theo là: {result_next_seesion} - BET: {monneyB}")
                                        break
                        
                            if name == "live":
                                time_in_bet = self.data_status[username]["time_live"] - 2
                            else:
                                time_in_bet = self.data_status[username]["time_normal"] - 2

                            if time == time_in_bet and self.data_status[username]["status"] == "wait_bet":
                                seasion = self.data_status[username]["current_session"]
                                next_betTypeResult = self.data_status[username]["next_betTypeResult"]

                                # Xỉu lẻ Tài chẵn (Giống nhau)
                                if next_betTypeResult == "X":
                                    if name == "live":
                                        if option == "livetx":
                                            eid = "SMALL"
                                        elif option == "livecl":
                                            eid = "ODD"
                                    elif name == "normal":
                                        eid = 2
                                else:
                                    if name == "live":
                                        if option == "livetx":
                                            eid = "BIG"
                                        elif option == "livecl":
                                            eid = "EVEN"
                                    elif name == "normal":
                                        eid = 1

                                if site == "sunwin":
                                    if name == "normal":
                                        data_bet = json.dumps([6,"MiniGame","taixiuPlugin",{"cmd":1000,"b":self.data_status[username]["next_bet"],"aid":1,"sid":seasion,"eid":eid}])
                                    elif name == "live":
                                        data_bet = json.dumps([6,"Livestream","TaiXiuLivestreamPlugin",{"cmd":1952,"b":self.data_status[username]["next_bet"],"eid":eid,"sid":seasion}])
                                elif site == "hitclub":
                                    if name == "normal":
                                        data_bet = json.dumps(["6","MiniGame","taixiuPlugin",{"cmd":1000,"b":self.data_status[username]["next_bet"],"sid":seasion,"aid":1,"eid":eid,"sqe":False,"a":False}])

                                await websocket.send(data_bet)
                                next_bet = self.data_status[username]["next_bet"]

                                if next_betTypeResult == "T" and option == "livecl":
                                    type_bet = "C"
                                elif next_betTypeResult == "X" and option == "livecl":
                                    type_bet = "L"
                                else:
                                    type_bet = next_betTypeResult

                                print(f"Phiên: #{seasion} - TK: {username} - Thời gian: {time} - BET: {type_bet}: {f'{next_bet:,}'}")

                                self.data_status[username]["status"] = "wait_result_bet"
                                self.data_status[username]["session_bet"] = seasion
                                self.data_status[username]["current_bet"] = next_bet
                                self.data_status[username]["current_betTypeResult"] = next_betTypeResult

                                self.data_status[username]["next_session"] = None
                                self.data_status[username]["next_betTypeResult"] = None
                                self.data_status[username]["next_bet"] = 0
                                self.data_status[username]["prev_session_rs"] = False
                            # Mở file ở chế độ 'a' (append) để ghi thêm dữ liệu
                            # print(data)
                            # append_if_data_changes(str(data_status[username]) + str(dict_result))
                            # await asyncio.sleep(1)
                        except json.JSONDecodeError as e:
                            print(f"Failed to decode JSON: {e}")
            except InvalidStatusCode as e:
                print(f"Server từ chối kết nối WebSocket: {e}. Thử lại...")
                await asyncio.sleep(5)
            except websockets.ConnectionClosed as e:
                await asyncio.sleep(1)
                continue

    async def main(self, login_data):
        tasks = []
        username = list(login_data.keys())[0]
        if login_data[username]["status"] == True:
            option = login_data[username]["option"]
            site = login_data[username]["site"]
            path = login_data[username]["path"]
            if site == "sunwin":
                live = "wss://ws-taixiu-ls.azhkthg1.com/websocket"
                balance = "wss://websocket.azhkthg1.net/websocket4"
                normal = "wss://websocket.azhkthg1.net/websocket"
            elif site == "hitclub":
                live = "wss://ws-taixiu-ls.azhkthg1.com/websocket"
                balance = "wss://carkgwaiz.hytsocesk.com/websocket"
                normal = "wss://mynygwais.hytsocesk.com/websocket"
            if option == "livetx" or option == "livecl":
                await self.connect_and_communicate(live, "live", username, option, site, path)
            elif option == "normal":
                await self.connect_and_communicate(normal, "normal", username, option, site, path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--data', type=str, required=True, help='an integer for the balance amount')
    args = parser.parse_args()
    params = json.loads(args.data)
    client = WebSocketBot(params)
    asyncio.run(client.main(params))