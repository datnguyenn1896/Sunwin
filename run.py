import subprocess
import os
import time
import hashlib

run1 = subprocess.Popen(["python", "1.py"])
run2 = subprocess.Popen(["python", "2.py"])
run3 = subprocess.Popen(["python", "3.py"])
run4 = subprocess.Popen(["python", "4.py"])
message = "\U0001F680 Start..."

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
file_paths = ['login-1.txt', 'login-2.txt', 'login-3.txt', 'login-4.txt']

# Đọc các tệp và lưu hash ban đầu
initial_hashes = read_files(file_paths)

# Chờ 5 phút
time.sleep(300)

# Kiểm tra sự thay đổi
unchanged_files = check_for_changes(initial_hashes, file_paths)
if unchanged_files:
    for name in unchanged_files:
        if name == "login-1":
            run1.kill()
        elif name == "login-2":
            run2.kill()
        elif name == "login-3":
            run3.kill()
        elif name == "login-4":
            run4.kill()
else:
    print("Tất cả các tệp đều có sự thay đổi hoặc không tồn tại.")