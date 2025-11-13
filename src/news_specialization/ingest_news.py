# https://news.google.com/home?hl=vi&gl=VN&ceid=VN:vi

import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup
import pandas as pd

# ===========================================================================================================================
# Hyperparameter Configuration 
# ===========================================================================================================================
MAIN_URL = 'https://news.google.com/home?hl=vi&gl=VN&ceid=VN:vi'

# ===========================================================================================================================
# Driver Loading Function 
# ===========================================================================================================================

def load_driver() -> webdriver.Chrome | None:
    """
    Khởi tạo Chrome WebDriver ở chế độ cơ bản nhất để chạy local.
    """
    options = webdriver.ChromeOptions()
    try:
        print("🚀 Đang khởi tạo Chrome WebDriver (chế độ cơ bản)...")
        driver = webdriver.Chrome(options=options)
        print("✅ WebDriver đã sẵn sàng.")
        return driver
        
    except WebDriverException as e:
        print(f"❌ Lỗi: Không thể khởi tạo WebDriver.")
        print(f"- Vui lòng kiểm tra xem bạn đã cài đặt trình duyệt Google Chrome chưa.")
        print(f"- Lỗi chi tiết: {e}")
        return None









# ===========================================================================================================================
# Ingesting News Functionality
# ===========================================================================================================================

SELECTORS = {
    "search_box": 'input[aria-label="Tìm kiếm chủ đề, vị trí và nguồn"]',
    "article_container": "article.IFHyqb",
    "link_and_title": "a.JtKRv",
    "source": "div.vr1PYe",
    "timestamp": "time.hvbAAd"
}

def _parse_page_source(soup: BeautifulSoup, seen_urls: set, keyword: str) -> list:
    """
    Hàm phụ trợ: Bóc tách dữ liệu từ soup và trả về các bài viết MỚI.
    """
    new_results = []
    articles = soup.select(SELECTORS["article_container"])

    for article in articles:
        link_tag = article.select_one(SELECTORS["link_and_title"])
        if not link_tag:
            continue

        relative_url = link_tag.get('href', '').lstrip('.')
        full_url = "https://news.google.com" + relative_url

        if full_url not in seen_urls:
            seen_urls.add(full_url)
            source_tag = article.select_one(SELECTORS["source"])
            time_tag = article.select_one(SELECTORS["timestamp"])

            new_results.append({
                'keyword': keyword,
                'title': link_tag.text.strip(),
                'source': source_tag.text.strip() if source_tag else "N/A",
                'timestamp': time_tag.text.strip() if time_tag else "N/A",
                'url': full_url
            })
    return new_results



from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from newspaper import Article
def get_article_details(
    url: str,
    temp_driver
) -> str:
    """
    Sử dụng newspaper3k để truy cập một URL và bóc tách nội dung chính.
    """
    # Trích xuất link gốc
    def _get_original_url(
        url
    ):
        temp_driver.get(url)
        time.sleep(3) 
        real_url = temp_driver.current_url
        return real_url
    
    original_url = _get_original_url(url)
    try:
        # Tải và phân tích bài báo
        article = Article(original_url)
        article.download()
        article.parse()
        # Trả về toàn bộ nội dung text của bài báo
        return article.text
    except Exception as e:
        print(f"   -> Lỗi khi bóc tách url {url}: {e}")
        return "" # Trả về chuỗi rỗng nếu có lỗi




def get_news(keyword: str, driver: webdriver.Chrome, topk: int = 50) -> list | None:
    """
    Hàm chính: Điều khiển trình duyệt, tìm kiếm, cuộn trang và gọi hàm phụ trợ để bóc tách.
    """
    if not driver:
        print("WebDriver không khả dụng.")
        return None
    
    try:
        print(f"Bắt đầu quá trình lấy ÍT NHẤT {topk} tin cho từ khóa: '{keyword}'")
        driver.get(MAIN_URL)
        
        search_box = driver.find_element(By.CSS_SELECTOR, SELECTORS["search_box"])
        search_box.click()
        search_box.send_keys(keyword + Keys.RETURN)
        time.sleep(3)
        print("-> Tìm kiếm thành công.")

        print("-> Bắt đầu cuộn trang linh hoạt...")
        all_results = []
        seen_urls = set()
        patience = 3
        stalls = 0

        while True:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            newly_found_articles = _parse_page_source(soup, seen_urls, keyword)

            if newly_found_articles:
                all_results.extend(newly_found_articles)
                print(f"   -> Đã tìm thấy {len(newly_found_articles)} tin mới. Tổng cộng: {len(all_results)}.")
            
            if len(all_results) >= topk:
                print(f"   -> Đã đạt hoặc vượt mức tối thiểu {topk} bài viết. Dừng cuộn.")
                break

            last_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3.5)
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                stalls += 1
                if stalls >= patience:
                    print(f"   -> Đã cuộn đến cuối trang. Dừng lại.")
                    break
            else:
                stalls = 0

        print(f"✅ Quá trình hoàn tất. Thu được {len(all_results)} bài viết.")
        return all_results

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi trong hàm get_news: {e}")
        return None
    








# ===========================================================================================================================
# Lưu dữ liệu
# ===========================================================================================================================
import os, json

def save(result, keyword):
    if result:
        # 1. Chuẩn bị đường dẫn và tên file động
        output_dir = 'data'
        filename = f"news_{keyword.replace(' ', '_').lower()}.json"
        output_path = os.path.join(output_dir, filename)

        # 2. Đảm bảo thư mục 'data' tồn tại
        os.makedirs(output_dir, exist_ok=True)

        # 3. Mở file và sử dụng json.dump() để ghi dữ liệu
        # encoding='utf-8' là cần thiết cho tiếng Việt
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(
                result,             # Dữ liệu cần ghi (toàn bộ danh sách 'result')
                f,                  # Đối tượng file để ghi vào
                ensure_ascii=False, # Quan trọng: Để hiển thị đúng tiếng Việt có dấu
                indent=2            # Thụt lề 2 dấu cách để file dễ đọc và "đẹp"
            )
        
        print(f"✅ Đã lưu thành công file JSON vào: '{output_path}'")
    else:
        print("Không có dữ liệu để lưu.")

# ===========================================================================================================================
# Main Execution
# ===========================================================================================================================
def main():
    # INPUT
    keywords = ["Credit Suisse"] 

    # SELF-CONFIGURATION 
    driver = load_driver()
    temp_driver = load_driver()

    if not driver:
        print("Không thể khởi tạo driver. Dừng chương trình.")
        return
    if not temp_driver:
        print("Không thể khởi tạo driver. Dừng chương trình.")
        return
    
    # START EXECUTING TASK
    try:
        for keyword in keywords:
            result = get_news(keyword, driver)
            if result:
                print(f"\n--- Bắt đầu lấy nội dung chi tiết cho {len(result)} bài viết về '{keyword}' ---")

                for item in result:
                    print(f"-> Đang xử lý: {item['title'][:60]}...")
                    item['content'] = get_article_details(
                        item['url'],
                        temp_driver = temp_driver
                    )
                
                save(result, keyword)
            else:
                print(f"Không tìm thấy bài viết nào cho từ khóa '{keyword}'.")

    finally:
        if driver:
            driver.quit()
            print("\nĐã đóng WebDriver.")
        
    

main()