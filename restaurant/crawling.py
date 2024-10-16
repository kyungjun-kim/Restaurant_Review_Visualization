import os
import django
import sys

# 프로젝트의 최상위 경로를 PYTHONPATH에 추가합니다.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Django 설정 파일 로드
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_restaurant.settings")  # 'web_restaurant'-> 프로젝트 이름에 맞게 수정.
# Django 초기화
django.setup()

import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException,ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from restaurant.models import Restaurant, Review, Chef, Menu
from selenium.webdriver.common.action_chains import ActionChains


# 웹드라이버 설정
options = Options()
options.add_argument("--disable-features=UseTensorFlowLite")  # TensorFlow Lite 비활성화
# options.add_argument("--headless")  # 필요시 헤드리스 모드 사용
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://app.catchtable.co.kr/ct/curation/culinaryclasswars?tabIndex=0&currentExhibitionKey=classwars-all&isUseExhibitionFilter=1&hasShopRefsFromClient=1&curationQuickFilterKey=2&serviceType=INTEGRATION&uniqueListId=1728841646438&metaContractedType=0&sortMethod=recommended&centerBoundsLat=35.60447951909298&centerBoundsLng=127.62260840243572&zoomLevel=13&isNewSearchInMap=1")
time.sleep(2)  # 페이지 로딩 대기

visited_restaurants = set()  # 방문한 식당 저장
collected_reviews = []  # 수집한 리뷰 저장
# collected_menus = []  # 수집한 메뉴 저장

# 코드 단축 함수
def getElement(link) :
    return driver.find_element(By.CLASS_NAME, link)
def getElements(link) :
    return driver.find_elements(By.CLASS_NAME, link)

# 현재 페이지의 식당 정보 크롤링 함수
def get_res_info(target_text) :
    
    #해당 페이지에 방문한 식당 데이터 추가
    name_chef = getElement('j8dkby0').text.split("\n")[0].split("로 출연한 ")[-1]
    try :
        nick_name = getElement('j8dkby0').text.split("\n")[0].split("로 출연한 ")[0].strip("으")
    except :
        nick_name = ""
    
    #현재 식당링크 :
    link_now = driver.current_url
    
    # 식당명 (한글, 영어)
    name_restaurant = target_text
    name_restaurant_en = link_now.split("/")[-1].split("?")[0]
    
    #평점 정보
    try : 
        rating = float(getElement('dl6idsb').text)
        rating_cnt = getElement('dl6idsc').text
        rating_cnt = int("".join(re.findall(r'\d+', rating_cnt)))
    except :
        rating = 0.0
        rating_cnt = 0
        print("평점 정보 X")

    #식당 설명
    style_restaurant = getElement('dl6ids4').text.split("\n")[-1]
    try :
        desc_restaurant = getElement('mxtve20').text
    except :
        desc_restaurant = ""
        print("식당 설명 X")

    #특이 사항
    etc_restaurant = ""
    etc_restaurant += getElements('_1ltqxco1g')[3].text.replace("\n"," , ") + ""
    etc_restaurant += " , ".join(getElements('v-scroll-inner')[1].text.split())

    #영업 시간 -> DB에 어떤 형태로 들어가는지에 따라 보완 예정
    #getElements('_1ltqxco1g')[-1].click()
    #time_restaurant = 

    #식당 위치
    getElement('_1ltqxco1g').click()
    loca_res = getElement('zn9ch54').text.split("\n")[0]
    
    tmp = [name_chef, nick_name ,
           name_restaurant, name_restaurant_en
           ,loca_res, link_now
           ,rating, rating_cnt
           , style_restaurant, desc_restaurant
           ,etc_restaurant
           ]
    return tmp


# 식당 리스트 페이지 스크롤
def scroll_and_visit_restaurants():
    """모든 식당을 순서대로 방문하며 데이터를 수집"""
    visited_indices = set()  # 방문한 식당 인덱스 저장

    while True:

        # 1. 현재 페이지의 모든 virtual_{i} 요소 수집
        elements = driver.find_elements(By.CSS_SELECTOR, 'div[id^="virtual_"][data-index]')

        new_elements_found = False

        for element in elements:
            try:
                # 각 element의 data-index 값을 추출
                index = int(element.get_attribute("data-index"))

                if index not in visited_indices:
                    visited_indices.add(index)
                    restaurant_name = element.find_element(By.CLASS_NAME, "ShopListItem_title__1p45wh65").text.strip()

                    print(f"새로운 식당 발견: {restaurant_name} (index: {index})")

                    visit_and_collect_data(element, restaurant_name)
                    new_elements_found = True

                else:
                    continue

            except Exception as e:
                continue

        # 3. 스크롤 아래로 내리기
        # driver.execute_script("window.scrollBy(0, 1500);")
        # print("스크롤 다운")
        time.sleep(1)

        if not new_elements_found:
            print("더 이상 스크롤할 수 없습니다. 모든 식당을 수집했습니다.")
            break



