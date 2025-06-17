# file_helper.py

import json
import os
import re
import logging
from datetime import datetime

# Cấu hình logging
logger = logging.getLogger(__name__)

def load_json(file_path):
    """Đọc dữ liệu từ file JSON
    
    Args:
        file_path (str): Đường dẫn đến file JSON cần đọc
        
    Returns:
        list/dict: Dữ liệu đọc được từ file JSON, trả về list rỗng nếu có lỗi
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        logger.warning(f"File không tồn tại: {file_path}")
        return []
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Lỗi khi đọc file {file_path}: {e}")
        return []

def save_json(file_path, data):
    """Lưu dữ liệu vào file JSON
    
    Args:
        file_path (str): Đường dẫn đến file JSON cần lưu
        data (list/dict): Dữ liệu cần lưu
        
    Returns:
        bool: True nếu lưu thành công, False nếu có lỗi
    """
    try:
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        logger.debug(f"Đã lưu dữ liệu vào file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi lưu file {file_path}: {e}")
        return False

def generate_id(prefix=None, data_list=None, id_field=None):
    """Tạo ID tự động dựa trên prefix, danh sách hiện có và trường id tùy chọn
    
    Args:
        prefix (str, optional): Tiền tố cho ID (mặc định: "id")
        data_list (list, optional): Danh sách dữ liệu để tìm ID lớn nhất
        id_field (str, optional): Tên trường chứa ID trong dữ liệu
        
    Returns:
        str: ID mới được tạo theo định dạng prefix_XXX
    """
    if data_list is None:
        data_list = []
    if not prefix:
        prefix = "id"
    if not data_list:
        return f"{prefix}_001"
    
    max_num = 0
    for item in data_list:
        id_val = None
        if id_field and id_field in item and item[id_field] is not None and str(item[id_field]).startswith(prefix):
            id_val = item[id_field]
        else:
            # Ưu tiên *_id, nếu không có thì kiểm tra 'id' hoặc 'notification_id'
            id_key = next((key for key in item.keys() if key.endswith('_id')), None)
            if id_key and item.get(id_key) is not None and str(item[id_key]).startswith(prefix):
                id_val = item[id_key]
            elif 'id' in item and item.get('id') is not None and str(item['id']).startswith(prefix):
                id_val = item['id']
            elif 'notification_id' in item and item.get('notification_id') is not None and str(item['notification_id']).startswith(prefix):
                id_val = item['notification_id']
        if id_val:
            try:
                num = int(str(id_val).split('_')[-1])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                continue
    new_id = f"{prefix}_{max_num + 1:03d}"
    logger.debug(f"Đã tạo ID mới: {new_id}")
    return new_id

def get_current_datetime():
    """Lấy thời gian hiện tại theo format ISO
    
    Returns:
        str: Thời gian hiện tại theo định dạng ISO
    """
    return datetime.now().isoformat()

def format_datetime_display(datetime_str, show_time=True):
    """Chuyển đổi chuỗi datetime sang định dạng dd-mm-yyyy hh:mm:ss hoặc dd-mm-yyyy
    
    Args:
        datetime_str (str): Chuỗi datetime theo định dạng ISO hoặc YYYY-MM-DD
        show_time (bool): Hiển thị giờ phút giây hay không
    
    Returns:
        str: Chuỗi datetime đã định dạng
    """
    try:
        if not datetime_str:
            return ""
        
        dt = None
        # Xử lý chuỗi ISO với T
        if 'T' in datetime_str:
            # Xử lý trường hợp có phần thập phân giây
            clean_dt = datetime_str.split('.')[0] if '.' in datetime_str else datetime_str
            dt = datetime.fromisoformat(clean_dt)
        # Xử lý chuỗi ngày đơn giản YYYY-MM-DD
        else:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d")
            
        # Định dạng kết quả
        if show_time:
            formatted = dt.strftime("%d-%m-%Y %H:%M:%S")
        else:
            formatted = dt.strftime("%d-%m-%Y")
        logger.debug(f"Định dạng datetime: {datetime_str} -> {formatted}")
        return formatted
    except Exception as e:
        logger.error(f"Lỗi định dạng datetime: {datetime_str}, Error: {e}")
        return datetime_str

def get_formatted_current_datetime(show_time=True):
    """Lấy thời gian hiện tại với định dạng hiển thị
    
    Args:
        show_time (bool): Hiển thị giờ phút giây hay không
    
    Returns:
        str: Chuỗi datetime đã định dạng dd-mm-yyyy hh:mm:ss hoặc dd-mm-yyyy
    """
    now = datetime.now()
    if show_time:
        return now.strftime("%d-%m-%Y %H:%M:%S")
    else:
        return now.strftime("%d-%m-%Y")

def validate_date_format(date_string):
    """Kiểm tra format ngày tháng YYYY-MM-DD
    
    Args:
        date_string (str): Chuỗi ngày tháng cần kiểm tra
        
    Returns:
        bool: True nếu đúng định dạng, False nếu sai
    """
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        logger.warning(f"Định dạng ngày không hợp lệ: {date_string}")
        return False

def validate_datetime_format(datetime_string):
    """Kiểm tra format datetime ISO
    
    Args:
        datetime_string (str): Chuỗi datetime cần kiểm tra
        
    Returns:
        bool: True nếu đúng định dạng, False nếu sai
    """
    try:
        datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
        return True
    except ValueError:
        logger.warning(f"Định dạng datetime không hợp lệ: {datetime_string}")
        return False

def is_valid_email(email):
    """Kiểm tra định dạng email
    
    Args:
        email (str): Email cần kiểm tra
        
    Returns:
        bool: True nếu email hợp lệ hoặc rỗng, False nếu không hợp lệ
    """
    if not email:  # Cho phép email rỗng
        return True
    # Regex cơ bản cho email
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = re.match(regex, email) is not None
    if not is_valid:
        logger.warning(f"Email không hợp lệ: {email}")
    return is_valid

def is_valid_phone(phone):
    """Kiểm tra định dạng số điện thoại (10-11 chữ số)
    
    Args:
        phone (str): Số điện thoại cần kiểm tra
        
    Returns:
        bool: True nếu số điện thoại hợp lệ hoặc rỗng, False nếu không hợp lệ
    """
    if not phone:  # Cho phép số điện thoại rỗng
        return True
    # Regex cho số điện thoại 10-11 chữ số
    regex = r'^\d{10,11}$'
    is_valid = re.match(regex, phone) is not None
    if not is_valid:
        logger.warning(f"Số điện thoại không hợp lệ: {phone}")
    return is_valid

def is_strong_password(password):
    """Kiểm tra độ mạnh mật khẩu
    
    Yêu cầu:
    - Ít nhất 8 ký tự
    - Ít nhất 1 chữ hoa
    - Ít nhất 1 chữ thường
    - Ít nhất 1 số
    - Ít nhất 1 ký tự đặc biệt
    
    Args:
        password (str): Mật khẩu cần kiểm tra
        
    Returns:
        bool: True nếu mật khẩu đủ mạnh, False nếu không
    """
    if not password:
        logger.warning("Mật khẩu không được để trống")
        return False
        
    is_valid = (
        len(password) >= 8 and
        re.search(r'[a-z]', password) and
        re.search(r'[A-Z]', password) and
        re.search(r'\d', password) and
        re.search(r'[^\w\s]', password)
    )
    
    if not is_valid:
        logger.warning("Mật khẩu không đủ mạnh")
    return is_valid

def copy_avatar_to_assets(source_path, user_id):
    """Sao chép ảnh đại diện vào thư mục assets
    
    Args:
        source_path (str): Đường dẫn đến file ảnh gốc
        user_id (str): ID của người dùng để đặt tên file đích
        
    Returns:
        str: Đường dẫn mới đến file ảnh trong thư mục assets hoặc None nếu thất bại
    """
    import shutil
    try:
        if not source_path or not os.path.exists(source_path):
            logger.warning(f"Không tìm thấy file nguồn: {source_path}")
            return None
            
        # Lấy extension của file gốc
        _, extension = os.path.splitext(source_path)
        if not extension:
            extension = '.png'  # Mặc định nếu không có extension
            
        # Tạo tên file đích: avatar_user_001.jpg
        filename = f"avatar_{user_id}{extension}"
        
        # Đường dẫn đến thư mục assets
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        
        # Đường dẫn đầy đủ đến file đích
        dest_path = os.path.join(assets_dir, filename)
        
        # Sao chép file
        logger.debug(f"Đang sao chép từ {source_path} -> {dest_path}")
        shutil.copy2(source_path, dest_path)
        logger.info(f"Đã sao chép ảnh thành công: {dest_path}")
        
        return dest_path
    except Exception as e:
        logger.error(f"Lỗi khi sao chép avatar: {e}")
        return None