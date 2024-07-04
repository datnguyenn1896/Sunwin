import asyncio
import websockets
import json
import certifi
import ssl
import logging
from telegram import Bot
import tracemalloc


tracemalloc.start()

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

def write_data(data):
    with open('login-4.txt', 'a', encoding='utf-8') as file:
        file.write(data)

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

def send_test_message(chat_id, message):
        bot = Bot(token="7337195716:AAHFpNJk6OrbRZU-2vcLfRarAKyXU2mXCaI")
        try:
            bot.send_message(chat_id=chat_id, text=message,
                             parse_mode='Markdown')
        except Exception as ex:
            print(ex)

previous_session = None

status_bet = False
# dự đoán
result_next_seesion = None
# Số tiền bet
monneyB = 0
bet = False
gold = 0

data_status = {}

# Tắt toàn bộ logging
logging.basicConfig(level=logging.CRITICAL)

async def connect_and_communicate(uri, name, username, option, site):
    try:
        data_status[username] = {"status":"wait_end_session",
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
                "lose_strick" : 0,
                "time_live":35,
                "time_normal":50
                }
    
        global data, previous_session
        while True:
            try:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                async with websockets.connect(uri, ping_interval=1, ssl=ssl_context, ping_timeout=15) as websocket:
                    payload = json.loads(login)
                    # print(payload)
                    await websocket.send(json.dumps(payload[username][name]))
                    await websocket.send(json.dumps(payload[username][name]))
                    bot = Bot(token="7337195716:AAHFpNJk6OrbRZU-2vcLfRarAKyXU2mXCaI")
                    if name == "live":
                        time = data_status[username]["time_live"]
                    else:
                        time = data_status[username]["time_normal"]

                    # print(f"Sent message: {payload}")
                    while True:
                        message = await websocket.recv()
                        # print(f"Received message: {message}")
                        
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
                                    data_status[username]["gold"] = int(data[1]["As"]["gold"])


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
                                asyncio.create_task(send_ping(websocket))
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
                                data_status[username]["current_session"] = seasion
                                data_status[username]["next_session"] = seasion + 1
                                if seasion:
                                    if previous_session is None or seasion > data_status[username]["current_session"]:
                                        previous_session = seasion
                                        data_status[username]["prev_session"] = previous_session
                                        # print(f"Đang chờ kết thúc phiên: {previous_session}")
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
                                            
                                            print(data_get_history, name, site)
                                            await websocket.send(data_get_history)
                                            # print(sid)

                                    elif seasion != previous_session:
                                        if data_status[username]["status"] != "wait_result_bet":
                                            data_status[username]["status"] = "next_session"
                                        previous_session = seasion
                                        if name == "live":
                                            time = data_status[username]["time_live"]
                                        elif name == "normal":
                                            time = data_status[username]["time_normal"]

                                time -= 1
                                gold = data_status[username]["gold"]
                                # print(f"Phiên: #{seasion} - Thời gian: {time} TK:{username} - TÀI: Số người: {userB} / Số tiền: {betB} - XỈU: {userS} / Số tiền: {betS} - Tài khoản: {f'{gold:,}'}")
                                # print(data_status[username]["status"])
                            
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
                                add_to_dict(sid, resultB)
                                # print("chạy vào đây", sid)
                                if sid == data_status[username]["prev_session"]:
                                    # data_status[username]["status"] = "next_session"
                                    data_status[username]["next_session"] = sid + 1
                                data_status[username]["prev_session_rs"] = True

                                

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

                                add_to_dict(sid, resultB)
                                if sid == data_status[username]["prev_session"]:
                                    # data_status[username]["status"] = "next_session"
                                    data_status[username]["next_session"] = sid + 1
                                data_status[username]["prev_session_rs"] = True

                            if name != "balance" and data_status[username]["status"] == "wait_result_bet" and (data_status[username]["session_bet"] in dict_result):
                                session_bet = data_status[username]["session_bet"]
                                # Dự đoán
                                current_betTypeResult = data_status[username]["current_betTypeResult"]
                                current_bet = data_status[username]["current_bet"]
                        
                                # Kết quả
                                betTypeResult =dict_result[data_status[username]["session_bet"]]
                                data_status[username]["total"] += 1
                                if current_betTypeResult == betTypeResult:
                                    status = "\U0001F525 WIN"
                                    data_status[username]["total_win"] += 1
                                    data_status[username]["lose_strick"] = 0
                                    gold += current_bet + current_bet * 99/100
                                else:
                                    status = "\U0001F32A LOSE"
                                    data_status[username]["total_lose"] += 1
                                    data_status[username]["lose_strick"] += 1
                                    gold -= current_bet

                                total = data_status[username]["total"]
                                total_win = data_status[username]["total_win"]
                                total_lose = data_status[username]["total_lose"]

                                if current_betTypeResult == "T" and option == "livecl":
                                    type_bet = "C"
                                elif current_betTypeResult == "X" and option == "livecl":
                                    type_bet = "L"
                                else:
                                    type_bet = current_betTypeResult
                                message = f"\U0001F680 #{session_bet} - TK: {username} - BET: {type_bet} - {f'{current_bet:,}'} - KQ: {betTypeResult} - {status} - TOTAL: {total} - WIN: {total_win} - LOSE: {total_lose} - \U0001F4B5: {f'{gold:,}'}"
                                print(message)
                                send_test_message(chat_id, message)
                                # asyncio.run(send_test_message(chat_id, message))

                                write_data(str(gold))

                                data_status[username]["status"] = "next_session"
                                data_status["prev_session_rs"] = True

                                data_status[username]["session_bet"] = None
                                data_status[username]["current_betTypeResult"] = None
                                data_status[username]["current_bet"] = None

                            elif data_status[username]["session_bet"] != None and data_status[username]["current_session"] > data_status[username]["session_bet"]:
                                await asyncio.sleep(1)
                                if site == "sunwin":
                                    if name == "live":
                                        data_get_history = json.dumps([6,"Livestream","TaiXiuLivestreamPlugin",{"cmd":1965,"sid":data_status[username]["session_bet"]}])
                                    elif name == "normal":
                                        data_get_history = json.dumps([6,"MiniGame","taixiuPlugin",{"cmd":1007,"sid":data_status[username]["session_bet"],"aid":1}])
                                elif site == "hitclub":
                                    if name == "normal":
                                        data_get_history = json.dumps(["6","MiniGame","taixiuPlugin",{"cmd":"1007","sid":data_status[username]["session_bet"],"aid":"1"}]	)
 
                                await websocket.send(data_get_history)

                            # Dự đoán phiên tiếp theo
                            if data_status[username]["status"] == "next_session" and data_status[username]["prev_session_rs"]:
                                history = ""
                                for line in str(payload[username]["fortune"]).split(","):
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
                                    lose_strick = data_status[username]["lose_strick"]

                                    if lose_strick == len(payload[username]["fund"].split(",")):
                                        data_status[username]["lose_strick"] = 0
                                        lose_strick = 0
                                        monneyB = int(payload[username]["fund"].split(",")[lose_strick])
                                    else:
                                        monneyB = int(payload[username]["fund"].split(",")[lose_strick])

                                    # # In kết quả
                                    if result_next_seesion:
                                        data_status[username]["status"] = "wait_bet"
                                        data_status[username]["next_betTypeResult"] = result_next_seesion
                                        data_status[username]["next_bet"] = monneyB
                                        # print(f"Dự đoán phiên tiếp theo là: {result_next_seesion} - BET: {monneyB}")
                                        break
                        
                            if name == "live":
                                time_in_bet = data_status[username]["time_live"] - 2
                            else:
                                time_in_bet = data_status[username]["time_normal"] - 2

                            if time == time_in_bet and data_status[username]["status"] == "wait_bet":
                                seasion = data_status[username]["current_session"]
                                next_betTypeResult = data_status[username]["next_betTypeResult"]

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
                                        data_bet = json.dumps([6,"MiniGame","taixiuPlugin",{"cmd":1000,"b":data_status[username]["next_bet"],"aid":1,"sid":seasion,"eid":eid}])
                                    elif name == "live":
                                        data_bet = json.dumps([6,"Livestream","TaiXiuLivestreamPlugin",{"cmd":1952,"b":data_status[username]["next_bet"],"eid":eid,"sid":seasion}])
                                elif site == "hitclub":
                                    if name == "normal":
                                        data_bet = json.dumps(["6","MiniGame","taixiuPlugin",{"cmd":1000,"b":data_status[username]["next_bet"],"sid":seasion,"aid":1,"eid":eid,"sqe":False,"a":False}])

                                await websocket.send(data_bet)
                                next_bet = data_status[username]["next_bet"]

                                if next_betTypeResult == "T" and option == "livecl":
                                    type_bet = "C"
                                elif next_betTypeResult == "X" and option == "livecl":
                                    type_bet = "L"
                                else:
                                    type_bet = next_betTypeResult

                                print(f"Phiên: #{seasion} - TK: {username} - Thời gian: {time} - BET: {type_bet}: {f'{next_bet:,}'}")

                                data_status[username]["status"] = "wait_result_bet"
                                data_status[username]["session_bet"] = seasion
                                data_status[username]["current_bet"] = next_bet
                                data_status[username]["current_betTypeResult"] = next_betTypeResult

                                data_status[username]["next_session"] = None
                                data_status[username]["next_betTypeResult"] = None
                                data_status[username]["next_bet"] = 0
                                data_status[username]["prev_session_rs"] = False
                            # Mở file ở chế độ 'a' (append) để ghi thêm dữ liệu
                            # print(data)
                            append_if_data_changes(str(data_status[username]) + str(dict_result))
                            # await asyncio.sleep(1)
                        except json.JSONDecodeError as e:
                            print(f"Failed to decode JSON: {e}")

            except websockets.ConnectionClosed as e:
                # print(f"Connection closed unexpectedly: {e}")
                # Thực hiện lại kết nối tại đây, có thể sử dụng vòng lặp while hoặc asyncio.sleep để tái kết nối
                await asyncio.sleep(1)  # Chờ 5 giây trước khi tái kết nối
                continue
    except asyncio.CancelledError:
        print("Main has been cancelled")
    

