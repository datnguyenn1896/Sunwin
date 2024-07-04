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
    sub_len = len(substring)
    if len(sequence) - sub_len == 1:
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
        old_data = data

def write_data(data):
    with open('login-4.txt', 'a', encoding='utf-8') as file:
        file.write(data)

dict_result = {}

def add_to_dict(key, value):
    dict_result[key] = value
    if len(dict_result) > 10:
        keys = list(dict_result.keys())
        del dict_result[keys[0]]

def get_top_n_items(n):
    sorted_items = sorted(dict_result.items(), key=lambda item: item[0], reverse=True)
    top_n_items = sorted_items[:n]
    top_n_items_reversed = top_n_items[::-1]
    return top_n_items_reversed

async def send_ping(websocket):
    while True:
        try:
            await websocket.ping()
        except websockets.ConnectionClosed:
            break
        await asyncio.sleep(1)

def send_test_message(chat_id, message):
    bot = Bot(token="YOUR_TELEGRAM_BOT_TOKEN")
    try:
        bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
    except Exception as ex:
        print(ex)

def send_message(chat_id, text):
    api_key = "YOUR_TELEGRAM_BOT_TOKEN"
    url = f'https://api.telegram.org/bot{api_key}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as err:
        print("Error:", err)

previous_session = None
gold = 0
data_status = {}

logging.basicConfig(level=logging.CRITICAL)

