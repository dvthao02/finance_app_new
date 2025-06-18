import os
import logging
from utils.file_helper import load_json, save_json, generate_id
import datetime

# Cấu hình logging
logger = logging.getLogger(__name__)

class TransactionManager:
    def __init__(self, file_path='transactions.json', budget_manager=None):
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
        self.budget_manager = budget_manager # Thêm tham chiếu đến BudgetManager nếu truyền vào

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
        # Sau khi thêm giao dịch chi tiêu, chỉ gọi apply_expense_to_budget (KHÔNG gọi add_or_update_budget)
        if self.budget_manager and transaction.get('type') == 'expense':            
            user_id = transaction.get('user_id')
            category_id = transaction.get('category_id')
            date_str = transaction.get('date')
            amount = transaction.get('amount', 0)
            logging.debug(f"add_transaction: user_id={user_id}, category_id={category_id}, date={date_str}, amount={amount}")
            if user_id and category_id and date_str:
                try:
                    tx_date = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    year, month = tx_date.year, tx_date.month
                    self.budget_manager.apply_expense_to_budget(user_id, category_id, year, month, amount)
                except Exception as e:
                    logging.error(f"Error in apply_expense_to_budget: {e}")
        return transaction

    def get_transaction_by_id(self, transaction_id):
        """Lấy giao dịch theo ID của nó."""
        transactions = self.get_all_transactions()
        for t in transactions:
            if t.get('transaction_id') == transaction_id:
                return t
        return None

    def update_transaction(self, updated_transaction):
        """Cập nhật một giao dịch hiện có."""
        transactions = self.get_all_transactions()
        for i, t in enumerate(transactions):
            if t.get('transaction_id') == updated_transaction.get('transaction_id'):
                # Preserve created_at if not in updated_transaction or make it explicit
                if 'created_at' not in updated_transaction and 'created_at' in t:
                    updated_transaction['created_at'] = t['created_at']
                updated_transaction['updated_at'] = datetime.datetime.now().isoformat()
                transactions[i] = updated_transaction
                save_json(self.file_path, transactions)
                # Sau khi cập nhật giao dịch chi tiêu, cập nhật ngân sách liên quan
                if self.budget_manager and updated_transaction.get('type') == 'expense':
                    user_id = updated_transaction.get('user_id')
                    category_id = updated_transaction.get('category_id')
                    date_str = updated_transaction.get('date')
                    if user_id and category_id and date_str:
                        try:
                            tx_date = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            year, month = tx_date.year, tx_date.month
                            self.budget_manager.add_or_update_budget({
                                'user_id': user_id,
                                'category_id': category_id,
                                'month': month,
                                'year': year
                            })
                        except Exception as e:
                            logger.error(f"TransactionManager: Error updating budget after update_transaction: {e}")
                return updated_transaction
        # Handle case where transaction to update is not found (optional: raise error or return None)
        logger.warning(f"Transaction with ID {updated_transaction.get('transaction_id')} not found for update.")
        return None 

    def delete_transaction(self, transaction_id):
        """Xóa một giao dịch theo ID của nó."""
        transactions = self.get_all_transactions()
        original_length = len(transactions)
        transactions = [t for t in transactions if t.get('transaction_id') != transaction_id]
        if len(transactions) < original_length:
            save_json(self.file_path, transactions)
            # Sau khi xóa giao dịch chi tiêu, cập nhật ngân sách liên quan
            deleted_tx = [t for t in transactions if t.get('transaction_id') == transaction_id]
            if self.budget_manager and deleted_tx and deleted_tx[0].get('type') == 'expense':
                user_id = deleted_tx[0].get('user_id')
                category_id = deleted_tx[0].get('category_id')
                date_str = deleted_tx[0].get('date')
                if user_id and category_id and date_str:
                    try:
                        tx_date = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        year, month = tx_date.year, tx_date.month
                        self.budget_manager.add_or_update_budget({
                            'user_id': user_id,
                            'category_id': category_id,
                            'month': month,
                            'year': year
                        })
                    except Exception as e:
                        logger.error(f"TransactionManager: Error updating budget after delete_transaction: {e}")
            return True
        logger.warning(f"Transaction with ID {transaction_id} not found for deletion.")
        return False

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
    
    def get_total_expenses(self, user_id, category_id, year, month):
        """
        Tính toán tổng số tiền chi tiêu cho một người dùng, theo danh mục, năm và tháng nhất định.
        
        Args:
            user_id: ID của người dùng
            category_id: ID của danh mục chi tiêu
            year: Năm cần tính toán
            month: Tháng cần tính toán
            
        Returns:
            float: Tổng số tiền chi tiêu
        """
        user_transactions = self.get_transactions_by_user(user_id)
        total_spent = 0
        for t in user_transactions:
            if t.get('type') == 'expense' and \
               t.get('category_id') == category_id:
                try:
                    # Đảm bảo ngày hợp lệ và được phân tích đúng cách
                    date_str = t.get('date', '')
                    if not date_str: # Bỏ qua nếu thiếu ngày
                        continue
                    
                    # Xử lý 'Z' ở cuối chuỗi ngày để chỉ định timezone UTC nếu có
                    if date_str.endswith('Z'):
                        tx_date = datetime.datetime.fromisoformat(date_str[:-1] + '+00:00')
                    else:
                        # Cố gắng phân tích trực tiếp, hoặc thêm timezone nếu nó là naive
                        # Phần này có thể cần điều chỉnh dựa trên định dạng ngày tháng chính xác được lưu trữ
                        try:
                            tx_date = datetime.datetime.fromisoformat(date_str)
                        except ValueError: # Nếu là naive và fromisoformat thất bại
                            # Giả định rằng đây là giờ địa phương nếu không có timezone, hoặc có thể mặc định là UTC
                            # Để đơn giản, hãy giả định rằng nó có thể phân tích được hoặc đã có timezone
                            logger.warning(f"Transaction {t.get('transaction_id')} has date '{date_str}' that might be naive or unparseable without further context.")
                            # Cố gắng một định dạng phổ biến nếu fromisoformat thất bại
                            try:
                                tx_date = datetime.datetime.strptime(date_str.split('T')[0], "%Y-%m-%d")
                            except: # Nếu tất cả đều thất bại, bỏ qua giao dịch này để tính toán tổng
                                logger.error(f"Could not parse date for transaction {t.get('transaction_id')}: {date_str}")
                                continue
                                
                    if tx_date.year == year and tx_date.month == month:
                        total_spent += t.get('amount', 0)
                except ValueError as e:
                    logger.error(f"Invalid date format ('{t.get('date')}') for transaction {t.get('transaction_id')}: {e}")
                    continue
                except Exception as ex: # Bắt bất kỳ lỗi phân tích nào khác
                    logger.error(f"Error processing transaction {t.get('transaction_id')} for date parsing: {ex}")
                    continue
        logger.debug(f"TransactionManager.get_total_expenses for user {user_id}, cat {category_id}, {month}/{year}: {total_spent}")
        return total_spent
