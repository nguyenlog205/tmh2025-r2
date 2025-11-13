import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class ViT5Summarizer:
    def __init__(self, model_name="VietAI/vit5-large-vietnews-summarization"):
        """
        Khởi tạo model và tokenizer một lần duy nhất.
        """
        print(f"⏳ Đang tải model {model_name}...")
        
        # Tự động chọn GPU nếu có, không thì dùng CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"⚙️ Thiết bị đang sử dụng: {self.device.upper()}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(self.device)
        
        print("✅ Model đã sẵn sàng!")

    def summarize_one(self, text, max_length=256, min_length=50):
        """
        Hàm xử lý 1 bài news.
        :param text: Nội dung bài báo (đã được clean).
        :param max_length: Độ dài tối đa của tóm tắt.
        :return: Chuỗi văn bản tóm tắt.
        """
        if not text or len(text.strip()) < 50:
            return ""

        # Chuẩn bị input theo format của VietNews
        input_text = "vietnews: " + text + " </s>"
        
        # Tokenize và đưa vào thiết bị (GPU/CPU)
        # padding và truncation để đảm bảo input không quá dài gây lỗi bộ nhớ
        encoding = self.tokenizer(
            input_text, 
            return_tensors="pt", 
            padding=True, 
            truncation=True, 
            max_length=1024 
        )
        
        input_ids = encoding["input_ids"].to(self.device)
        attention_masks = encoding["attention_mask"].to(self.device)

        # Generate tóm tắt
        with torch.no_grad(): # Tắt gradient để tiết kiệm VRAM và chạy nhanh hơn
            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_masks,
                max_length=max_length,
                min_length=min_length,
                num_beams=4,          # Beam search giúp câu văn hay hơn
                early_stopping=True,
                no_repeat_ngram_size=3 # Tránh lặp từ
            )

        # Decode kết quả
        summary = self.tokenizer.decode(
            outputs[0], 
            skip_special_tokens=True, 
            clean_up_tokenization_spaces=True
        )
        
        return summary

def summarize_for_file(
    filepath = r'data\bronze\news\news_credit_suisse.json',
    output_path = r'data\bronze\news\summarized_credit_suisse.json'
):
    import pandas as pd
    summarizer = ViT5Summarizer()
    dataset = pd.read_json(filepath)
    content = dataset['content']
    summarized_content = pd.Series('', index=content.index, dtype='object')
    count = 0

    for idx, news in enumerate(content):
        if idx < 25:
            continue

        print(f'Processing the {idx}\'th news')
        summarized_content[idx] = summarizer.summarize_one(news)
        count=count+1
        # break
    
    dataset['summarision'] = summarized_content
    print(f'Đã tóm tắt {count} bào báo')
    
    
    dataset.to_json(
        r'..\data\bronze\news\summarized_credit_suisse.json',
        orient='records',
        indent=4,
        force_ascii=False,
        #encoding='utf-8'  # Thêm cái này để đảm bảo file lưu chuẩn UTF-8
    )

# summarize_for_file()





# --- Test nhanh nếu chạy trực tiếp file này ---
def main():
    summarizer = ViT5Summarizer()
    test_text = "VietAI là tổ chức phi lợi nhuận với sứ mệnh ươm mầm tài năng về trí tuệ nhân tạo."
    print("Tóm tắt thử:", summarizer.summarize_one(test_text))