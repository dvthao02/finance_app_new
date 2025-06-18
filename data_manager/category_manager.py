# category_manager.py

import os
import json
import logging
from datetime import datetime
from utils.file_helper import load_json, save_json, generate_id, get_current_datetime, format_datetime_display
from data_manager.user_manager import UserManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CategoryManager:
    def __init__(self, file_path='categories.json'):
        # Get the directory where the package is installed
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, 'data')
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        
        # Initialize categories file if it doesn't exist
        if not os.path.exists(self.file_path):
            logger.info(f"Creating new categories file at {self.file_path}")
            self.save_categories([])
            
        self.categories = self.load_categories()
        self.user_manager = UserManager()
        self.current_user_id = None

        # Ensure default categories exist
        self.ensure_default_categories()

    def ensure_default_categories(self):
        """Kiểm tra và tạo lại categories mặc định nếu cần"""
        try:
            # Tải categories hiện tại
            self.categories = self.load_categories()
            
            # Kiểm tra xem có categories hệ thống không
            system_categories = [cat for cat in self.categories 
                              if cat.get('user_id') == "system"]
            
            if not system_categories:
                logger.warning("No system categories found. Creating defaults...")
                self._create_default_categories()
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error ensuring default categories: {str(e)}")
            return False

    def _create_default_categories(self):
        """Create default income and expense categories"""
        default_categories = [
            # Income categories
            {"name": "Lương", "type": "income", "icon": "💰", "color": "#34a853"},
            {"name": "Thưởng", "type": "income", "icon": "🎁", "color": "#34a853"},
            {"name": "Đầu tư", "type": "income", "icon": "📈", "color": "#34a853"},
            {"name": "Thu nhập phụ", "type": "income", "icon": "💵", "color": "#34a853"},
            
            # Expense categories
            {"name": "Ăn uống", "type": "expense", "icon": "🍽️", "color": "#ea4335"},
            {"name": "Di chuyển", "type": "expense", "icon": "🚗", "color": "#ea4335"},
            {"name": "Mua sắm", "type": "expense", "icon": "🛍️", "color": "#ea4335"},
            {"name": "Hóa đơn & Tiện ích", "type": "expense", "icon": "📄", "color": "#ea4335"},
            {"name": "Giải trí", "type": "expense", "icon": "🎮", "color": "#ea4335"},
            {"name": "Sức khỏe", "type": "expense", "icon": "🏥", "color": "#ea4335"},
            {"name": "Giáo dục", "type": "expense", "icon": "📚", "color": "#ea4335"},
            {"name": "Khác", "type": "expense", "icon": "📝", "color": "#ea4335"}
        ]
        
        created_categories = []
        for cat in default_categories:
            try:
                category = {
                    'category_id': generate_id('cat', self.categories),
                    'name': cat["name"],
                    'type': cat["type"],
                    'icon': cat["icon"],
                    'color': cat["color"],
                    'description': f"Danh mục {cat['type']} mặc định",
                    'is_active': True,
                    'created_at': get_current_datetime(),
                    'updated_at': get_current_datetime(),
                    'user_id': "system"
                }
                created_categories.append(category)
                logger.info(f"Created default category: {cat['name']}")
                
            except Exception as e:
                logger.error(f"Error creating default category {cat['name']}: {str(e)}")
                
        if created_categories:
            self.categories.extend(created_categories)
            self.save_categories()
            logger.info(f"Created {len(created_categories)} default categories")

    def set_current_user(self, user_id):
        """Thiết lập người dùng hiện tại"""
        try:
            if user_id and self.user_manager.get_user_by_id(user_id):
                self.current_user_id = user_id
                logger.debug(f"Set current user to: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting current user: {str(e)}")
            return False

    def load_categories(self):
        """Tải danh sách categories từ file"""
        try:
            categories = load_json(self.file_path)
            logger.debug(f"Loaded {len(categories)} categories from {self.file_path}")
            return categories
        except Exception as e:
            logger.error(f"Error loading categories: {str(e)}")
            return []

    def save_categories(self, categories=None):
        """Lưu danh sách categories vào file"""
        try:
            if categories is None:
                categories = self.categories
            save_json(self.file_path, categories)
            logger.debug(f"Saved {len(categories)} categories to {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving categories: {str(e)}")
            return False    
        
    def get_all_categories(self, user_id=None, category_type=None, active_only=True):
        """Lấy tất cả categories"""
        try:
            # Tải lại categories từ file để đảm bảo dữ liệu mới nhất
            self.categories = self.load_categories()
            
            # Nếu không cung cấp user_id, trả về tất cả categories bao gồm cả hệ thống
            if user_id is None:
                if hasattr(self, 'current_user_id') and self.current_user_id:
                    user_id = self.current_user_id
                else:
                    # Trả về tất cả categories khi không có user_id 
                    # (cần cho hiển thị biểu đồ/thống kê)
                    return self.categories
                
            # Lấy categories hệ thống
            system_categories = [cat for cat in self.categories 
                              if cat.get('user_id') == "system"]
            
            # Lấy categories của user
            user_categories = [cat for cat in self.categories 
                            if cat.get('user_id') == user_id]
            
            # Kết hợp categories
            result = system_categories + user_categories

            # Lọc theo trạng thái active
            if active_only:
                result = [cat for cat in result if cat.get('is_active', True)]

            # Lọc theo loại category
            if category_type:
                result = [cat for cat in result if cat.get('type') == category_type]

            logger.debug(f"Retrieved {len(result)} categories for user {user_id} (including {len(system_categories)} system categories)")
            return result
            
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return []

    def get_category_by_id(self, category_id):
        """Lấy category theo ID"""
        try:
            if not category_id:
                return None
                
            # Tải lại categories từ file để đảm bảo dữ liệu mới nhất
            self.categories = self.load_categories()
            
            for category in self.categories:
                if category['category_id'] == category_id:
                    return category
            return None
            
        except Exception as e:
            logger.error(f"Error getting category {category_id}: {str(e)}")
            return None
            
    def get_category_by_name(self, name, user_id=None, category_type=None):
        """Lấy category theo tên, có thể lọc theo user_id và category_type"""
        try:
            if not name:
                return None
                
            for category in self.categories:
                name_match = category['name'].lower() == name.lower()
                user_match = user_id is None or category.get('user_id') == user_id
                type_match = category_type is None or category.get('type') == category_type
                
                if name_match and user_match and type_match:
                    return category
            return None
            
        except Exception as e:
            logger.error(f"Error getting category by name: {str(e)}")
            return None

    def get_category_stats(self):
        """Lấy thống kê về categories"""
        try:
            stats = {
                'total': len(self.categories),
                'active': len([c for c in self.categories if c.get('is_active', True)]),
                'income': len([c for c in self.categories if c.get('type') == 'income']),
                'expense': len([c for c in self.categories if c.get('type') == 'expense'])
            }
            return stats
            
        except Exception as e:
            logger.error(f"Error getting category stats: {str(e)}")
            return {
                'total': 0,
                'active': 0,
                'income': 0,
                'expense': 0
            }

    def create_category(self, user_id=None, name=None, category_type=None, icon="📝", color="#808080", description="", is_active=True):
        """Tạo category mới. Raises ValueError for bad input, Exception for save errors."""
        if user_id is None:
            user_id = self.current_user_id
        
        if not all([user_id, name, category_type]):
            raise ValueError("Thiếu trường bắt buộc: user_id, name, category_type.")
            
        if category_type not in ['income', 'expense']:
            raise ValueError(f"Loại danh mục không hợp lệ: {category_type}. Phải là 'income' hoặc 'expense'.")
            
        # Reload categories to ensure uniqueness check is against the latest data
        self.categories = self.load_categories()
        existing = self.get_category_by_name(name)
        # Allow if existing is for a different user AND not a system category.
        # Or, more strictly, prevent if name exists for current user_id or system.
        if existing and (existing.get('user_id') == user_id or existing.get('user_id') == "system"):
            raise ValueError(f"Tên danh mục '{name}' đã tồn tại cho người dùng này hoặc là danh mục hệ thống.")

        new_category = {
            'category_id': generate_id('cat', self.categories),
            'name': name,
            'type': category_type,
            'icon': icon,
            'color': color,
            'description': description,
            'is_active': is_active,
            'created_at': get_current_datetime(),
            'updated_at': get_current_datetime(),
            'user_id': user_id
        }

        self.categories.append(new_category)
        if self.save_categories():
            logger.info(f"Created new category: {name} with ID {new_category['category_id']}")
            return new_category # Return the created category dict on success
        else:
            # Attempt to remove the category if save failed to keep self.categories consistent
            self.categories.pop()
            logger.error(f"Failed to save after appending new category: {name}")
            raise Exception("Lưu danh mục mới thất bại.")

    def update_category(self, category_id, current_user_id, is_admin, **kwargs):
        """Cập nhật category. Raises ValueError for bad input or not found, Exception for save errors."""
        if not category_id:
            raise ValueError("Category ID is required for update.")
        if not current_user_id:
            raise ValueError("Current user ID is required for update.")
            
        self.categories = self.load_categories() 
        category_to_update = None
        category_index = -1
        for i, cat in enumerate(self.categories):
            if cat.get('category_id') == category_id:
                category_to_update = cat
                category_index = i
                break
        
        if not category_to_update:
            raise ValueError(f"Danh mục với ID '{category_id}' không tìm thấy.")

        # Ownership/Permission Check
        owner_id = category_to_update.get('user_id')
        if owner_id == "system" and not is_admin:
            raise PermissionError("Bạn không có quyền sửa danh mục hệ thống.")
        if owner_id != "system" and owner_id != current_user_id and not is_admin:
            raise PermissionError("Bạn không có quyền sửa danh mục này.")

        updated = False
        if 'name' in kwargs and kwargs['name'] != category_to_update.get('name'):
            new_name = kwargs['name']
            existing_for_name = self.get_category_by_name(new_name)
            # Check if new name conflicts with another category owned by the same user or a system category
            if (existing_for_name and 
                existing_for_name.get('category_id') != category_id and
                (existing_for_name.get('user_id') == owner_id or existing_for_name.get('user_id') == "system")):
                raise ValueError(f"Tên danh mục '{new_name}' đã tồn tại cho người dùng này hoặc là danh mục hệ thống.")

        allowed_fields = ['name', 'type', 'icon', 'color', 'description', 'is_active']
        for field in allowed_fields:
            if field in kwargs:
                # For system categories, non-admins cannot change 'type'
                if owner_id == "system" and not is_admin and field == 'type' and category_to_update.get(field) != kwargs[field]:
                    raise PermissionError("Bạn không có quyền thay đổi loại của danh mục hệ thống.")
                if category_to_update.get(field) != kwargs[field]:
                    category_to_update[field] = kwargs[field]
                    updated = True

        if updated:
            category_to_update['updated_at'] = get_current_datetime()
            self.categories[category_index] = category_to_update
            if self.save_categories():
                logger.info(f"Updated category: {category_id} by user {current_user_id}")
                return category_to_update
            else:
                logger.error(f"Failed to save after updating category: {category_id}")
                raise Exception(f"Lưu cập nhật cho danh mục '{category_id}' thất bại.")
        else:
            return None

    def delete_category(self, category_id, current_user_id, is_admin):
        """Xóa category. Raises ValueError for bad input or not found/not allowed, Exception for save errors."""
        if not category_id:
            raise ValueError("Category ID is required for deletion.")
        if not current_user_id:
            raise ValueError("Current user ID is required for deletion.")

        self.categories = self.load_categories()
        category_to_delete = None
        category_index = -1

        for i, category in enumerate(self.categories):
            if category.get('category_id') == category_id:
                category_to_delete = category
                category_index = i
                break
        
        if not category_to_delete:
            raise ValueError(f"Danh mục với ID '{category_id}' không tìm thấy.")
        
        # Ownership/Permission Check
        owner_id = category_to_delete.get('user_id')
        if owner_id == "system":
            if not is_admin:
                raise PermissionError("Bạn không có quyền xóa danh mục hệ thống. Bạn có thể đặt nó thành không hoạt động.")
            # Admins can proceed to delete system categories if that's intended (current code allows physical delete)
        elif owner_id != current_user_id and not is_admin: # Not system, not owner, and not admin
            raise PermissionError("Bạn không có quyền xóa danh mục này.")
            
        del self.categories[category_index]
        if self.save_categories():
            logger.info(f"Deleted category: {category_id} by user {current_user_id}")
            return True
        else:
            self.categories.insert(category_index, category_to_delete)
            logger.error(f"Failed to save after deleting category: {category_id}")
            raise Exception(f"Lưu thay đổi sau khi xóa danh mục '{category_id}' thất bại.")

    def get_categories_by_type(self, user_id=None, category_type=None):
        """Lấy categories theo loại (income/expense)"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or category_type is None:
            return []
            
        return [cat for cat in self.get_all_categories(user_id, active_only=True) 
                if cat.get('type') == category_type]

    def restore_category(self, user_id=None, category_id=None):
        """Khôi phục category đã xóa"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or category_id is None:
            return False, "Thiếu thông tin bắt buộc"
            
        category = self.get_category_by_id(user_id, category_id)
        if not category:
            return False, "Không tìm thấy category hoặc không có quyền"

        # Kiểm tra quyền
        if not self.user_manager.is_admin(user_id) and category.get('user_id') != user_id:
            return False, "Không có quyền khôi phục category này"

        category['is_active'] = True

        if self.save_categories():
            return True, "Đã khôi phục category thành công"
        return False, "Lỗi khi lưu file"

    def search_categories(self, user_id=None, keyword=None):
        """Tìm kiếm categories theo từ khóa"""
        if user_id is None:
            user_id = self.current_user_id
            
        if user_id is None or keyword is None:
            return []
            
        keyword = keyword.lower()
        result = []

        for category in self.get_all_categories(user_id):
            if (keyword in category['name'].lower() or 
                keyword in category.get('description', '').lower()):
                result.append(category)

        return result

    def get_category_name(self, category_id=None):
        """Trả về tên category theo ID (hoặc 'Unknown' nếu không tìm thấy)"""
        if category_id is None:
            return "Unknown"
            
        for category in self.categories:
            if category.get('category_id') == category_id:
                return category.get('name', 'Unknown')
        return "Unknown"

    def get_user_categories(self, user_id, is_admin=False):
        """Get all categories for a user or all if admin"""
        if is_admin:
            return self.categories
        return [c for c in self.categories if c['user_id'] == user_id or c['user_id'] is None]

    def format_datetime(self, dt_str):
        """Định dạng datetime cho hiển thị"""
        try:
            return format_datetime_display(dt_str)
        except Exception as e:
            logger.error(f"Error formatting datetime {dt_str}: {e}")
            return dt_str