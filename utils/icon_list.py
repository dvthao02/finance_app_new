"""
Module chứa danh sách các biểu tượng (icon) dùng trong ứng dụng.
Có thể import và sử dụng ở bất kỳ nơi nào cần dùng icons.
"""

CATEGORY_ICONS = [
    # Thu nhập
    "💰", "💵", "🎁", "💸",

    # Ăn uống
    "🍔", "🧋", "🍽️", "🥘",

    # Di chuyển
    "🚗", "⛽", "🅿️", "🚌",

    # Mua sắm
    "🛍️", "👗", "👟", "💄",

    # Hóa đơn - Tiện ích
    "💡", "🔌", "🚿", "🌐", "📱",

    # Sức khỏe
    "🏥", "🩺", "💊", "🛡️",

    # Giải trí
    "🎮", "🎬", "🎫", "✈️",

    # Giáo dục
    "📚", "🏫", "📖", "💻",

    # Gia đình & Nhà cửa
    "🏠", "🏡", "🧰", "🛋️",

    # Con cái
    "🧒", "📓", "🧸",

    # Tài chính khác
    "💳", "🏦", "📈", "💼",

    # Khác
    "❓"
] 

# Các màu cơ bản cho danh mục
CATEGORY_COLORS = {
    # Thu nhập
    "income": [
        "#34a853",  # Xanh lá - Google
        "#00a86b",  # Xanh lá - Seafoam
        "#4caf50",  # Xanh lá - Material
        "#8bc34a",  # Xanh lá nhạt - Material
        "#cddc39",  # Xanh vàng - Material
        "#7cb342",  # Xanh lá - Light Green
        "#43a047",  # Xanh lá - Green
        "#00c853",  # Xanh lá - Material A400
    ],
    
    # Chi tiêu
    "expense": [
        "#ea4335",  # Đỏ - Google
        "#f44336",  # Đỏ - Material
        "#e53935",  # Đỏ đậm - Material
        "#d32f2f",  # Đỏ đậm - Material
        "#c62828",  # Đỏ đậm - Material
        "#b71c1c",  # Đỏ đậm - Material
        "#ff5252",  # Đỏ nhạt - Material A200
        "#ff1744",  # Đỏ nhạt - Material A400
    ],
    
    # Màu trung tính
    "neutral": [
        "#9e9e9e",  # Xám - Material
        "#607d8b",  # Xanh xám - Material
        "#546e7a",  # Xanh xám đậm - Material
        "#455a64",  # Xanh xám đậm - Material
        "#37474f",  # Xanh xám đậm - Material
        "#263238",  # Xanh xám đậm - Material
    ]
}
