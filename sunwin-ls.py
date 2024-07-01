import asyncio
import websockets
import json
import certifi
import ssl
import logging
from telegram import Bot

def get_next_char(sequence, substring):
    # Kiểm tra độ dài chuỗi con
    sub_len = len(substring)

    if len(sequence) - sub_len == 1:
        # raise ValueError("Độ dài chuỗi con phải nhỏ hơn độ dài chuỗi đầu vào.")
    
        # Kiểm tra xem chuỗi con có khớp với phần đầu của chuỗi đầu vào không
        if sequence[:sub_len] == substring:
            return sequence[sub_len]
    return None

old_data = None

def append_if_data_changes(data):
    global old_data
    if old_data is None:
        old_data = data
    elif old_data != data:
        with open('example.txt', 'a', encoding='utf-8') as file:
            file.write(data + "\n")
        old_data = data  # Cập nhật old_data sau khi ghi vào file

dict_result = {}
def add_to_dict(key, value):
    # Thêm phần tử mới vào từ điển
    dict_result[key] = value
    
    # Nếu số phần tử trong từ điển vượt quá 10, xóa phần tử đầu tiên
    if len(dict_result) > 10:
        # Lấy danh sách các khóa của từ điển
        keys = list(dict_result.keys())
        # Xóa phần tử đầu tiên
        del dict_result[keys[0]]

def get_top_n_items(n):
    # Sắp xếp các phần tử trong từ điển theo key giảm dần
    sorted_items = sorted(dict_result.items(), key=lambda item: item[0], reverse=True)
    
    # Lấy n phần tử đầu tiên trong danh sách đã sắp xếp
    top_n_items = sorted_items[:n]
    
    # Đảo ngược danh sách các phần tử đã chọn từ lớn đến bé
    top_n_items_reversed = top_n_items[::-1]
    return top_n_items_reversed

async def send_ping(websocket):
    while True:
        try:
            await websocket.ping()
            # print("Sent ping")
        except websockets.ConnectionClosed:
            # print("Connection closed unexpectedly, reconnecting...")
            break
        await asyncio.sleep(1)  # Gửi ping sau mỗi 10 giây

def send_test_message(message):
        chat_id = "-4248092135"
        bot = Bot(token="7337195716:AAHFpNJk6OrbRZU-2vcLfRarAKyXU2mXCaI")
        try:
            bot.send_message(chat_id=chat_id, text=message,
                             parse_mode='Markdown')
        except Exception as ex:
            print(ex)


previous_session = None
time = 35

status_bet = False
# dự đoán
result_next_seesion = None
# Số tiền bet
monneyB = 0
bet = False
gold = 0

data_status = {"status":"wait_end_session",
               "prev_session":None,
               "prev_bet": 0,
               "prev_session_rs": True,
               "session_bet":None,
               "current_session":None,
               "current_betTypeResult":None,
               "current_bet":0,
               "next_session": None,
               "next_betTypeResult": None,
               "next_bet": 0,
               "gold": 0,
               "total" : 0,
               "total_win" : 0,
               "total_lose" : 0,
               "lose_strick" : 0}

with open('login.json', 'r') as file:
    login = file.read()

with open('settings.json', 'r', encoding='utf-8') as file:
    settings = file.read()

with open('fund.txt', 'r') as file:
    fund = file.read()

# Tắt toàn bộ logging
logging.basicConfig(level=logging.CRITICAL)

