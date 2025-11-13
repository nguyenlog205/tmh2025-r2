import os
from typing import List
from dotenv import load_dotenv

def load_env(
    required_vars: List[str]
) -> None:
    """
    Load file .env và kiểm tra xem các biến bắt buộc có tồn tại không.
    Args:
        required_vars (List[str]): Danh sách các tên biến môi trường cần kiểm tra (ví dụ: ['GROQ_API_KEY', 'DB_URL']).
    
    """
    
    # Load biến từ file .env vào os.environ
    load_dotenv()

    

    # 3. Tìm và kiểm tra các biến bị thiếu
    if not required_vars:
        return
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        error_msg = f"❌ Lỗi cấu hình: Thiếu các biến môi trường sau: {', '.join(missing_vars)}"
        raise EnvironmentError(error_msg)

    print("✅ Đã load và kiểm tra môi trường thành công.")