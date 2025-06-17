import os
import logging
from utils.file_helper import load_json, save_json, generate_id
import datetime

# Cấu hình logging
logger = logging.getLogger(__name__)

class TransactionManager:
    def __init__(self, file_path='transactions.json'):
        """Khởi tạo quản lý giao dịch
        
        Args:
            file_path: Đường dẫn đến file lưu trữ giao dịch
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        if not os.path.exists(self.file_path):
            save_json(self.file_path, [])

    def get_all_transactions(self):
        """Lấy tất cả giao dịch
        
        Returns:
            list: Danh sách tất cả giao dịch
        """
        return load_json(self.file_path)

    def get_transactions_by_user(self, user_id):
        """Lấy giao dịch theo ID người dùng
        
        Args:
            user_id: ID của người dùng
            
        Returns:
            list: Danh sách giao dịch của người dùng
        """
        return [t for t in self.get_all_transactions() if t.get('user_id') == user_id]

    def add_transaction(self, transaction):
        """Thêm giao dịch mới
        
        Args:
            transaction: Thông tin giao dịch cần thêm
            
        Returns:
            dict: Thông tin giao dịch đã được thêm
        """
        transactions = self.get_all_transactions()
        # Chuẩn hóa ID cho đồng bộ
        if 'transaction_id' not in transaction:
            # Tìm ID lớn nhất hiện tại
            max_id = 0
            for t in transactions:
                tid = t.get('transaction_id', '')
                if tid and tid.startswith('txn_'):
                    try:
                        id_num = int(tid[4:])
                        max_id = max(max_id, id_num)
                    except ValueError:
                        continue
            # Tạo ID mới
            transaction['transaction_id'] = f"txn_{max_id+1:03d}"
        
        # Chuẩn hóa định dạng ngày
        for date_field in ['date', 'created_at', 'updated_at']:
            if date_field in transaction:
                try:
                    transaction[date_field] = datetime.datetime.fromisoformat(transaction[date_field].replace('Z', '+00:00')).isoformat()
                except Exception as e:
                    logger.error(f"Không thể chuẩn hóa ngày cho trường {date_field}: {e}")
        
        transactions.append(transaction)
        save_json(self.file_path, transactions)
        return transaction

    def get_transactions_by_month(self, year, month):
        """Lấy giao dịch theo tháng
        
        Args:
            year: Năm cần lấy
            month: Tháng cần lấy
            
        Returns:
            list: Danh sách giao dịch trong tháng
        """
        transactions = self.get_all_transactions()
        
        # Nếu cả năm và tháng đều là 0, trả về tất cả giao dịch (bộ lọc = "Tất cả")
        if year == 0 or month == 0:
            return transactions
        
        month_transactions = []
        
        for t in transactions:
            try:
                # Phân tích ngày từ định dạng ISO
                tx_date = datetime.datetime.fromisoformat(t.get('date', '').replace('Z', '+00:00'))
                if tx_date.year == year and tx_date.month == month:
                    month_transactions.append(t)
            except Exception as e:
                logger.warning(f"Không thể xử lý ngày giao dịch: {e}")
                continue
                
        return month_transactions
        
    def get_recent_transactions(self, limit=10, user_id=None):
        """Lấy các giao dịch gần đây
        
        Args:
            limit: Số lượng giao dịch tối đa cần lấy
            user_id: ID người dùng để lọc (tùy chọn)
            
        Returns:
            list: Danh sách giao dịch gần đây
        """
        transactions = self.get_all_transactions()
        
        # Lọc theo user_id nếu được cung cấp
        if user_id:
            transactions = [t for t in transactions if t.get('user_id') == user_id]
        
        # Sắp xếp theo ngày (mới nhất lên đầu)
        try:
            sorted_transactions = sorted(transactions, 
                key=lambda t: datetime.datetime.fromisoformat(t.get('date', '').replace('Z', '+00:00')), 
                reverse=True)
        except Exception as e:
            logger.warning(f"Không thể sắp xếp giao dịch: {e}")
            sorted_transactions = transactions
            
        return sorted_transactions[:limit]
    
    def get_transactions_in_range(self, start_date, end_date, user_id=None):
        """Lấy giao dịch trong khoảng thời gian
        
        Args:
            start_date: Ngày bắt đầu (có thể là datetime.date hoặc datetime.datetime)
            end_date: Ngày kết thúc (có thể là datetime.date hoặc datetime.datetime)
            user_id: ID người dùng để lọc (tùy chọn)
            
        Returns:
            list: Danh sách giao dịch trong khoảng thời gian
        """
        transactions = self.get_all_transactions()
        
        logger.debug(f"Lấy giao dịch trong khoảng: start_date={start_date} (type: {type(start_date)}), end_date={end_date} (type: {type(end_date)}), user_id={user_id}")
        
        # Xử lý trường hợp start_date hoặc end_date là None
        if start_date is None or end_date is None:
            if user_id:
                result = [t for t in transactions if t.get('user_id') == user_id]
                logger.debug(f"-> {len(result)} giao dịch (tất cả thời gian, đã lọc theo người dùng)")
                return result
            logger.debug(f"-> {len(transactions)} giao dịch (tất cả thời gian)")
            return transactions

        # Chuyển đổi start_date và end_date sang datetime.datetime nếu chúng là datetime.date
        if isinstance(start_date, datetime.date) and not isinstance(start_date, datetime.datetime):
            start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        else:
            start_datetime = start_date

        if isinstance(end_date, datetime.date) and not isinstance(end_date, datetime.datetime):
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
        else:
            end_datetime = end_date
            
        logger.debug(f"Đã chuyển đổi: start_datetime={start_datetime}, end_datetime={end_datetime}")

        # Lọc theo user_id nếu được cung cấp
        if user_id:
            transactions = [t for t in transactions if t.get('user_id') == user_id]

        filtered_transactions = []
        for transaction in transactions:
            try:
                tx_date_str = transaction.get('date', '')
                if not tx_date_str:
                    continue
                
                # Đảm bảo tx_date là timezone-aware (UTC) nếu nó từ ISO format có Z, hoặc naive nếu không có.
                # Giả định rằng start_datetime và end_datetime là naive hoặc đã được xử lý timezone phù hợp.
                # Để đơn giản, nếu tx_date_str có 'Z', chuyển nó thành UTC, nếu không thì coi là naive.
                if 'Z' in tx_date_str:
                    tx_date = datetime.datetime.fromisoformat(tx_date_str.replace('Z', '+00:00'))
                    # Nếu start_datetime/end_datetime là naive, cần làm cho tx_date naive (ở UTC) để so sánh
                    # Hoặc làm cho start_datetime/end_datetime aware.
                    # Hiện tại, giả định start_datetime/end_datetime là naive (local time).
                    # Nếu tx_date là UTC, chuyển nó về local time để so sánh (nếu cần) hoặc ngược lại.
                    # Để đơn giản nhất, nếu dữ liệu ngày tháng không nhất quán về timezone,
                    # có thể cần một chiến lược chuẩn hóa timezone toàn diện hơn.
                    # Tạm thời, nếu start_datetime/end_datetime là naive, và tx_date là aware,
                    # chúng ta sẽ làm tx_date naive bằng cách loại bỏ thông tin tz.
                    if start_datetime.tzinfo is None and tx_date.tzinfo is not None:
                        tx_date = tx_date.replace(tzinfo=None) # So sánh naive với naive
                else:
                    tx_date = datetime.datetime.fromisoformat(tx_date_str) # Đã là naive

                # Kiểm tra nếu trong khoảng: start_datetime <= tx_date <= end_datetime
                if start_datetime <= tx_date <= end_datetime:
                    filtered_transactions.append(transaction)
                # else: # Bỏ log này để tránh quá nhiều output
                    # logger.debug(f"Giao dịch {transaction.get('transaction_id')} bị bỏ qua: tx_date={tx_date} không nằm trong [{start_datetime}, {end_datetime}]")

            except Exception as e:
                logger.warning(f"Không thể xử lý ngày giao dịch cho {transaction.get('transaction_id', 'N/A')}: {e}, chuỗi ngày: {tx_date_str}")
                continue

        logger.debug(f"-> {len(filtered_transactions)} giao dịch trong khoảng {start_datetime} - {end_datetime} cho user_id={user_id}")
        return filtered_transactions
