import json
import re
import unicodedata
import pandas as pd

class NewsPreprocessor:
    def __init__(self, filepath=None, data=None):
        """
        Khởi tạo bộ tiền xử lý.
        :param filepath: Đường dẫn tới file JSON (nếu có).
        :param data: Dữ liệu dạng list hoặc dict (nếu không load từ file).
        """
        self.data = []
        if filepath:
            self.load_data(filepath)
        elif data:
            self.data = data

    def load_data(self, filepath):
        """Đọc file JSON (xử lý cấu trúc lồng nhau nếu cần)."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                
            # Kiểm tra cấu trúc file (trường hợp file upload có key 'fullContent')
            if isinstance(raw_data, dict) and 'fullContent' in raw_data:
                self.data = raw_data['fullContent']
            elif isinstance(raw_data, list):
                self.data = raw_data
            else:
                raise ValueError("Cấu trúc JSON không được hỗ trợ.")
            
            print(f"✅ Đã load {len(self.data)} bài báo.")
        except Exception as e:
            print(f"❌ Lỗi khi đọc file: {e}")

    def clean_text(self, text):
        """
        Hàm làm sạch văn bản chính cho tiếng Việt.
        """
        if not isinstance(text, str) or not text:
            return ""

        # 1. Chuẩn hóa Unicode (chuyển về dựng sẵn NFC - quan trọng cho tiếng Việt)
        text = unicodedata.normalize('NFC', text)

        # 2. Loại bỏ URL
        text = re.sub(r'https?://\S+|www\.\S+', '', text)

        # 3. Loại bỏ các cụm từ thường gặp trong báo chí (Caption ảnh, nguồn)
        # Ví dụ: "Ảnh: ...", "Nguồn: ...", "Theo ..." ở đầu câu hoặc cuối đoạn
        text = re.sub(r'(Ảnh|Nguồn|Theo)\s*[:].*?(\n|$)', ' ', text, flags=re.IGNORECASE)
        
        # 4. Loại bỏ thông tin ngày tháng rác dạng "13/11/2025 11:21" nằm lơ lửng trong text
        text = re.sub(r'\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{1,2}', '', text)

        # 5. Loại bỏ các ký tự đặc biệt không mong muốn (giữ lại dấu câu cơ bản và tiếng Việt)
        # Pattern này giữ lại chữ cái, số, và các dấu câu phổ biến
        text = re.sub(r'[^\w\s,.;:?!%\(\)\"\'-]', ' ', text)

        # 6. Xử lý khoảng trắng (newlines thành space, xóa double space)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def filter_relevant_content(self, keyword="Credit Suisse"):
        """
        Lọc các bài viết chỉ liên quan đến từ khóa (nếu cần thiết).
        Dữ liệu của bạn có nhiều bài không liên quan (showbiz, tai nạn).
        """
        initial_count = len(self.data)
        # Lọc nếu keyword xuất hiện trong title hoặc content
        self.data = [
            article for article in self.data 
            if keyword.lower() in str(article.get('title', '')).lower() 
            or keyword.lower() in str(article.get('content', '')).lower()
        ]
        print(f"🔍 Đã lọc bài viết theo từ khóa '{keyword}': {initial_count} -> {len(self.data)}")

    def remove_duplicates(self):
        """Loại bỏ các bài báo trùng lặp dựa trên Title."""
        df = pd.DataFrame(self.data)
        if df.empty:
            return
        
        initial_count = len(df)
        # Xóa trùng lặp dựa trên tiêu đề (title)
        df.drop_duplicates(subset=['title'], keep='first', inplace=True)
        
        self.data = df.to_dict('records')
        print(f"🗑️ Đã xóa {initial_count - len(df)} bài viết trùng lặp.")

    def process(self, filter_keyword=None):
        """
        Chạy toàn bộ quy trình tiền xử lý.
        """
        processed_data = []
        
        # Bước 1: Lọc trùng lặp trước khi xử lý để tiết kiệm thời gian
        self.remove_duplicates()

        # Bước 2: Lọc nội dung theo từ khóa (Tùy chọn)
        if filter_keyword:
            self.filter_relevant_content(filter_keyword)

        # Bước 3: Clean text
        for article in self.data:
            clean_article = article.copy()
            
            # Làm sạch Title
            clean_article['clean_title'] = self.clean_text(article.get('title', ''))
            
            # Làm sạch Content
            clean_article['clean_content'] = self.clean_text(article.get('content', ''))
            
            # Tính độ dài word count (hữu ích để lọc bài quá ngắn)
            clean_article['word_count'] = len(clean_article['clean_content'].split())

            # Chỉ lấy bài có nội dung đáng kể (>20 từ)
            if clean_article['word_count'] > 20:
                processed_data.append(clean_article)

        self.data = processed_data
        print("✅ Tiền xử lý hoàn tất.")
        return self.data

    def save_to_json(self, output_path):
        """Lưu kết quả ra file JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        print(f"💾 Đã lưu file tại: {output_path}")

# --- Ví dụ cách sử dụng ---
if __name__ == "__main__":
    # Đường dẫn file của bạn
    input_file = 'news_credit_suisse.json'
    output_file = 'cleaned_news_data.json'

    # Khởi tạo
    processor = NewsPreprocessor(filepath=input_file)

    # Chạy xử lý (Có thể truyền từ khóa 'Credit Suisse' để lọc bỏ tin rác như Showbiz/Tai nạn)
    # Nếu muốn giữ tất cả, để filter_keyword=None
    cleaned_data = processor.process(filter_keyword="Credit Suisse")

    # Xem thử 1 bài
    if cleaned_data:
        print("\n--- Ví dụ bài viết sau khi clean ---")
        print("Title:", cleaned_data[0]['clean_title'])
        print("Content Snippet:", cleaned_data[0]['clean_content'][:200], "...")

    # Lưu file
    processor.save_to_json(output_file)