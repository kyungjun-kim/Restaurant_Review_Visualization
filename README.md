# crawl_restaurant
흑백요리사에 나온 식당들 리뷰 시각화 서비스


# 초기 데이터 설정방법
- 기존 Model존재 시 삭제, makemigrations, migrate 필요
```sh
$ python manage.py runserver
```
- url접속
    - http://127.0.0.1:8000/restaurant/init
 
# 크롤링 방법
- crawling.py 실행 -> 리뷰 제외한 식당 데이터 DB에 입력
- ReviewCrawl.py 실행 -> 리뷰 데이터 DB에 입력
- **두 코드 순서대로 실행하시면 됩니다.**

# main화면 확인
    - 127.0.0.1:8000/restaurant