#  식당 방문 후 데이터 수집
def visit_and_collect_data(restaurant_element, restaurant_name):
    try:
        # 스크롤을 사용해 요소가 보이도록 처리
        actions = ActionChains(driver)
        actions.move_to_element(restaurant_element).perform()
        time.sleep(1)

        restaurant_element.click()
        print(f"'{restaurant_name}' 클릭 성공")
        time.sleep(2)

        """코드 수정 / collect_chef_and_restaurant 에 수정 (김경준)"""
        tmp = get_res_info(restaurant_name)   


        chef = driver.find_element(By.CLASS_NAME, "j8dkby2")
        chef_name = chef.text.strip()
        print(f"셰프 이름: {chef_name}")

        # 쉐프와 레스토랑 정보 저장
        restaurant = collect_chef_and_restaurant(tmp)
        #restaurant = collect_chef_and_restaurant(chef_name, restaurant_name)    # Restaurant 인스턴스가 반환되어 저장됨

        # 메뉴 정보 수집 및 저장
        collect_menus(restaurant)

        # 리뷰 수집 및 저장
#        collect_reviews(restaurant_name)   # 리뷰 미구현으로 주석 처리

        # 식당 리스트로 돌아가기
        driver.back()
        time.sleep(2)
        driver.back()  
        time.sleep(2)

    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
        print(f"식당 방문 중 오류: {e}")


# 쉐프, 레스토랑 데이터 수집 및 저장
def collect_chef_and_restaurant(info_list):
    """쉐프와 레스토랑 정보를 저장하고 레스토랑 객체를 반환"""
    
    # 전달된 정보 리스트 해제
    (
        name_chef, nick_name, name_restaurant, name_restaurant_en, loca_res,
        link_now, rating, rating_cnt, style_restaurant, desc_restaurant, etc_restaurant
    ) = info_list

    try:
        # 쉐프 객체 생성 또는 조회
        chef, _ = Chef.objects.get_or_create(
            chef_name=name_chef,
            defaults={"image_url": "./default_image.jpeg"}
        )

        # 레스토랑 객체 생성 또는 조회 (모든 필드를 defaults에 포함)
        restaurant, created = Restaurant.objects.get_or_create(
            restaurant_name=name_restaurant,
            chef=chef,
            defaults={
                "restaurant_name_en": name_restaurant_en,
                "address": loca_res,
                "style": style_restaurant,
                "url": link_now,
                "review_count": rating_cnt if rating_cnt is not None else 0,  # None일 경우 0으로 설정
                "description": desc_restaurant,
            }
        )

        if created:
            print(f"'{name_restaurant}' 저장 성공")
        else:
            print(f"'{name_restaurant}'은 이미 존재합니다.")

        return restaurant

    except Exception as e:
        print(f"쉐프 또는 레스토랑 저장 중 오류: {e}")
        return None


