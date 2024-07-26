import subprocess
import os
import time
import hashlib
import json
import signal

def get_file_hash(file_path):
    """Tính hash của nội dung tệp để so sánh sự thay đổi."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()

def read_files(file_paths):
    """Đọc nội dung của các tệp và lưu trữ hash của chúng."""
    file_hashes = {}
    for file_path in file_paths:
        if os.path.exists(file_path):
            file_hashes[file_path] = get_file_hash(file_path)
        else:
            print(f"Tệp {file_path} không tồn tại.")
    return file_hashes

def check_for_changes(initial_hashes, file_paths):
    """Kiểm tra xem các tệp có thay đổi không và trả ra các tệp không thay đổi."""
    unchanged_files = []
    for file_path in file_paths:
        if os.path.exists(file_path):
            new_hash = get_file_hash(file_path)
            if new_hash == initial_hashes.get(file_path):
                unchanged_files.append(file_path)
        else:
            print(f"Tệp {file_path} không tồn tại.")
    return unchanged_files

# Đường dẫn tới các tệp txt
file_paths = ['login-1.txt', 'login-2.txt', 'login-3.txt', 'login-4.txt', 'login-5.txt', 'login-6.txt', 'login-7.txt', 'login-8.txt',  'login-9.txt']
dict_balance_run = {}
dict_autotx_run = {}

        
while(True):
    with open('login.json', 'r') as file:
        data = file.read()
        data_json =json.loads(data)
        for username in data_json:
            data = data_json[username]
            path = data_json[username]["path"]
            data_send = json.dumps({username:data})
            if username in data_json and isinstance(data_json[username], dict):
                if data_json[username]["status"] == True:
                    if path not in dict_balance_run:
                        run_balance = subprocess.Popen(["python", "balance.py","--data", str(data_send)])
                        time.sleep(5)
                        run_auto_tx = subprocess.Popen(["python", "autotx.py","--data", str(data_send)])
                        try:
                            dict_balance_run[path] = run_balance.pid
                            dict_autotx_run[path] = run_auto_tx.pid
                            print("Start: " + path)
                        except:
                            print("")


    print("")
    # Đọc các tệp và lưu hash ban đầu
    initial_hashes = read_files(file_paths)
    # Chờ 5 phút
    time.sleep(300)

    # Kiểm tra sự thay đổi
    unchanged_files = check_for_changes(initial_hashes, file_paths)
    if unchanged_files:
        for path_unchanged_files in unchanged_files:
            path = str(path_unchanged_files).replace(".txt","")
            pid_balance = dict_balance_run[path]
            pid_autotx = dict_autotx_run[path]
            os.kill(pid_balance, signal.SIGTERM)
            time.sleep(1)
            os.kill(pid_autotx, signal.SIGTERM)
            time.sleep(1)
            if path in dict_balance_run:
                del dict_balance_run[path]
                del dict_autotx_run[path]
            print("Stop: " + path)
    else:
        print("Tất cả các tệp đều có sự thay đổi hoặc không tồn tại.")