async def connect_and_communicate(uri, name):
    global time, data, previous_session

    while True:
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            async with websockets.connect(uri, ping_interval=1, ssl=ssl_context, ping_timeout=5) as websocket:
                payload = json.loads(login)
                await websocket.send(json.dumps(payload[name]))
                await websocket.send(json.dumps(payload[name]))

                # print(f"Sent message: {payload}")
                while True:
                    message = await websocket.recv()
                    # print(f"Received message: {message}")
                    try:
                        
                        data = json.loads(message)
                        if data[0]==6:
                            print(data)
                        # Xử lý dữ liệu ở đây
                        if name == "websocket4":
                            data_get_history = json.dumps([6,"Simms","channelPlugin",{"cmd":310}])
                            await websocket.send(data_get_history)
                        
                            if data[0] == 5 and data[1]["cmd"] == 310:
                                data_status["gold"] = int(data[1]["As"]["gold"])

                        # print("Parsed JSON:", data[0], data[1])
                        if data[0] == 1 and data[1] == True:
                            payload_connect_tx = json.dumps([6,"Livestream","TaiXiuLivestreamPlugin",{"cmd":1950,"sC":True}])
                            # print("Connect tài xỉu")
                            await websocket.send(payload_connect_tx)
                            # Khởi động luồng gửi ping định kỳ
                            asyncio.create_task(send_ping(websocket))
                                                # Thêm kết quả vào dict khi nhận đc wss get lịch sử
                        
                        if data[0] == 5 and data[1]["cmd"] == 1957:
                            # print(data[1]["gi"][0])
                            betB = f'{data[1]["bs"][3]["v"]:,}'
                            userB = f'{data[1]["bs"][3]["uC"]:,}'

                            betS = f'{data[1]["bs"][6]["v"]:,}'
                            userS = f'{data[1]["bs"][6]["uC"]:,}'
                            seasion = data[1]["sid"]
                            
                            # Cập nhập seasion hiện tại
                            data_status["current_session"] = seasion
                            data_status["next_session"] = seasion + 1
                            if seasion:
                                if previous_session is None or seasion > data_status["current_session"]:
                                    previous_session = seasion
                                    data_status["prev_session"] = previous_session
                                    # print(f"Đang chờ kết thúc phiên: {previous_session}")
                                    # Get kết quả 10 phiên gần nhất
                                    for sid in range(seasion - 10, seasion):
                                        data_get_history = json.dumps([6,"Livestream","TaiXiuLivestreamPlugin",{"cmd":1965,"sid":sid}])
                                        await websocket.send(data_get_history)
                                        # print(sid)

                                elif seasion != previous_session:
                                    if data_status["status"] != "wait_result_bet":
                                        data_status["status"] = "next_session"
                                    previous_session = seasion
                                    time = 35

                            time -= 1
                            gold = data_status["gold"]
                            # print(f"Phiên: #{seasion} - Thời gian: {time} - TÀI: Số người: {userB} / Số tiền: {betB} - XỈU: {userS} / Số tiền: {betS} - Tài khoản: {f'{gold:,}'}")
                            # print(data_status["status"])

                        # Nhận được message tin nhắn trả kết quả
                        if data[0] == 5 and data[1]["cmd"] == 1965:
                            result = 0
                            for a in data[1]["rs"]:
                                result += int(a)
                            if result >= 11:
                                resultB = "T"
                            else:
                                resultB = "X"
                            sid = data[1]["sid"]
                            add_to_dict(sid, resultB)
                            

                            if sid == data_status["prev_session"]:
                                # data_status["status"] = "next_session"
                                data_status["next_session"] = sid + 1
                            data_status["prev_session_rs"] = True

                        # Nhận được message tin nhắn trả kết quả phiên trước
                        if data[0] == 5 and data[1]["cmd"] == 1956:
                            result = str(data[1]["betTypeResult"]).split(",")[0]
                            if result == "BIG":
                                resultB = "T"
                            else:
                                resultB = "X"
                            sid = data[1]["sessionId"]
                            add_to_dict(sid, resultB)
                            if sid == data_status["prev_session"]:
                                # data_status["status"] = "next_session"
                                data_status["next_session"] = sid + 1
                            data_status["prev_session_rs"] = True

                        if data_status["status"] == "wait_result_bet" and (data_status["session_bet"] in dict_result):
                            session_bet = data_status["session_bet"]
                            # Dự đoán
                            current_betTypeResult = data_status["current_betTypeResult"]
                            current_bet = data_status["current_bet"]
                    
                            # Kết quả
                            betTypeResult =dict_result[data_status["session_bet"]]
                            data_status["total"] += 1
                            if current_betTypeResult == betTypeResult:
                                status = "\U0001F525 WIN"
                                data_status["total_win"] += 1
                                data_status["lose_strick"] = 0

                            else:
                                status = "\U0001F32A LOSE"
                                data_status["total_lose"] += 1
                                data_status["lose_strick"] += 1

                            total = data_status["total"]
                            total_win = data_status["total_win"]
                            total_lose = data_status["total_lose"]

                            message = f"\U0001F680 #{session_bet} - BET: {current_betTypeResult} - {f'{current_bet:,}'} - KQ: {betTypeResult} - {status} - TOTAL: {total} - WIN: {total_win} - LOSE: {total_lose} - \U0001F4B5: {f'{gold:,}'}"
                            print(message)
                            send_test_message(message)

                            data_status["status"] = "next_session"
                            data_status["prev_session_rs"] = True

                            data_status["session_bet"] = None
                            data_status["current_betTypeResult"] = None
                            data_status["current_bet"] = None
                        elif data_status["session_bet"] != None and data_status["current_session"] > data_status["session_bet"]:
                            print("chạy vài đây")
                            await asyncio.sleep(1)
                            data_get_history = json.dumps([6,"Livestream","TaiXiuLivestreamPlugin",{"cmd":1965,"sid":data_status["session_bet"]}])
                            await websocket.send(data_get_history)
                        # Dự đoán phiên tiếp theo
                        if data_status["status"] == "next_session" and data_status["prev_session_rs"]:
                            history = ""
                            with open('fortune.txt', 'r', encoding='utf-8') as file:
                                lines = file.readlines()
                                for line in lines:
                                    line = line.strip()
                                    count = len(line) - 1
                                    top_items = get_top_n_items(count)
                                    # In kết quả
                                    for key, value in top_items:
                                        # print(f"{key}: {value}")
                                        history += value
                                    # print(history)
                                    result_next_seesion = get_next_char(line, history)
                                    history = ""
                                    lose_strick = data_status["lose_strick"]
                                    monneyB = int(fund.split(",")[lose_strick])
                                    # # In kết quả
                                    if result_next_seesion:
                                        data_status["status"] = "wait_bet"
                                        data_status["next_betTypeResult"] = result_next_seesion
                                        data_status["next_bet"] = monneyB
                                        # print(f"Dự đoán phiên tiếp theo là: {result_next_seesion} - BET: {monneyB}")
                                        break
                        
                        json_data = json.loads(settings)
                        if time == json_data["time_in_bet"] and data_status["status"] == "wait_bet":
                            seasion = data_status["current_session"]
                            next_betTypeResult = data_status["next_betTypeResult"]
                            if next_betTypeResult == "X":
                                eid = "SMALL"
                            else:
                                eid = "BIG"
                            # print([6,"Livestream","TaiXiuLivestreamPlugin",{"cmd":1952,"b":data_status["next_bet"],"eid":eid,"sid":seasion}])
                            data_bet = json.dumps([6,"Livestream","TaiXiuLivestreamPlugin",{"cmd":1952,"b":data_status["next_bet"],"eid":eid,"sid":seasion}])
                            await websocket.send(data_bet)
                            next_bet = data_status["next_bet"]
                            print(f"Phiên: #{seasion} - Thời gian: {time} - BET: {next_betTypeResult}: {f'{next_bet:,}'}")

                            data_status["status"] = "wait_result_bet"
                            data_status["session_bet"] = seasion
                            data_status["current_bet"] = next_bet
                            data_status["current_betTypeResult"] = next_betTypeResult

                            data_status["next_session"] = None
                            data_status["next_betTypeResult"] = None
                            data_status["next_bet"] = 0
                            data_status["prev_session_rs"] = False
                        # Mở file ở chế độ 'a' (append) để ghi thêm dữ liệu
                        
                        append_if_data_changes(str(data_status) + str(dict_result))
                        # await asyncio.sleep(1)
                    except json.JSONDecodeError as e:
                        print(f"Failed to decode JSON: {e}")

        except websockets.ConnectionClosed as e:
            # print(f"Connection closed unexpectedly: {e}")
            # Thực hiện lại kết nối tại đây, có thể sử dụng vòng lặp while hoặc asyncio.sleep để tái kết nối
            await asyncio.sleep(1)  # Chờ 5 giây trước khi tái kết nối
            continue


async def main():
    # Địa chỉ WebSocket server
    uri1 = "wss://ws-taixiu-ls.azhkthg1.com/websocket"
    uri2 = "wss://websocket.azhkthg1.net/websocket4"

    # Tạo các tác vụ kết nối đến hai WebSocket server
    task1 = asyncio.create_task(connect_and_communicate(uri1, "websocketlive"))
    task2 = asyncio.create_task(connect_and_communicate(uri2, "websocket4"))

    # Chờ cả hai tác vụ hoàn thành
    await asyncio.gather(task1, task2)

# Chạy chương trình
asyncio.run(main())