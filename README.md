<aside>
👉🏻

**목차**

</aside>

## 프로젝트 주제

**🧑‍🍳 흑백요리사 출연 식당 리뷰 시각화 웹 서비스**

## 프로젝트 개요

“**흑백요리사 출연 식당 리뷰 시각화 웹 서비스”**은 현재 가장 반응이 좋은 넷플릭스 TV프로그램 흑백요리사 2라운드에 출현한 셰프들의 식당에 대한 정보를 시각화하는 서비스입니다. **메인 페이지**에서는 2라운드에 진출한 **흑백요리사** 총 40인에 대한 **이미지**와 **이름 혹은 닉네임**을 확인할 수 있습니다. 각 셰프의 이미지를 클릭하면 **상세 페이지**로 이동하게 되고, **셰프의 식당**에 대한 **상세 정보**와 **가격 그래프** 그리고 **리뷰 워드클라우드**를 확인할 수 있습니다.

## 프로젝트 선정 이유

- 넷플릭스 프로그램 **흑백요리사**의 인기에, ****2라운드에 진출한 40인 셰프들의 식당은 큰 주목을 받고 있습니다. 셰프가 직접 운영하는 식당을 예약하기 위해 하루에 10만명이 웹사이트에 방문하는 등의 궁금증은 더 커가고 있습니다. 이를 해소하고자 흑백요리사 출현 식당들의 리뷰들과 가격 그리고 상세 정보를 활용하여 필요한 정보를 제공할 예정입니다.
    
    주목받은 식당을 직접 다녀온 사람들의 경험과 후기를 효과적으로 분석하고 시각화 함으로써, 사용자들은 각 식당의 강점과 약점을 직관적으로 파악할 수 있습니다. 또한, 리뷰 데이터와 함께 가격을 분석해 맛, 서비스, 분위기 등 다양한 요소를 기준으로 식당을 평가할 수 있어 방문 전 참고 자료로 활용될 수 있습니다. 
    

## 프로젝트 세부 결과

### Data Crawling / Data Storage

