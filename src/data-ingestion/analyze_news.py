import os
import json
from groq import Groq

# --- CẤU HÌNH API ---
# Thay API Key của bạn vào đây
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "gsk_YOUR_API_KEY_HERE")

class VNSentimentAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        # Dùng Llama 3 70B để hiểu tiếng Việt và ngữ cảnh tài chính tốt nhất
        self.model = "llama3-70b-8192" 

    def analyze(self, news_text):
        """
        Phân tích tin tức Tiếng Việt.
        """
        
        # --- PROMPT KỸ THUẬT (QUAN TRỌNG) ---
        # Chỉ định rõ model đóng vai chuyên gia đọc tiếng Việt
        system_prompt = """
        Bạn là một Chuyên gia Phân tích Rủi ro Tài chính (Financial Risk Analyst).
        Nhiệm vụ: Phân tích các tiêu đề tin tức tiếng Việt về ngân hàng Credit Suisse.
        
        Hãy trả về kết quả dưới dạng JSON (không thêm lời dẫn) với các trường sau:
        1. "sentiment": Chỉ chọn một trong 3 nhãn: "Negative", "Neutral", "Positive".
        2. "risk_score": Số nguyên từ 0 (An toàn) đến 10 (Rủi ro sụp đổ/Hoảng loạn).
        3. "key_factors": Trích xuất 2-3 từ khóa quan trọng nhất trong câu (Tiếng Việt).
        4. "reasoning": Giải thích ngắn gọn tại sao chấm điểm này (bằng Tiếng Việt).
        
        Ví dụ định dạng output mong muốn:
        {
            "sentiment": "Negative",
            "risk_score": 8,
            "key_factors": ["trái phiếu AT1", "vô giá trị"],
            "reasoning": "Việc trái phiếu bị xóa bỏ gây thiệt hại lớn cho nhà đầu tư."
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
                        "content": f"Phân tích tin này: '{news_text}'",
                    }
                ],
                model=self.model,
                temperature=0, # Giữ độ sáng tạo = 0 để kết quả nhất quán
                response_format={"type": "json_object"}, 
            )

            result_json = chat_completion.choices[0].message.content
            return json.loads(result_json)

        except Exception as e:
            print(f"Lỗi khi phân tích: {news_text[:20]}... | {e}")
            return None

# --- CHẠY THỬ NGHIỆM ---
if __name__ == "__main__":
    analyzer = VNSentimentAnalyzer()
    
    # Dữ liệu tiếng Việt thực tế từ log của bạn
    vn_news_samples = [
        "Trái phiếu AT1 là gì và vì sao 17 tỷ USD trái phiếu Credit Suisse trở thành giấy vụn?",
        "Ngân hàng UBS hoàn tất thương vụ thâu tóm Credit Suisse, vươn mình trở thành gã khổng lồ",
        "Credit Suisse được bơm thanh khoản từ Ngân hàng Quốc gia Thụy Sĩ",
        "Vụ sụp đổ của Credit Suisse có thể làm giảm vị thế của Thụy Sĩ trên trường quốc tế"
    ]

    print(f"{'TIN TỨC':<60} | {'RỦI RO (0-10)':<12} | {'CẢM XÚC'}")
    print("-" * 90)

    for news in vn_news_samples:
        result = analyzer.analyze(news)
        if result:
            # Cắt ngắn tiêu đề để hiển thị cho đẹp
            short_title = (news[:55] + '..') if len(news) > 55 else news
            print(f"{short_title:<60} | {result['risk_score']:<12} | {result['sentiment']}")
            print(f"   -> Lý do: {result['reasoning']}")
            print("-" * 90)