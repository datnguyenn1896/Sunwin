from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import uuid
import psutil
import hashlib
from datetime import datetime

def get_hardware_info():
    # Lấy địa chỉ MAC
    mac = uuid.getnode()
    mac_addr = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

    # Lấy thông tin CPU
    cpu_info = str(psutil.cpu_freq()) + str(psutil.cpu_count())

    # Lấy thông tin ổ cứng
    disk_info = ""
    for disk in psutil.disk_partitions():
        disk_info += disk.device

    # Kết hợp tất cả thông tin
    combined_info = mac_addr + cpu_info + disk_info
    return combined_info

def generate_unique_id(hardware_info):
    # Tạo hash SHA-256 từ thông tin phần cứng
    unique_id = hashlib.sha256(hardware_info.encode()).hexdigest()
    return unique_id


# Đường dẫn tới file JSON chứa thông tin xác thực
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Phạm vi truy cập
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Tạo credentials
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# ID của bảng tính Google Sheets và tên của sheet
SPREADSHEET_ID = '18dI4ReHFdhHmoiYN0zlVJtMWOXJvpnwnR6cqEf08w2A'
RANGE_NAME = 'device!A1:D10'  # Chỉnh sửa range tùy thuộc vào vị trí dữ liệu của bạn
SHEET_NAME = 'device'
# Tạo dịch vụ Google Sheets API
service = build('sheets', 'v4', credentials=creds)

# Gọi API để đọc dữ liệu từ bảng tính
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
values = result.get('values', [])

hardware_info = get_hardware_info()
unique_id = generate_unique_id(hardware_info)

# Lấy thời gian hiện tại
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Kiểm tra và hiển thị dữ liệu
if not values:
    print('Không có dữ liệu được tìm thấy.')
else:
    for row in values:
        device = row[1]
        activate = row[2]
        if unique_id == device and activate == "ON":
            print("oke")
        elif unique_id == device and activate == "OFF":
            # Tìm dòng trống đầu tiên
            row_number = len(values) + 1  # Dòng trống đầu tiên là dòng sau dòng cuối cùng có dữ liệu
            data_to_insert = [current_time, unique_id, "OFF"]
            # Tạo range cho dòng trống đầu tiên
            range_to_update = f'{device}!A{row_number}'

            # Cấu trúc dữ liệu để điền
            body = {
                'values': [data_to_insert]}
            # Điền dữ liệu vào dòng trống đầu tiên
            # Thêm dòng mới vào sheet2
            # Lấy sheet2 từ file
            # Thêm dữ liệu vào cuối bảng
            result = service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=SHEET_NAME,
                valueInputOption='RAW',
                body=body
            ).execute()
            print("Thiết bị này chưa được kích hoạt, vui lòng liên hệ Nguyễn Đạt.")
            break