import os
import json
import sys
from groq import Groq

class FinancialRiskAnalyzer:
    def __init__(
        self, 
        api_key=None,
        model="llama-3.3-70b-versatile"
    ):
        """
        Khởi tạo Analyzer với API Key và Model.
        Nếu không truyền api_key, nó sẽ tự tìm trong biến môi trường GROQ_API_KEY.
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Không tìm thấy API Key. Vui lòng set biến môi trường GROQ_API_KEY hoặc truyền trực tiếp.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model

    def analyze_news(self, news_text):
        """
        Phân tích đoạn tin tức và trả về dict chứa thông tin đánh giá rủi ro.
        """
        
        # System prompt được thiết kế để ép model trả về JSON chuẩn
        # --- ĐÃ CẬP NHẬT: Thêm "publication_date" và "keywords" ---
        system_prompt = """
        Bạn là một chuyên gia AI về Quản trị Rủi ro Tài chính (Financial Risk Management).
        Nhiệm vụ: Phân tích văn bản tin tức được cung cấp và trích xuất các tín hiệu rủi ro.
        
        YÊU CẦU OUTPUT:
        Chỉ trả về một chuỗi JSON hợp lệ (không markdown, không giải thích thêm) với cấu trúc sau:
        {
            "risk_score": (số nguyên từ 1-10, 10 là cực kỳ nguy hiểm),
            "risk_category": (string, ví dụ: "Thanh khoản", "Pháp lý", "Uy tín", "Thị trường"),
            "sentiment": (string, "Negative" | "Neutral" | "Positive"),
            "key_entities": (list các tổ chức/công ty bị ảnh hưởng),
            "publication_date": (string, trích xuất ngày từ tin tức theo dạng "YYYY-MM-DD". Nếu không tìm thấy, trả về null),
            "keywords": (list 5-7 keywords quan trọng nhất, không trùng lặp),
            "reasoning": (tóm tắt ngắn gọn tại sao lại chấm điểm như vậy, dưới 30 từ)
        }
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"Hãy phân tích tin tức sau:\n{news_text}",
                    }
                ],
                model=self.model,
                temperature=0.1, # Giữ temperature thấp để kết quả ổn định
                response_format={"type": "json_object"}, # Bắt buộc trả về JSON
            )

            # Lấy nội dung trả về
            result_content = chat_completion.choices[0].message.content
            
            # Parse từ string sang Python Dict
            return json.loads(result_content)

        except Exception as e:
            return {
                "error": True,
                "message": str(e)
            }


def example():
    """Hàm ví dụ để test nhanh module này khi chạy như một script."""
    
    # Thêm ngày vào tin tức để test tính năng trích xuất
    sample_news = """
    Tập đoàn Bất động sản ABC vừa tuyên bố vỡ nợ trái phiếu lô A123 trị giá 5000 tỷ đồng. 
    Thông báo này được đưa ra vào sáng ngày 13 tháng 11 năm 2025.
    Chủ tịch tập đoàn hiện không thể liên lạc được. Cổ phiếu sàn hàng loạt.
    """
    
    # --- FIX IMPORT CHO SCRIPT ---
    # Đoạn này xử lý lỗi "attempted relative import with no known parent package"
    try:
        from ..utils import config
    except ImportError:
        print("Đang chạy ở chế độ Script, fix sys.path...")
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        # Nhảy lên 2 cấp (từ src/data-ingestion -> src -> project root)
        project_root = os.path.dirname(os.path.dirname(current_dir))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        try:
            from src.utils import config
        except ImportError:
            print("Lỗi: Không thể tìm thấy src.utils.config. Vui lòng kiểm tra cấu trúc thư mục.")
            return

    # --- XỬ LÝ API KEY ---
    # Giả định hàm config.load_env() sẽ load key vào os.environ
    # (dựa trên module env_loader.py chúng ta đã làm)
    try:
        # Giả sử hàm này là load_and_validate_env
        # Nếu tên hàm của bạn là load_env, hãy sửa lại
        if hasattr(config, 'load_and_validate_env'):
            config.load_and_validate_env(['GROQ_API_KEY'])
        elif hasattr(config, 'load_env'):
             config.load_env(['GROQ_API_KEY'])
        else:
            print("Cảnh báo: Không tìm thấy hàm load_env trong config.")
            
    except Exception as e:
        print(f"Lỗi khi load env: {e}")
        # Dù sao thì class cũng sẽ check os.environ, nên cứ thử tiếp tục
        pass

    # Khởi tạo Analyzer (Class sẽ tự đọc key từ os.environ)
    try:
        analyzer = FinancialRiskAnalyzer()
    except ValueError as e:
        print(e)
        print("-> Hãy đảm bảo bạn đã tạo file .env và set GROQ_API_KEY.")
        return
        
    print("--- Đang phân tích... ---")
    result = analyzer.analyze_news(sample_news)
    
    # In kết quả đẹp
    print(json.dumps(result, indent=2, ensure_ascii=False))


# Sửa lại để chạy hàm example() khi file này được thực thi trực tiếp
if __name__ == "__main__":
    example()