import os
import django
import re
import sys

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
from bs4 import BeautifulSoup

# 프로젝트의 최상위 경로를 PYTHONPATH에 추가합니다.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_restaurant.settings')
django.setup()

from restaurant.models import Restaurant, Review, Chef

# Chrome 드라이버 설정
options = Options()
options.add_argument("--headless")  # 브라우저 창을 띄우지 않고 실행
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 비동기 코드에서 ORM 호출 허용
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# 페이지가 로딩될 시간을 기다림
# time.sleep(3)



# 페이지 스크롤 함수
def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 끝까지 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  # 스크롤 후 대기 시간

        # 새로운 높이 계산 후 비교
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # 스크롤이 더 이상 불가능할 때 종료
        last_height = new_height

# <br> 태그 제거 함수
def clean_review_text(text):

    soup = BeautifulSoup(text, 'html.parser')

    # 해시태그 <span class="__hashtag"> 태그들 제거
    for hashtag in soup.find_all('span', class_='__hashtag'):
        hashtag.decompose()


    return re.sub(r'<br\s*/?>', '\n', soup.get_text())  # <br>을 줄바꿈으로 변환



def collect_reviews(restaurant):
    # 평점과 리뷰 내용 수집
    reviews = []
    try:
        # URL 생성 및 페이지 이동
        url = f"https://app.catchtable.co.kr/ct/shop/{restaurant.restaurant_name_en}/review?type=DINING&sortingFilter=L"
        driver.get(url)
        print(f"{restaurant.restaurant_name}의 리뷰 페이지 접근 성공: {url}")

        # 페이지 로딩 대기 및 스크롤
        time.sleep(3)
        scroll_to_bottom()


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

    except Exception as e:
        print(f"{restaurant.restaurant_name} 리뷰 수집 중 오류 발생: {e}")
    
    return reviews

def save_reviews(restaurant, reviews):
    # 기존 리뷰 삭제 후 새로운 리뷰 저장
    Review.objects.filter(restaurant=restaurant).delete()
    print(f"기존 리뷰 삭제 완료: {restaurant.restaurant_name}")

    for review in reviews:
        Review.objects.create(
            restaurant=restaurant,
            review_text=review['content'],
            review_category=review['rating']
        )
        print(f"저장된 리뷰 - 평점: {review['rating']}, 내용: {review['content']}")



# 메인
restaurants = Restaurant.objects.all()
for restaurant in restaurants:
    print(f"'{restaurant.restaurant_name}' 리뷰 수집 시작")
    reviews = collect_reviews(restaurant)
    if reviews:
        save_reviews(restaurant, reviews)
        print(f"'{restaurant.restaurant_name}' 리뷰 수집 완료")
    else:
        print(f"'{restaurant.restaurant_name}'에 대한 리뷰가 없습니다.")


# 드라이버 종료
driver.quit()
print("모든 리뷰 수집 완료")