import os
import django
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from django.core.exceptions import ObjectDoesNotExist
import time


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_restaurant.settings')
django.setup()


# Chrome 드라이버 설정
options = Options()
options.add_argument("--headless")  # 브라우저 창을 띄우지 않고 실행
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

start_time = time.time()
from restaurant.models import *
# 비동기 코드에서 ORM 호출 허용
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
Review.objects.all().delete()
# Restaurant 모델에서 2 곳만 읽어서 테스트
i = 1
for restaurant in Restaurant.objects.all():
    driver.get(f'https://app.catchtable.co.kr/ct/shop/{restaurant.restaurant_name_en}/review?type=DINING&sortingFilter=L')

    # 페이지가 로딩될 시간을 기다림
    time.sleep(1)

    # 페이지 스크롤 함수
    def scroll_to_bottom():
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # 끝까지 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.7)  # 스크롤 후 대기 시간

            # 새로운 높이 계산 후 비교
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # 스크롤이 더 이상 불가능할 때 종료
            last_height = new_height

    # 스크롤을 끝까지 내림
    scroll_to_bottom()

    # <br> 태그 제거 함수
    def clean_review_text(text):
        return re.sub(r'<br\s*/?>', '\n', text)  # <br>을 줄바꿈으로 변환

    # 평점과 리뷰 내용 수집
    reviews = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "_10fm75h6"))
        )
        # 모든 평점과 리뷰 요소를 찾음
        ratings = driver.find_elements(By.CLASS_NAME, "_10fm75h6")
        contents = driver.find_elements(By.CLASS_NAME, "review-content")

        for rating, content in zip(ratings, contents):
            # rating 값 정수로 버림
            rating_value = float(rating.text)
            review_type = 'good' if rating_value == 5 else 'bad'
            review_text = clean_review_text(content.get_attribute("innerHTML").strip())

            review_data = {
                "rating": review_type,
                "content": review_text
            }
            reviews.append(review_data)
        
        # Model에 저장
        for review in reviews:
                Review.objects.create(
                    restaurant=restaurant,
                    review_text=review['content'],
                    review_category=review['rating']
                )
        print(str(i),restaurant)
        i+=1
    except Exception as e:
        print(f"오류 발생: {e}")
driver.quit()
end_time = time.time()
execution_time = end_time - start_time
print(f"코드 수행 시간: {execution_time:.6f}초")
