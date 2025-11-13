import os
from dotenv import load_dotenv
from typing import List, Dict

def load_env(required_keys: List[str]) -> Dict[str, str]:
    """
    Tải và kiểm tra danh sách các biến môi trường bắt buộc.
    
    Args:
        required_keys (List[str]): Danh sách các key cần lấy (VD: ['GROQ_API_KEY', 'DB_URL'])
        
    Returns:
        Dict[str, str]: Dictionary chứa các key và value tương ứng.
    """
    
    loaded = load_dotenv(override=True)
    if not loaded:
        print("⚠️ Cảnh báo: Không tìm thấy file .env (Hoặc file rỗng)")

    env_vars = {}
    missing_keys = []

    for key in required_keys:
        value = os.getenv(key)
        if not value:
            missing_keys.append(key)
        else:
            env_vars[key] = value

    if missing_keys:
        error_msg = f"❌ LỖI CẤU HÌNH: Thiếu các biến môi trường sau trong file .env: {', '.join(missing_keys)}"
        raise ValueError(error_msg)
    
    print("✅ Đã tải cấu hình thành công!")
    return env_vars

if __name__ == "__main__":
    try:
        # ĐỊNH NGHĨA DANH SÁCH CẦN LẤY
        my_keys = ["GROQ_API_KEY", "PROJECT_NAME", "DB_PORT"]
        
        # GỌI HÀM
        config = load_env(my_keys)
        
        # TRUY CẬP GIÁ TRỊ
        # Vì đã check lỗi bên trong hàm rồi, ra tới đây là chắc chắn có dữ liệu
        print(f"Đang chạy dự án: {config['PROJECT_NAME']}")
        print(f"API Key là: {config['GROQ_API_KEY'][:5]}...")
        
    except ValueError as e:
        print(e)