async def async_task(name, delay):
    print(f"Task {name} started")
    await asyncio.sleep(delay)
    print(f"Task {name} completed")

async def main(login):
    # Chế độ
    # Bình thường: normal
    # Livestream: live
    data_json =json.loads(login)
    # Chạy chương trình
    # Địa chỉ WebSocket server
    

    tasks = []
    # Chờ cả hai tác vụ hoàn thành
    for username in data_json:
        if data_json[username]["status"] == True:
            option = data_json[username]["option"]
            site = data_json[username]["site"]
            if site == "sunwin":
                live = "wss://ws-taixiu-ls.azhkthg1.com/websocket"
                balance = "wss://websocket.azhkthg1.net/websocket4"
                normal = "wss://websocket.azhkthg1.net/websocket"
                if option == "livetx" or option == "livecl":
                    # Tạo các tác vụ kết nối đến hai WebSocket server
                    task1 = asyncio.create_task(connect_and_communicate(live, "live", username, option, site))
                    task2 = asyncio.create_task(connect_and_communicate(balance, "balance", username, option, site))
                elif option == "normal":
                    task1 = asyncio.create_task(connect_and_communicate(normal, "normal", username, option, site))
                    task2 = asyncio.create_task(connect_and_communicate(balance, "balance", username, option, site))
            elif site == "hitclub":
                live = "wss://ws-taixiu-ls.azhkthg1.com/websocket"
                balance = "wss://carkgwaiz.hytsocesk.com/websocket"
                normal = "wss://mynygwais.hytsocesk.com/websocket"
                if option == "livetx" or option == "livecl":
                    # Tạo các tác vụ kết nối đến hai WebSocket server
                    task1 = asyncio.create_task(connect_and_communicate(live, "live", username, option, site))
                    task2 = asyncio.create_task(connect_and_communicate(balance, "balance", username, option, site))
                elif option == "normal":
                    task1 = asyncio.create_task(connect_and_communicate(normal, "normal", username, option, site))
                    task2 = asyncio.create_task(connect_and_communicate(balance, "balance", username, option, site))

            tasks.append(task1)
            tasks.append(task2)
    await asyncio.gather(*tasks)

with open('login-4.json', 'r') as file:
    login = file.read()

if __name__ == "__main__":
    asyncio.run(main(login))