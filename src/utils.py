from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def get_original_url(url):
    options = Options()
    options.add_argument("--headless") # Chạy ẩn danh không hiện cửa sổ
    
    # Khởi tạo driver
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        
        # Chờ một chút để Google thực hiện redirect bằng Javascript
        # Tùy mạng mà chỉnh thời gian, 2-3s thường là đủ
        time.sleep(3) 
        
        # Lấy URL hiện tại sau khi đã redirect
        real_url = driver.current_url
        return real_url
    finally:
        driver.quit()

def testing():
    google_news_url = "https://news.google.com/read/CBMitgFBVV95cUxNTU4xa2FnMXJfZ0lUaC1WY2JxSUU4bVF4dVhHSVpta2RZcGFUY05XeWplemtmcUZzZ1FGTlpoN0JBcm9vakpaQmJ3QnppVFVHT0VaRlhBOGdOUk8yR0dYSzIyZFh5SXZaRzJuVUxpaXpHOUZNQW41Zm1OWGZnSjY0eXZTZnEzQzNLSFpBMmlNdVpONXRmX3Ewcmc3bTZLRUJka0wzVzV4VThmT3dzcGpqYjNsd3Z6dw?hl=vi&gl=VN&ceid=VN%3Avi"
    print("Đang lấy link gốc...")
    real_link = get_original_url(google_news_url)
    print(f"Link gốc là: {real_link}")