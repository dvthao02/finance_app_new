from data_manager.user_manager import UserManager
import sys

def main():
    try:
        user_manager = UserManager()
        updated_count = user_manager.reset_all_passwords("12345aA@")
        print(f"Đã reset mật khẩu thành công cho {updated_count} tài khoản")
        print("Mật khẩu mới: 12345aA@")
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