♾️ [캐치테이블](https://app.catchtable.co.kr/ct/curation/culinaryclasswars?tabIndex=0&currentExhibitionKey=classwars-all&isUseExhibitionFilter=1&hasShopRefsFromClient=1&curationQuickFilterKey=2&serviceType=INTEGRATION&uniqueListId=1728841646438&metaContractedType=0&sortMethod=recommended&centerBoundsLat=35.60447951909298&centerBoundsLng=127.62260840243572&zoomLevel=13&isNewSearchInMap=1) 사이트를 활용한 크롤링으로 식당들의 정보를 수집하였습니다.

- **데이터 크롤링**
    - Selenium을 사용하여 웹 페이지를 자동으로 탐색하도록 구현
    - 모델 구조를 기반으로 셰프, 식당, 메뉴, 리뷰에 대한 데이터를 크롤링
    - 데이터 중복 저장 방지와 예외 처리 구현
- **데이터 저장 및 관리**
    - Django ORM을 사용해 크롤한 데이터를 저장
    - Django의 기본 데이터베이스 SQLite 사용
- 식당 상세 정보 데이터

```python
from restaurant.models import Restaurant, Review, Chef, Menu

# 현재 페이지의 식당 정보 크롤링 함수
def get_res_info(target_text) :
    
    #해당 페이지에 방문한 식당 데이터 추가
    name_chef = getElement('j8dkby0').text.split("\n")[0].split("로 출연")[-1].strip("한 ")
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
    (name_chef, nick_name, name_restaurant, name_restaurant_en, loca_res,
        link_now, rating, rating_cnt, style_restaurant, desc_restaurant, etc_restaurant
    ) = info_list

    try:
        # 쉐프 객체 생성 또는 조회
        chef, _ = Chef.objects.get_or_create(
            chef_name=name_chef,
            defaults={"image_url": "./default_image.jpeg"}
        )

        print("레스토랑 오브젝트")
        #print(Restaurant.objects.all())
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
            time.sleep(2)

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
            review_category = 'good' if rating_value == 5 else 'bad' if rating_value < 3 else 'neutral'

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
```

- 리뷰 데이터
    - 평점 : 평점 5점은 좋은 리뷰, 평점 3~4점은 중립 그리고 평점 1~2점은 나쁜 리뷰로 구분하였습니다.

```python
from restaurant.models import Restaurant, Review, Chef

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
            review_type = 'good' if rating_value == 5 else 'bad' if rating_value < 3 else 'neutral' # 평점 기준 수정
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
```

### Backend

ERD를 통하여 모델을 한눈에 확인할 수 있습니다.

- **Chef** : 쉐프명, 쉐프이미지(이미지 경로)
- **Restaurant** : 식당명, 식당영문명, 주소, 음식유형, 사이트, 리뷰수, 설명
- **Review** : 평가내용, 평점, 평가구분
- **Menu** : 메뉴명, 가격

![image](https://github.com/user-attachments/assets/b0f85b1b-87b2-4f4f-ac47-582b33d49002)


```python
class Chef(models.Model):
    chef_name = models.CharField(max_length=50, verbose_name='쉐프명', null=False)
    image_url = models.CharField(max_length=500, verbose_name='이미지경로', null=False)
    def __str__(self):
        return f'쉐프 : {self.chef_name}'

class Restaurant(models.Model):
    chef = models.ForeignKey(Chef, on_delete=models.CASCADE, related_name='restaurants')  # 쉐프와 연결
    restaurant_name = models.CharField(max_length=100, verbose_name='레스토랑명', null=False)
    restaurant_name_en = models.CharField(max_length=100, verbose_name='레스토랑영문명', null=False)
    address = models.CharField(max_length=200, verbose_name='주소', null=False)
    style = models.CharField(max_length=200, verbose_name='스타일', null=False)
    url = models.CharField(max_length=100, verbose_name='catchtable_url', null=False)
    review_count = models.BigIntegerField(verbose_name='리뷰수', null=False)
    description = models.TextField(verbose_name='설명')

    def __str__(self):
        return f'쉐프 : {self.chef.chef_name} / 레스토랑 : {self.restaurant_name}'

class Review(models.Model):
    REVIEW_CHOICES = [
        ('good', 'Good Review'),
        ('bad', 'Bad Review'),
        ('neutral', 'Neutral Review'),
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')  # 레스토랑과 연결
    review_text = models.TextField(verbose_name='리뷰', null=False)
    review_category = models.CharField(max_length=8, choices=REVIEW_CHOICES, default='neutral', verbose_name='리뷰 종류')

    def __str__(self):
        return f'{self.restaurant.restaurant_name} - {self.get_review_category_display()}'

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')  # 레스토랑과 연결
    menu_name = models.CharField(max_length=100, verbose_name='메뉴명', null=False)
    price = models.CharField(max_length=50, verbose_name='가격', null=False)

    def __str__(self):
        return f'{self.restaurant.restaurant_name} - {self.menu_name} - {self.price} 원'
```

### Frontend

- **메인 페이지**
    - 흑백요리사 2라운드 진출자 40인에 대한 이미지와 이름 혹은 닉네임을 한눈에 볼 수 있습니다.
    - 쉐프의 이미지를 클릭하게 되면 상세 페이지로 이동하게 됩니다.
    
    ![image](https://github.com/user-attachments/assets/c1ad3903-8386-4a3f-b74c-5dea8913e9f8)

    

- **상세 페이지**
    - 해당 쉐프 식당에 대한 상세 정보, 상위 10개의 메뉴 가격과 평균 가격 비교 그래프 그리고 좋은/나쁜 리뷰 워드 클라우드를 확인할 수 있습니다.
    - `목록으로 돌아가기 버튼` 옆, `식당 버튼`을 활용하여 해당 쉐프의 식당을 선택할 수 있습니다.
        
        ![image](https://github.com/user-attachments/assets/2e9715a7-936b-4542-924f-5d7a4e0628f2)

        
        강승원 쉐프의 트리드(trid) 상세 페이지
        
        ![image](https://github.com/user-attachments/assets/665a8e20-380d-497f-9f92-f9bc6f0b2ae6)

        
        윤남노 쉐프의 디핀 deepin 상세 페이지
        
        ![image](https://github.com/user-attachments/assets/890ab840-102c-4a17-8ab7-2685372e3150)

        
        김도윤 쉐프의 윤서울 상세 페이지
        
    

### Data Visualize

- **리뷰 워드클라우드**
    - 좋은 리뷰(5점)와 나쁜 리뷰(1~2점)를 나누어서 워드 클라우드로 나타내었습니다.
    - 두 글자 이상의 명사를 대상으로 워드클라우드가 표현되었으며, 형태소 분석을 위해 konlpy를 사용하였습니다.
    - 불용어 사전을 활용해 리뷰에 자주 등장하지만 도움이 되지 않는 단어들을 제거하여, 워드 클라우드의 직관적 이해를 향상시켰습니다.
    - 워드 클라우드 생성시 mask 이미지를 활용하여 좋은/나쁜 리뷰 단어가 직관적으로 보이도록 표현하였습니다.
    
    ```python
    def make_wordcloud(reviews_list: List[str], font_path: str, num_each_fold: int, good_words: List[str],
                        stopwords_path:Union[str, None]=None,
                        mask_img_path:Union[str, None]=None) -> Union[str, None]:
        if not reviews_list:
            return None
        
        if stopwords_path:
            stopwords = open(stopwords_path, 'r', encoding='utf-8')
            stopwords_list = [line.split('\n')[0] for line in stopwords.readlines()]
            stopwords.close()
        
        mask_img_data = None
        if mask_img_path:
            mask_img_data = np.array(Image.open(mask_img_path))
        
        # 형태소 분석을 통해 명사 추출 및 카운팅
        hannanum = Hannanum()
        noun_counter = Counter()
        total_num = len(reviews_list)
    
        for i in range((total_num + num_each_fold - 1) // num_each_fold): 
            reviews_text = ""
            
            # 슬라이싱할 때 리스트 크기를 초과하지 않도록 보장
            for s in reviews_list[i*num_each_fold:min((i+1)*num_each_fold, total_num)]:
                if s:
                    reviews_text += s + ' ' 
                
            nouns = hannanum.nouns(reviews_text)
            
            if not good_words:
                for noun in nouns:
                    good_words.append(noun)
            else:
                nouns = [noun for noun in nouns if noun not in good_words]
            
            filtered_nouns = [noun for noun in nouns if len(noun) > 1]
            if stopwords_path:
                filtered_nouns = [nouns for nouns in filtered_nouns if nouns not in stopwords_list]
            noun_counter.update(filtered_nouns) 
    
        
        if not noun_counter:
            noun_counter.update(["리뷰X"])  
    
        # WordCloud 생성
        wordcloud = WordCloud(
            font_path=font_path,
            background_color='white',
            width=500,
            height=500,
            mask=mask_img_data,
        ).generate_from_frequencies(noun_counter)  # 카운터로부터 워드클라우드 생성
    
        # 이미지로 저장
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')  # 축을 숨김
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)
    
        # 이미지를 base64로 인코딩하여 반환
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
        return image_base64
    ```
    
- **가격 그래프**
    - 전체 식당 평균 가격과 해당 식당의 평균 가격을 비교하여 막대 그래프로 구현하였습니다.
    
    ```python
    def avg_price_plot(mean_restaurant_price, this_restaurant_price, font_path):
        font_prop = font_manager.FontProperties(fname=font_path)
        
        fig, ax = plt.subplots(figsize=(5,5))
        bar_plot = ax.bar(['평균 가격', '이 식당의 가격'], [mean_restaurant_price, this_restaurant_price], color=['#4CAF50', '#F44336'])
        ax.set_xticklabels(['평균 가격', '이 식당의 가격'], fontproperties=font_prop)
        ax.set_title('가격 수', fontproperties=font_prop)
        ax.set_ylabel('가격', fontproperties=font_prop)
    
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        
        return plot_base64
    ```
    
    - 해당 식당 상위 10개의 메뉴 가격을 막대 그래프로 구현하였습니다.
    
    ```python
    def menu_price_plot(menu, price, font_path, top_k=10):
        font_prop = font_manager.FontProperties(fname=font_path)
        menu = menu[:top_k]
        price = price[:top_k]
    
        df = pd.DataFrame({"menu":menu, "price":price})
        df_sorted = df.sort_values("price")
    
        fig, ax = plt.subplots(figsize=(12,6))
        bar_plot = ax.barh("menu", "price", data=df_sorted)
        ax.set_yticklabels(df_sorted["menu"], fontproperties=font_prop)
        ax.set_title('메뉴 가격', fontproperties=font_prop)
        ax.set_xlabel('가격', fontproperties=font_prop)
    
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
        return plot_base64
    ```
    

## 활용 기술 및 프레임워크

**Frontend**

- Html/Css
- JavaScript

**Backend**

- Framework: Django(Python3)
- DataBase: Sqlite
- ORM: Django ORM

**Crawling**

- Selenium

**Communication & Collaboration Tools**

- Git/GitHub
- Slack
- Notion
- Zoom

## 팀원 및 역할

크롤링 & 백엔드 : 강명주, 김경준, 이준호

프론트엔드 & 백엔드 : 김선재

프론트엔드 & 시각화 : 송기웅(⭐️팀장), 정동민

프론트엔드 & 보고서 : 현승현

## 프로젝트 결론

**“흑백요리사 출연 식당 리뷰 시각화 웹 서비스”** 프로젝트는 현재의 트렌드를 빠르게 반영하여 인기가 많은 식당에 대한 정보를 사용자에게 손쉽게 제공하는 데 중점을 두고 있습니다. 사용자는 자신이 방문하고 싶은 식당의 평점과 리뷰를 기반으로 직관적으로 정보를 얻을 수 있으며, 리뷰는 좋은 리뷰와 나쁜 리뷰로 구분됩니다. 이를 통해 사용자는 식당에 대한 명확한 인상을 쉽게 얻을 수 있으며, 단순히 수치화된 평점만이 아닌 실제 고객들의 경험을 바탕으로 식당을 평가할 수 있게 됩니다.

또한, 식당의 상위 10개 메뉴와 평균 가격을 제공하여 가격대에 대한 감을 잡을 수 있도록 하였습니다. 이를 보충하기 위해, 2라운드에 진출한 40인의 쉐프 식당들의 메뉴 평균 가격과 비교할 수 있는 기능을 추가하였습니다. 이를 통해 사용자는 방문하려는 식당의 가격대가 다른 인기 식당들에 비해 어떤 수준인지 직관적으로 파악할 수 있습니다. 이 정보는 사용자가 자신의 예산에 맞는 식당을 선택하는 데 큰 도움을 줄 것입니다.

프로젝트는 사용자의 편의성을 극대화하는 데 중점을 두었으며, 식당의 상세 정보 제공을 단순화하고 빠르게 접근할 수 있도록 설계되었습니다. 식당의 평점, 리뷰, 가격 정보를 한눈에 볼 수 있는 이 시스템은 사용자가 식당 선택에 있어 더 많은 정보와 확신을 가지고 결정을 내릴 수 있게 합니다.


