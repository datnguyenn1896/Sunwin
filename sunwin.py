import asyncio
import websockets
import json
import certifi
import ssl

def get_next_char(sequence, substring):
    # Kiểm tra độ dài chuỗi con
    sub_len = len(substring)

    if len(sequence) - sub_len == 1:
        # raise ValueError("Độ dài chuỗi con phải nhỏ hơn độ dài chuỗi đầu vào.")
    
        # Kiểm tra xem chuỗi con có khớp với phần đầu của chuỗi đầu vào không
        if sequence[:sub_len] == substring:
            return sequence[sub_len]
    return None

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
            print("Connection closed unexpectedly, reconnecting...")
            break
        await asyncio.sleep(2)  # Gửi ping sau mỗi 10 giây
        
previous_session = None
time = 50
total = 0
total_win = 0
total_lose = 0
lose_strick = 0
status_bet = False
# dự đoán
result_next_seesion = None
# Số tiền bet
monneyB = 0
bet = False

with open('login.json', 'r') as file:
    login = file.read()

with open('settings.json', 'r', encoding='utf-8') as file:
    settings = file.read()

with open('fund.txt', 'r') as file:
    fund = file.read()


async def send_message():
    global previous_session, time, settings, bet, fund, result_next_seesion, total, total_win, total_lose, lose_strick, status_bet

    while True:
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            uri = "wss://websocket.azhkthg1.net/websocket"
            async with websockets.connect(uri, ping_interval=2, ssl=ssl_context) as websocket:
                payload = login
                await websocket.send(payload)
                await websocket.send(payload)
                # print(f"Sent message: {payload}")
                while True:
                    message = await websocket.recv()
                    # print(f"Received message: {message}")
                    try:
                        data = json.loads(message)
                        # Xử lý dữ liệu ở đây
                        # print("Parsed JSON:", data[0], data[1])
                        if data[0] == 1 and data[1] == True:
                            payload_connect_tx = json.dumps([6,"MiniGame","taixiuPlugin",{"cmd":1005}])
                            # print("Connect tài xỉu")
                            await websocket.send(payload_connect_tx)
                            # Khởi động luồng gửi ping định kỳ
                            asyncio.create_task(send_ping(websocket))
                                                # Thêm kết quả vào dict khi nhận đc wss get lịch sử

                        if data[0] == 5 and data[1]["cmd"] == 1007:
                            result = data[1]["d1"] + data[1]["d2"] + data[1]["d3"]
                            if result >= 11:
                                resultB = "T"
                            else:
                                resultB = "X"
                            sid = data[1]["sid"]
                            add_to_dict(sid, resultB)
                            # print(dict_result)

                        if data[0] == 5 and data[1]["cmd"] == 1008:
                            # print(data[1]["gi"][0]["B"])
                            
                            betB = f'{data[1]["gi"][0]["B"]["tB"]:,}'
                            userB = f'{data[1]["gi"][0]["B"]["tU"]:,}'

                            betS = f'{data[1]["gi"][0]["S"]["tB"]:,}'
                            userS = f'{data[1]["gi"][0]["S"]["tU"]:,}'
                            seasion = data[1]["sid"]
                            
                            if seasion:
                                if previous_session is None:
                                    previous_session = seasion
                                    print(f"Đang chờ kết thúc phiên: {previous_session}")
                                    # Get kết quả 10 phiên gần nhất
                                    for sid in range(seasion - 10, seasion):
                                        data_get_history = json.dumps([6,"MiniGame","taixiuPlugin",{"cmd":1007,"sid":sid,"aid":1}])
                                        await websocket.send(data_get_history)
                                        # print(sid)

                                elif seasion != previous_session:
                                    if status_bet == False:
                                        bet = True
                                    previous_session = seasion
                                    time = 50
                            time -= 1
                            print(f"Phiên: #{seasion} - Thời gian: {time} - TÀI: Số người: {userB} / Số tiền: {betB} - XỈU: {userS} / Số tiền: {betS}")
                        
                        if data[0] == 5 and data[1]["cmd"] == 1004:
                            result = data[1]["d1"] + data[1]["d2"] + data[1]["d3"]
                            if result >= 11:
                                resultB = "T"
                            else:
                                resultB = "X"
                            add_to_dict(seasion, resultB)
                            status_bet = False

                            print(f"Kết quả phiên: #{seasion} - {resultB} - {result}")
                            if result_next_seesion != None:
                                total += 1
                                if result_next_seesion == resultB:
                                    total_win += 1
                                    lose_strick = 0
                                    print(f"BET: {result_next_seesion} - Kết quả: {resultB} - WIN - Tổng số phiên: {total} - WIN: {total_win} - LOSE: {total_lose}")
                                elif result_next_seesion != resultB:
                                    total_lose += 1
                                    lose_strick += 1
                                    print(f"BET: {result_next_seesion} - Kết quả: {resultB} - LOSE - Tổng số phiên: {total} - WIN: {total_win} - LOSE: {total_lose}")

                            # Dự đoán kết quả
                            # Ví dụ chuỗi đầu vào và chuỗi con để so sánh
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
                                    monneyB = int(fund.split(",")[lose_strick])
                                    # # In kết quả
                                    if result_next_seesion:
                                        print(f"Dự đoán phiên tiếp theo là: {result_next_seesion} - BET: {monneyB}")
                                        break
                                    else:
                                        print(f"Không có cầu nào giống lịch sử hiện tại.")

                        json_data = json.loads(settings)
                        if time == json_data["time_in_bet"] and bet and result_next_seesion:
                            if result_next_seesion == "X":
                                eid = 2
                            else:
                                eid = 1
                            data_bet = json.dumps([6,"MiniGame","taixiuPlugin",{"cmd":1000,"b":monneyB,"aid":1,"sid":seasion,"eid":eid}])
                            await websocket.send(data_bet)
                            bet = False
                            status_bet = True

                            print(f"Phiên: #{seasion} - Thời gian: {time} - BET: {result_next_seesion}: {f'{monneyB:,}'}")
                        if data[0] == 5 and data[1]["cmd"] == 1002:
                            try:
                                mgs = data[1]["mgs"]
                                print(mgs)
                            except:
                                print("")

                    except json.JSONDecodeError as e:
                        print(f"Failed to decode JSON: {e}")

        except websockets.ConnectionClosed as e:
            print(f"Connection closed unexpectedly: {e}")
            # Thực hiện lại kết nối tại đây, có thể sử dụng vòng lặp while hoặc asyncio.sleep để tái kết nối
            await asyncio.sleep(2)  # Chờ 5 giây trước khi tái kết nối
            continue

asyncio.get_event_loop().run_until_complete(send_message())
