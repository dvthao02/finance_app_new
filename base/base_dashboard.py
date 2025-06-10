from PyQt5.QtWidgets import QMainWindow
import customtkinter as ctk
import os

class BaseDashboard(QMainWindow):
    def __init__(self, master=None):
        super().__init__(master)
        self.current_user = None
        self.current_user_id = None
        self.title(self.get_dashboard_title())
        self.geometry("1100x700")
        self.protocol("WM_DELETE_WINDOW", self.handle_logout)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.init_ui()
        self.logout_callback = None

    def init_ui(self):
        # Header nhỏ phía trên
        header = ctk.CTkFrame(self.main_frame, height=56, fg_color="#1976d2")
        header.pack(fill="x", side="top")
        title = ctk.CTkLabel(header, text=self.get_dashboard_title(), font=("Arial", 18, "bold"), text_color="white")
        title.pack(side="left", padx=16)
        self.avatar_label = ctk.CTkLabel(header, text="", width=40)
        self.avatar_label.pack(side="right", padx=8)
        logout_btn = ctk.CTkButton(header, text="Đăng xuất", fg_color="#fff", text_color="#d93025", command=self.handle_logout)
        logout_btn.pack(side="right", padx=8)
        # Main content: sidebar + content
        body_frame = ctk.CTkFrame(self.main_frame)
        body_frame.pack(fill="both", expand=True)
        self.sidebar = self.create_sidebar(body_frame)
        self.sidebar.pack(side="left", fill="y")
        self.content_area = self.create_content_area(body_frame)
        self.content_area.pack(side="right", fill="both", expand=True)

    def create_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, width=72)
        # ... add sidebar nav buttons here ...
        return sidebar

    def create_content_area(self, parent):
        content = ctk.CTkFrame(parent)
        # ... add content widgets here ...
        return content

    def set_logout_callback(self, callback):
        self.logout_callback = callback

    def handle_logout(self):
        if self.logout_callback:
            self.logout_callback()
        self.destroy()

    def get_dashboard_title(self):
        return "Dashboard"
