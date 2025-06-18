# user_manager.py

import bcrypt
# import re # No longer needed directly here
import os
import json
import logging
import sys
import random
import string
from datetime import datetime

# Add the parent directory to sys.path to make imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_helper import (
    load_json, save_json, generate_id,
    is_valid_email, is_valid_phone, is_strong_password # Import new validation functions
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, user_file='users.json'):
       # print('[DEBUG] UserManager __init__ start')
        # Get the directory where the package is installed
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, 'data')
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        self.user_file = os.path.join(data_dir, user_file)
        #print(f'[DEBUG] user_file path: {self.user_file}')
        # Initialize users file if it doesn't exist
        if not os.path.exists(self.user_file):
            #print(f'[DEBUG] Creating new users file at {self.user_file}')
            self.save_users([])
            
        # Create default admin if no users exist
        users = self.load_users()
        #print(f'[DEBUG] Loaded users: {users}')
        if not users:
            #print('[DEBUG] Creating default admin user')
            self.add_user(
                username="admin",
                password="Admin@123",
                full_name="Administrator",
                role="admin" # Changed from is_admin=True
            )
        #print('[DEBUG] UserManager __init__ end')

    def set_current_user(self, user_id):
        """Thiết lập người dùng hiện tại cho manager.
        Args:
            user_id (str): ID của người dùng
        """
        # This manager typically loads all users, but setting current_user_id 
        # can be useful for context-specific operations or logging.
        self.current_user_id = user_id
        logger.debug(f"UserManager current user set to: {user_id}")

    def load_users(self):
        try:
            users = load_json(self.user_file)
            logger.debug(f"Loaded {len(users)} users from {self.user_file}")
            return users
        except Exception as e:
            logger.error(f"Error loading users: {str(e)}")
            return []

    def save_users(self, users):
        try:
            save_json(self.user_file, users)
            logger.debug(f"Saved {len(users)} users to {self.user_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving users: {str(e)}")
            return False

    def hash_password(self, password):
        try:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise ValueError("Error processing password")

    def check_password(self, password, hashed):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error checking password: {str(e)}")
            return False

    def is_email_unique(self, email, user_id_to_exclude=None):
        if not email: # Empty email is considered unique in terms of not clashing
            return True
        users = self.load_users()
        for user in users:
            if user.get('user_id') == user_id_to_exclude:
                continue
            if user.get('email') == email:
                return False
        return True

    def is_phone_unique(self, phone, user_id_to_exclude=None):
        if not phone: # Empty phone is considered unique
            return True
        users = self.load_users()
        for user in users:
            if user.get('user_id') == user_id_to_exclude:
                continue
            if user.get('phone') == phone:
                return False
        return True

    def is_username_unique(self, username, user_id_to_exclude=None):
        if not username:
            return True
        users = self.load_users()
        for user in users:
            if user.get('user_id') == user_id_to_exclude:
                continue
            if user.get('username', '').lower() == username.lower():
                return False
        return True

    def is_admin(self, user_id):
        """Kiểm tra xem user_id có phải là admin không"""
        try:
            user = self.get_user_by_id(user_id)
            # Check if user exists and their role is 'admin'
            return user and user.get('role') == 'admin'
        except Exception as e:
            logger.error(f"Error checking admin status: {str(e)}")
            return False

    def find_user_by_username(self, username):
        if not username:
            return None
            
        try:
            users = self.load_users()
            logger.debug(f"Searching for user '{username}' in {len(users)} users")
            
            for user in users:
                if user['username'].lower() == username.lower():
                    logger.debug(f"Found user: {user['username']}")
                    return user
                    
            logger.debug(f"User '{username}' not found")
            return None
            
        except Exception as e:
            logger.error(f"Error finding user: {str(e)}")
            return None

    def find_user_by_email(self, email):
        if not email:
            return None
        try:
            users = self.load_users()
            for user in users:
                if user.get('email', '').lower() == email.lower():
                    return user
            return None
        except Exception as e:
            logger.error(f"Error finding user by email: {str(e)}")
            return None

    def find_user_by_email_or_username(self, identifier):
        if not identifier:
            return None
        try:
            users = self.load_users()
            for user in users:
                if user.get('email', '').lower() == identifier.lower() or user.get('username', '').lower() == identifier.lower():
                    return user
            return None
        except Exception as e:
            logger.error(f"Error finding user by email/username: {str(e)}")
            return None

    def authenticate_user(self, identifier, password):
        try:
            if not identifier or not password:
                logger.warning("Empty email/username or password")
                return {"status": "error", "message": "Vui lòng nhập email/tên đăng nhập và mật khẩu."}
                
            user = self.find_user_by_email_or_username(identifier)
            
            if not user:
                logger.warning(f"Failed login attempt for non-existent identifier: {identifier}")
                return {"status": "error", "message": "Sai email/tên đăng nhập hoặc mật khẩu."}
                
            if not user.get('is_active', True):
                logger.warning(f"Login attempt for locked user: {identifier}")
                return {"status": "error", "message": "Tài khoản đã bị khóa."}
                
            if not self.check_password(password, user['password']):
                logger.warning(f"Failed login attempt for user: {identifier}")
                return {"status": "error", "message": "Sai email/tên đăng nhập hoặc mật khẩu."}
                
            # Update last login time
            users = self.load_users()
            for u in users:
                if u.get('user_id') == user.get('user_id'):
                    u['last_login'] = datetime.now().isoformat()
                    break
            self.save_users(users)
            
            logger.info(f"Successful login for user: {identifier}")
            return {"status": "success", "user": user}

        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return {"status": "error", "message": "Lỗi xác thực. Vui lòng thử lại sau."}

    def generate_reset_code(self, identifier):
        """Sinh mã reset mật khẩu cho user (demo: in ra terminal, thực tế sẽ gửi email)"""        
        user = self.find_user_by_email_or_username(identifier)
        if not user:
            return {"status": "error", "message": "Không tìm thấy tài khoản với email/tên đăng nhập này."}
        
        code = ''.join(random.choices(string.digits, k=6))
        # Demo: ghi nhật ký, thực tế nên lưu vào DB và gửi email
        logging.info(f"[DEMO] Mã đặt lại mật khẩu cho {identifier}: {code}")
        user['reset_code'] = code
        user['reset_code_time'] = datetime.now().isoformat()
        users = self.load_users()
        for u in users:
            if u.get('user_id') == user.get('user_id'):
                u['reset_code'] = code
                u['reset_code_time'] = user['reset_code_time']
        self.save_users(users)
        return {"status": "success", "message": "Đã gửi mã đặt lại mật khẩu (xem terminal demo)."}

    def reset_password_with_code(self, identifier, code, new_password):
        user = self.find_user_by_email_or_username(identifier)
        if not user:
            return {"status": "error", "message": "Không tìm thấy tài khoản."}
        if user.get('reset_code') != code:
            return {"status": "error", "message": "Mã xác nhận không đúng."}
        if not is_strong_password(new_password):
            return {"status": "error", "message": "Mật khẩu mới không đủ mạnh."}
        user['password'] = self.hash_password(new_password)
        user['reset_code'] = None
        user['reset_code_time'] = None
        user['updated_at'] = datetime.now().isoformat()
        users = self.load_users()
        for u in users:
            if u.get('user_id') == user.get('user_id'):
                u.update(user)
        self.save_users(users)
        return {"status": "success", "message": "Đặt lại mật khẩu thành công."}

    def add_user(self, email, username, password, full_name="", phone="", date_of_birth="", address="", role="user"):
        try:
            if not email or not username or not password:
                logger.warning("Attempt to add user with empty email, username or password.")
                return {"status": "error", "message": "Email, tên đăng nhập và mật khẩu không được để trống."}

            users = self.load_users()

            if self.find_user_by_email(email):
                logger.warning(f"Attempt to add existing email: {email}")
                return {"status": "error", "message": "Email đã tồn tại."}

            if not self.is_username_unique(username):
                logger.warning(f"Attempt to add existing username: {username}")
                return {"status": "error", "message": "Tên đăng nhập đã tồn tại."}

            if not is_strong_password(password):
                logger.warning(f"Attempt to add user {email} with weak password.")
                return {"status": "error", "message": "Mật khẩu yếu. Phải gồm chữ hoa, thường, số và ký tự đặc biệt, ít nhất 8 ký tự."}

            # Email and Phone validation
            if email and not is_valid_email(email):
                logger.warning(f"Attempt to add user {email} with invalid email: {email}")
                return {"status": "error", "message": "Định dạng email không hợp lệ."}
            if phone and not is_valid_phone(phone):
                logger.warning(f"Attempt to add user {email} with invalid phone: {phone}")
                return {"status": "error", "message": "Định dạng số điện thoại không hợp lệ. (VD: 10-11 số)"}
            if phone and not self.is_phone_unique(phone):
                logger.warning(f"Attempt to add user {email} with non-unique phone: {phone}")
                return {"status": "error", "message": "Số điện thoại đã được sử dụng."}

            # If all validations pass, proceed to create user
            now = datetime.now().isoformat()
            user = {
                "user_id": generate_id("user", users),
                "username": username,
                "password": self.hash_password(password),
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "role": role,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
                "last_login": None,
                "avatar": None,
                "date_of_birth": date_of_birth,
                "address": address
            }
            
            users.append(user)
            if self.save_users(users):
                logger.info(f"Added new user: {email}")
                # Return success dictionary with user data
                return {"status": "success", "user": user}
            else:
                # Return error dictionary if saving fails
                logger.error(f"Failed to save new user {email} to file.")
                return {"status": "error", "message": "Lỗi khi lưu dữ liệu người dùng."}
                
        except ValueError as ve: # Catch specific ValueError from hash_password or other unexpected ValueErrors
            logger.error(f"ValueError during add_user for {email}: {str(ve)}")
            return {"status": "error", "message": str(ve)}
        except Exception as e: # Catch any other unexpected errors
            logger.error(f"Unexpected error adding user {email}: {str(e)}")
            return {"status": "error", "message": "Đã xảy ra lỗi hệ thống khi thêm người dùng."}

    def update_user(self, user_id, **kwargs):
        try:
            if not user_id:
                raise ValueError("User ID is required")
                
            users = self.load_users()
            user_to_update = None
            for u in users:
                if u['user_id'] == user_id:
                    user_to_update = u
                    break
            
            if not user_to_update:
                # This case should ideally not happen if user_id is always valid when called
                logger.error(f"User with ID {user_id} not found for update.")
                raise ValueError(f"User with ID {user_id} not found.")

            user_data_changed = False

            # Validate and prepare email if provided
            if 'email' in kwargs:
                email_to_check = kwargs['email']
                if email_to_check != user_to_update.get('email'):
                    if email_to_check and not is_valid_email(email_to_check): # Use imported function
                        raise ValueError("Định dạng email không hợp lệ.")
                    if email_to_check and not self.is_email_unique(email_to_check, user_id_to_exclude=user_id):
                        raise ValueError("Địa chỉ email đã được sử dụng.")
                    user_to_update['email'] = email_to_check
                    user_data_changed = True

            # Validate and prepare phone if provided
            if 'phone' in kwargs:
                phone_to_check = kwargs['phone']
                if phone_to_check != user_to_update.get('phone'):
                    if phone_to_check and not is_valid_phone(phone_to_check): # Use imported function
                        raise ValueError("Định dạng số điện thoại không hợp lệ. (VD: 10-11 số)")
                    if phone_to_check and not self.is_phone_unique(phone_to_check, user_id_to_exclude=user_id):
                        raise ValueError("Số điện thoại đã được sử dụng.")
                    user_to_update['phone'] = phone_to_check
                    user_data_changed = True
              # Update other allowed fields, including role if provided
            allowed_fields = ['full_name', 'date_of_birth', 'address', 'is_active', 'role', 'avatar'] # Added 'role' and 'avatar'
            for field in allowed_fields:
                if field in kwargs:
                    if user_to_update.get(field) != kwargs[field]:
                        user_to_update[field] = kwargs[field]
                        user_data_changed = True
                            
            if user_data_changed:
                user_to_update['updated_at'] = datetime.now().isoformat()
                if self.save_users(users):
                    logger.info(f"Updated user: {user_id}")
                    return True # Successfully updated
                else:
                    # This case implies save_users failed, which logs its own error
                    raise Exception("Lưu dữ liệu người dùng thất bại sau khi cập nhật.") 
            
            return False # No actual changes were made or needed saving
            
        except ValueError as ve: # Catch ValueErrors from validations and re-raise
            logger.warning(f"Validation error updating user {user_id}: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            # Wrap other exceptions in a generic one or re-raise if specific handling is not needed here
            raise Exception(f"Lỗi không xác định khi cập nhật người dùng: {str(e)}")

    def delete_user(self, user_id):
        try:
            if not user_id:
                raise ValueError("User ID is required")
                
            users = self.load_users()
            
            for i, user in enumerate(users):
                if user['user_id'] == user_id:
                    del users[i]
                    if self.save_users(users):
                        logger.info(f"Deleted user: {user_id}")
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False

    def toggle_user_lock(self, user_id, lock=True):
        try:
            users = self.load_users()
            user_updated = False
            for user in users:
                if user['user_id'] == user_id:
                    user['is_active'] = not lock
                    user['updated_at'] = datetime.now().isoformat()
                    user_updated = True
                    break
            
            if user_updated and self.save_users(users):
                logger.info(f"User {user_id} lock status set to {lock}")
                return True
            logger.warning(f"User {user_id} not found or failed to update lock status.")
            return False
        except Exception as e:
            logger.error(f"Error toggling user lock for {user_id}: {str(e)}")
            return False

    def admin_reset_password(self, user_id, new_password):
        try:
            if not user_id:
                return {"status": "error", "message": "User ID is required."}
            if not new_password:
                return {"status": "error", "message": "New password cannot be empty."}

            if not is_strong_password(new_password): # Use imported function
                return {"status": "error", "message": "Mật khẩu yếu. Phải gồm chữ hoa, thường, số và ký tự đặc biệt, ít nhất 8 ký tự."}

            users = self.load_users()
            user_found = False
            for user in users:
                if user['user_id'] == user_id:
                    user['password'] = self.hash_password(new_password)
                    user['updated_at'] = datetime.now().isoformat()
                    user_found = True
                    break
            
            if not user_found:
                return {"status": "error", "message": "User not found."}

            if self.save_users(users):
                logger.info(f"Admin reset password for user: {user_id}")
                return {"status": "success", "message": "Password reset successfully."}
            else:
                return {"status": "error", "message": "Failed to save updated user data."}
        except Exception as e:
            logger.error(f"Error resetting password for user {user_id}: {str(e)}")
            return {"status": "error", "message": f"An error occurred: {str(e)}"}

    def change_password(self, username, old_password, new_password):
        users = self.load_users()
        for user in users:
            if user['username'] == username and self.check_password(old_password, user['password']):
                if not is_strong_password(new_password): # Use imported function
                    raise ValueError("Mật khẩu mới không đủ mạnh.")
                user['password'] = self.hash_password(new_password)
                user['updated_at'] = datetime.now().isoformat()
                self.save_users(users)
                print("Đổi mật khẩu thành công.")
                return True
        raise ValueError("Sai mật khẩu cũ hoặc người dùng không tồn tại.")

    def deactivate_user(self, username):
        users = self.load_users()
        for user in users:
            if user['username'] == username:
                user['is_active'] = False
                user['updated_at'] = datetime.now().isoformat()
                self.save_users(users)
                print("Tài khoản đã được tắt.")
                return True
        raise ValueError("Không tìm thấy người dùng để tắt.")

    def activate_user(self, username):
        users = self.load_users()
        for user in users:
            if user['username'] == username:
                user['is_active'] = True
                user['updated_at'] = datetime.now().isoformat()
                self.save_users(users)
                print("Tài khoản đã được kích hoạt.")
                return True
        raise ValueError("Không tìm thấy người dùng để kích hoạt.")

    def update_user_info(self, username, full_name=None, email=None, phone=None, date_of_birth=None, address=None):
        users = self.load_users()
        for user in users:
            if user['username'] == username:
                if full_name is not None:
                    user['full_name'] = full_name
                if email is not None:
                    user['email'] = email
                if phone is not None:
                    user['phone'] = phone
                if date_of_birth is not None:
                    user['date_of_birth'] = date_of_birth
                if address is not None:
                    user['address'] = address
                user['updated_at'] = datetime.now().isoformat()
                self.save_users(users)
                print("Thông tin người dùng đã được cập nhật.")
                return True
        raise ValueError("Không tìm thấy người dùng để cập nhật thông tin.")

    def get_all_users(self, active_only=True):
        users = self.load_users()
        return [user for user in users if user['is_active']] if active_only else users

    def get_user_by_id(self, user_id):
        users = self.load_users()
        for user in users:
            if user['user_id'] == user_id:
                return user
        return None  # Thay đổi để trả về None thay vì raise ValueError

    def get_user_avatar(self, username):
        user = self.find_user_by_username(username)
        default_avatar = os.path.join('assets', 'avatar_user_001.jpg')
        if user:
            avatar = user.get('avatar')
            # Nếu avatar là None, rỗng hoặc file không tồn tại thì trả về avatar mặc định
            if avatar and os.path.exists(avatar):
                return avatar
            elif avatar and os.path.exists(os.path.join(os.getcwd(), avatar)):
                return os.path.join(os.getcwd(), avatar)
        return default_avatar

    def set_user_avatar(self, username, avatar_path):
        users = self.load_users()
        for user in users:
            if user['username'] == username:
                user['avatar'] = avatar_path
                user['updated_at'] = datetime.now().isoformat()
                self.save_users(users)
                print("Ảnh đại diện đã được cập nhật.")
                return True
        raise ValueError("Không tìm thấy người dùng để cập nhật ảnh đại diện.")

    def reset_all_passwords(self, new_password="123456aA@"):
        """Reset mật khẩu của tất cả users thành mật khẩu mặc định"""
        if not is_strong_password(new_password): # Use imported function
            raise ValueError("Mật khẩu mới không đủ mạnh")
            
        users = self.load_users()
        updated_count = 0
        
        for user in users:
            user['password'] = self.hash_password(new_password)
            user['updated_at'] = datetime.now().isoformat()
            updated_count += 1
            
        self.save_users(users)
        print(f"Đã reset mật khẩu cho {updated_count} tài khoản")
        return updated_count        

    def get_basic_user_info_list(self):
        users = self.load_users()
        return [
            {
                "user_id": u.get("user_id"),
                "username": u.get("username"),
                "email": u.get("email"),
                "created_at": u.get("created_at"),
                "is_active": u.get("is_active", True)
            }
            for u in users
        ]