async def connect_and_communicate(uri, name, username, option, site):
    try:
        data_status[username] = {"status": "wait_end_session", "prev_session": None, "prev_bet": 0, "prev_session_rs": True, "session_bet": None, "current_session": None, "current_betTypeResult": None, "current_bet": 0, "next_session": None, "next_betTypeResult": None, "next_bet": 0, "gold": 0, "total": 0, "total_win": 0, "total_lose": 0, "lose_strick": 0, "time_live": 35, "time_normal": 50}
    
        global data, previous_session
        while True:
            try:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                async with websockets.connect(uri, ping_interval=1, ssl=ssl_context, ping_timeout=15) as websocket:
                    payload = json.loads(login)
                    await websocket.send(json.dumps(payload[username][name]))
                    await websocket.send(json.dumps(payload[username][name]))

                    if name == "live":
                        time = data_status[username]["time_live"]
                    else:
                        time = data_status[username]["time_normal"]

                    asyncio.create_task(send_ping(websocket))
                    while True:
                        message = await websocket.recv()
                        
                        try: 
                            data = json.loads(message)
                            if site == "sunwin":
                                chat_id = "-4248092135"
                            elif site == "hitclub":
                                chat_id = "-4232039520"
                            if name == "balance":
                                if site == "sunwin":
                                    data_get_balance = json.dumps([6, "Simms", "channelPlugin", {"cmd": 310}])
                                elif site == "hitclub":
                                    data_get_balance = json.dumps([6, "Simms", "channelPlugin", {"cmd": 310}])
                                await websocket.send(data_get_balance)
                                if data[0] == 5 and data[1]["cmd"] == 310:
                                    data_status[username]["gold"] = int(data[1]["As"]["gold"])

                            if (name == "live" or name == "normal") and data[0] == 1 and data[1] == True:
                                if site == "sunwin":
                                    if name == "live":
                                        payload_connect_tx = json.dumps([6, "Livestream", "TaiXiuLivestreamPlugin", {"cmd": 1950, "sC": True}])
                                    elif name == "normal":
                                        payload_connect_tx = json.dumps([6, "MiniGame", "taixiuPlugin", {"cmd": 1005}])
                                elif site == "hitclub":
                                    if name == "live":
                                        payload_connect_tx = json.dumps([6, "MiniGame", "taiXiuLiveTipPlugin", {"cmd": 7511}])
                                    elif name == "normal":
                                        payload_connect_tx = json.dumps([6, "MiniGame", "taixiuPlugin", {"cmd": 1005}])
                                        
                                await websocket.send(payload_connect_tx)
                                asyncio.create_task(send_ping(websocket))

                            if data[0] == 5 and (data[1]["cmd"] == 1957 or data[1]["cmd"] == 1008):
                                if data[1]["cmd"] == 1957:
                                    betB = f'{data[1]["bs"][3]["v"]:,}'
                                    userB = f'{data[1]["bs"][3]["uC"]:,}'
                                    betS = f'{data[1]["bs"][6]["v"]:,}'
                                    userS = f'{data[1]["bs"][6]["uC"]:,}'
                                    seasion = data[1]["sid"]
                                elif data[1]["cmd"] == 1008:
                                    seasion = data[1]["sid"]
                                    betB = f'{data[1]["gi"][0]["B"]["tB"]:,}'
                                    userB = f'{data[1]["gi"][0]["B"]["tU"]:,}'
                                    betS = f'{data[1]["gi"][0]["S"]["tB"]:,}'
                                    userS = f'{data[1]["gi"][0]["S"]["tU"]:,}'

                                data_status[username]["current_session"] = seasion
                                data_status[username]["next_session"] = seasion + 1
                                if seasion:
                                    if previous_session is None or seasion > data_status[username]["current_session"]:
                                        previous_session = seasion
                                        data_status[username]["prev_session"] = previous_session
                                        for sid in range(seasion - 10, seasion):
                                            if site == "sunwin":
                                                if name == "live":
                                                    data_get_history = json.dumps([6, "Livestream", "TaiXiuLivestreamPlugin", {"cmd": 1965, "sid": sid}])
                                                elif name == "normal":
                                                    data_get_history = json.dumps([6, "MiniGame", "taixiuPlugin", {"cmd": 1007, "sid": sid, "aid": 1}])
                                            elif site == "hitclub":
                                                if name == "normal":
                                                    data_get_history = json.dumps([6, "MiniGame", "taixiuPlugin", {"cmd": 1007, "sid": sid, "aid": 1}])
                                                    
                                            await websocket.send(data_get_history)

                                    elif seasion != previous_session:
                                        if data_status[username]["status"] != "wait_result_bet":
                                            data_status[username]["status"] = "next_session"
                                        previous_session = seasion
                                        data_status[username]["prev_session"] = previous_session
                                        if data_status[username]["status"] == "wait_end_session":
                                            data_status[username]["prev_bet"] = 0
                                            data_status[username]["prev_session_rs"] = False

                            if data[0] == 5 and (data[1]["cmd"] == 1958 or data[1]["cmd"] == 1009):
                                if data[1]["cmd"] == 1958:
                                    seasion = data[1]["sid"]
                                    betTypeResult = data[1]["br"]
                                elif data[1]["cmd"] == 1009:
                                    seasion = data[1]["sid"]
                                    betTypeResult = data[1]["rs"]["betTypeResult"]

                                data_status[username]["prev_session"] = seasion
                                data_status[username]["session_bet"] = seasion + 1
                                data_status[username]["prev_session_rs"] = True
                                data_status[username]["current_betTypeResult"] = betTypeResult
                                if betTypeResult == 1:
                                    betTypeResult = "Xỉu"
                                elif betTypeResult == 2:
                                    betTypeResult = "Tài"
                                if data_status[username]["prev_bet"] == data_status[username]["current_betTypeResult"]:
                                    data_status[username]["total_win"] += data_status[username]["current_bet"]
                                    data_status[username]["lose_strick"] = 0
                                else:
                                    data_status[username]["total_lose"] += data_status[username]["current_bet"]
                                    data_status[username]["lose_strick"] += 1
                                    
                            if data[0] == 5 and (data[1]["cmd"] == 1965 or data[1]["cmd"] == 1007):
                                if data[1]["cmd"] == 1965:
                                    betTypeResult = data[1]["br"]
                                    seasion = data[1]["sid"]
                                elif data[1]["cmd"] == 1007:
                                    seasion = data[1]["sid"]
                                    betTypeResult = data[1]["rs"]["betTypeResult"]
                                if betTypeResult == 1:
                                    betTypeResult = "Xỉu"
                                elif betTypeResult == 2:
                                    betTypeResult = "Tài"
                                add_to_dict(seasion, betTypeResult)
                                top_10_dict = get_top_n_items(10)
                                with open("log_taixiu.json", "a", encoding="utf-8") as file:
                                    json.dump(top_10_dict, file, ensure_ascii=False)
                                    file.write("\n")

                            if data[0] == 5 and data[1]["cmd"] == 310:
                                append_if_data_changes(message)

                            if (data_status[username]["status"] == "next_session" or data_status[username]["status"] == "next_bet") and data_status[username]["next_session"] and data_status[username]["prev_session_rs"]:
                                if data_status[username]["status"] == "next_session":
                                    data_status[username]["status"] = "next_bet"
                                    if data_status[username]["lose_strick"] <= 4:
                                        data_status[username]["next_bet"] = 2
                                    else:
                                        data_status[username]["next_bet"] = 4

                                if data_status[username]["status"] == "next_bet":
                                    data_status[username]["current_bet"] = data_status[username]["next_bet"]
                                    data_status[username]["current_session"] = data_status[username]["next_session"]
                                    data_status[username]["current_betTypeResult"] = data_status[username]["next_betTypeResult"]

                                    data_status[username]["gold"] -= data_status[username]["current_bet"]
                                    data_status[username]["total"] += data_status[username]["current_bet"]

                                    msg = f'[{site}][{username}] [{name}]\nPhiên: {data_status[username]["current_session"]}\nCược: {data_status[username]["current_bet"]}\nVàng: {data_status[username]["gold"]}\nTổng: {data_status[username]["total"]}\nThắng: {data_status[username]["total_win"]}\nThua: {data_status[username]["total_lose"]}\nSố lần thua liên tiếp: {data_status[username]["lose_strick"]}'
                                    send_test_message(chat_id, msg)

                        except (json.JSONDecodeError, KeyError):
                            pass

                        await asyncio.sleep(1)
            except websockets.ConnectionClosed:
                pass

    except Exception as e:
        print(f"Error: {e}")

async def main():
    uri = "wss://example.com/ws"
    name = "live"
    username = "user1"
    option = None
    site = "sunwin"
    await connect_and_communicate(uri, name, username, option, site)

asyncio.run(main())
