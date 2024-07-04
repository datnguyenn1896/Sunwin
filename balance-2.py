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

def write_data(data):
    with open('login-2.txt', 'w', encoding='utf-8') as file:
        file.write(data)


async def send_ping(websocket):
    while True:
        try:
            await websocket.ping()
            # print("Sent ping")
        except websockets.ConnectionClosed:
            # print("Connection closed unexpectedly, reconnecting...")
            break
        await asyncio.sleep(1)  # Gửi ping sau mỗi 10 giây

def send_message(chat_id, text):
    api_key = "7337195716:AAHFpNJk6OrbRZU-2vcLfRarAKyXU2mXCaI"
    url = f'https://api.telegram.org/bot{api_key}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        return response
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else", err)


previous_session = None
gold = 0
data_status = {}
previous_gold = None

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
    
        global data, previous_session, previous_gold
        while True:
            try:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                async with websockets.connect(uri, ping_interval=2, ssl=ssl_context, ping_timeout=15) as websocket:
                    payload = json.loads(login)
                    # print(payload)
                    await websocket.send(json.dumps(payload[username][name]))
                    await websocket.send(json.dumps(payload[username][name]))

                    if name == "live":
                        time = data_status[username]["time_live"]
                    else:
                        time = data_status[username]["time_normal"]

                    # print(f"Sent message: {payload}")
                    while True:
                        message = await websocket.recv()
                        # if name == "live":
                        #     print(f"Received message: {message}")
                        
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
                                    current_gold = int(data[1]["As"]["gold"])
                                    if current_gold != previous_gold:
                                        # print("Dữ liệu đã thay đổi:", current_gold)
                                        write_data(str(round(current_gold)))
                                    # else:
                                    #     print("Không có thay đổi trong dữ liệu.")
                                    previous_gold = current_gold
                            await asyncio.sleep(1)
                        except json.JSONDecodeError as e:
                            print(f"Failed to decode JSON: {e}")
            except InvalidStatusCode as e:
                print(f"Server từ chối kết nối WebSocket: {e}. Thử lại...")
                await asyncio.sleep(5)  # Đợi 5 giây trước khi thử lại
            
            except websockets.ConnectionClosed as e:
                # print(f"Connection closed unexpectedly: {e}")
                # Thực hiện lại kết nối tại đây, có thể sử dụng vòng lặp while hoặc asyncio.sleep để tái kết nối
                await asyncio.sleep(1)  # Chờ 5 giây trước khi tái kết nối
                continue
            
    except asyncio.CancelledError:
        print("Main has been cancelled")
    


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
                    # task1 = asyncio.create_task(connect_and_communicate(live, "live", username, option, site))
                    await connect_and_communicate(balance, "balance", username, option, site)
                elif option == "normal":
                    # task1 = asyncio.create_task(connect_and_communicate(normal, "normal", username, option, site))
                    await connect_and_communicate(balance, "balance", username, option, site)

    # #         tasks.append(task1)
    # #         # tasks.append(task2)
    # await asyncio.gather(task1, task2)


with open('login-2.json', 'r') as file:
    login = file.read()

asyncio.run(main(login))