# 식당 메뉴와 가격 정보 수집, 저장
def collect_menus(restaurant):
    try:
        menus = []  # 매번 새로운 메뉴 리스트 생성, 식당과의 미스매치 방지

        # 메뉴 탭 클릭 (정확한 탭 클래스 이름을 사용해야 함)
        menu_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '메뉴')]"))   # 식당마다 탭 클래스명이 상이하여 xpath로 탐색
        )

        # 인덱스 41일 때 안되는 경우 예외 처리 (오팬파이어)
        if restaurant.restaurant_name == "오팬파이어" :
            menu_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="wrapperDiv"]/nav/ul/li[2]/a'))   # 예외 처리
            )

        menu_tab.click()  # 메뉴 탭 클릭
        print(f"'{restaurant.restaurant_name}'의 메뉴 탭 클릭 성공")
        time.sleep(2)  # 탭 클릭 후 로딩 대기

        # 메뉴 정보 수집
        menu_elements = driver.find_elements(By.CLASS_NAME, "_16e3mg81")
        if not menu_elements:  # 클래스명이 상이해 수집되지 않는 경우
            menu_elements = driver.find_elements(By.CLASS_NAME, "_1bx9okgf")

        # 메뉴 요소에서 데이터 수집/첫번째 클래스명이 없을 시 두 번째 클래스명으로 처리
        for menu in menu_elements:
            try:
                menu_name = menu.find_element(By.CLASS_NAME, "_16e3mg82").text.strip()
                price = menu.find_element(By.CLASS_NAME, "_16e3mg84").text.strip()
            except NoSuchElementException:  # 두 번째 클래스명 처리
                menu_name = menu.find_element(By.CLASS_NAME, "_1bx9okgh._1ltqxco1g").text.strip()
                price = menu.find_element(By.CLASS_NAME, "_1bx9okgi._1ltqxco1n").text.strip()

            menus.append({"name": menu_name, "price": price})
            print(f"수집된 메뉴 - 이름: {menu_name}, 가격: {price}")

        # 수집된 메뉴를 DB에 저장
        save_menus_to_db(restaurant, menus)

    except (NoSuchElementException, TimeoutException) as e:
        print(f"메뉴 수집 중 오류: {e}")


# 메뉴를 DB에 저장
def save_menus_to_db(restaurant, menus):
    try:
        # 기존 메뉴 삭제 후 새 메뉴 저장
        Menu.objects.filter(restaurant=restaurant).delete()
        print(f"기존 메뉴 삭제 완료: {restaurant.restaurant_name}")

        # 메뉴 저장
        for menu in menus:
            Menu.objects.create(
                restaurant=restaurant,
                menu_name=menu['name'],
                price=menu['price']
            )
            print(f"저장된 메뉴 - 이름: {menu['name']}, 가격: {menu['price']}")

    except Exception as e:
        print(f"메뉴 저장 중 오류: {e}")



# 리뷰와 평점을 수집, 저장
def collect_reviews(restaurant_name):
    try:
        # 1. 리뷰 탭 클릭
        review_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '리뷰')]"))  # 식당마다 탭 클래스명이 상이하여 xpath로 탐색
        )
        review_tab.click()  # 리뷰 탭 클릭
        print(f"'{restaurant_name}'의 리뷰 탭 클릭 성공")
        time.sleep(2)  # 탭 클릭 후 페이지 로딩 대기

#        scroll_to_bottom()  # 페이지 끝까지 스크롤   # 데이터 샘플링을 위한 주석 처리/테스트 이후 주석 해제
#        time.sleep(2)  # 스크롤 후 페이지 로딩 대기

        # 리뷰와 평점이 포함된 부모 요소들을 모두 가져오기
        review_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "review-item"))
        )

        # 부모 요소에서 평점과 리뷰 텍스트를 함께 추출
        for element in review_elements:
            rating = element.find_element(By.CLASS_NAME, "_10fm75h6").text.strip()
            content = element.find_element(By.CLASS_NAME, "review-content").get_attribute("innerHTML").strip()

            # 평점에 따라 카테고리 분류
            rating_value = float(rating)
            review_category = 'good' if rating_value >= 4 else 'bad'

            # HTML 정제 후 저장
            review_text = clean_html_text(content)

            # 수집한 리뷰를 리스트에 저장
            collected_reviews.append({
                "category": review_category,
                "content": review_text
            })

            print(f"수집된 리뷰 - 평점: {review_category}, 내용: {review_text}")

        # 수집된 데이터를 DB에 저장
        save_reviews_to_db(restaurant_name)

    except (TimeoutException, NoSuchElementException) as e:
        print(f"리뷰 수집 중 오류: {e}")


# 리뷰를 DB에 저장
def save_reviews_to_db(restaurant_name):
    try:
        # 기존 리뷰 삭제 후 새 리뷰 저장
        Review.objects.filter(restaurant=restaurant).delete()
        print(f"기존 리뷰 삭제 완료: {restaurant_name}")

        for review in collected_reviews:
            Review.objects.create(
                restaurant=restaurant,
                review_text=review['content'],
                review_category=review['category']
            )
            print(f"저장된 리뷰 - 평점: {review['category']}, 내용: {review['content']}")

    except Exception as e:
        print(f"리뷰 저장 중 오류: {e}")


# 페이지 끝까지 스크롤
def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# <br> 태그를 줄바꿈으로 변환
def clean_html_text(text):
    return re.sub(r'<br\s*/?>', '\n', text)


# 메인 실행
scroll_and_visit_restaurants()
driver.quit()