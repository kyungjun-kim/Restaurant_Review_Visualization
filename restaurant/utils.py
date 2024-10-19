
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd

# 문장에서 명사를 추출하는 형태소 분석 라이브러리
import jpype
from konlpy.tag import Hannanum
import io, os, sys
import base64

from .draw_plot import make_wordcloud, avg_price_plot, menu_price_plot

from restaurant.models import *


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
font_path = os.path.join('restaurant/static/fonts/D2Coding-Ver1.3.2-20180524.ttc')
stopwords_path = os.path.join('restaurant/static/txt/stopwords.txt')
thumb_up_img_path = os.path.join('restaurant/static/png/thumb_up.png')
thumb_down_img_path = os.path.join('restaurant/static/png/thumb_down.png')


def make_chef_json(chef_instance):
    """
        < json구조 >
        chef_json = {
            "chef_name" : 
            "image_url" :
            "restaurants" : [
                {
                    "restaurant_name": 
                    "address": 
                    "style": 
                    "url": 
                    "review_count": ,
                    "description": 
                    "menus": [{"menu_name":~~, "price":~~}, {"menu_name":~~, "price":~~}],
                    "reviews": {"good_reviews": Object, "baed_reviews" : Object},
                    "bar_plot": Object
                },
                {
                    "restaurant_name": 
                    "address": 
                    "style": 
                    "url": 
                    "review_count": ,
                    "description": 
                    "menus": [{"menu_name":~~, "price":~~}, {"menu_name":~~, "price":~~}],
                    "reviews": {"good_reviews": Object, "baed_reviews" : Object},
                    "bar_plot": Object
                }
            ]
        }    
------------------------------------------------------------
    menus = [{"menu_name":~~, "price":~~}]
    reviews = {"good_reviews": Object, "baed_reviews" : Object}
    bar_plot = bar graph
    """

    # 기본 구조 설정
    chef_json = {
        "chef_name": chef_instance.chef_name,
        "image_url": chef_instance.image_url,
        "restaurants": []
    }

    # 레스토랑별 메뉴, 리뷰 워드클라우드 생성
    for restaurant in chef_instance.restaurants.all():     
        menus = []
        reviews = []
        for menu in restaurant.menus.all():
            menus.append(
                {"menu_name": menu.menu_name,
                 "price" : string_to_amount(menu.price)}
            )
        good_reviews_list = []
        bad_reviews_list = []
        good_words = []
        # 좋은 리뷰와 안 좋은 리뷰 확인
        for good_review in restaurant.reviews.filter(review_category='good'):
            good_reviews_list.append(good_review.review_text)
        for bad_review in restaurant.reviews.filter(review_category='bad'):
            bad_reviews_list.append(bad_review.review_text)
        
        reviews.append(make_wordcloud(good_reviews_list, font_path, 300, good_words, stopwords_path, thumb_up_img_path))
        print(good_words)
        reviews.append(make_wordcloud(bad_reviews_list, font_path, 300, good_words, stopwords_path, thumb_down_img_path))
        font_prop = font_manager.FontProperties(fname=font_path)

        fig, ax = plt.subplots(figsize=(5,5))

        total_sum_price = 0
        total_sum_size = Menu.objects.values('price').count()
        for string_price in Menu.objects.values('price'):
            if string_price['price'].strip() == '':
                total_sum_size-=1
                continue
            total_sum_price += string_to_amount(string_price['price'])

        this_sum_price = 0
        this_sum_size = restaurant.menus.all().count()
        for string_price in restaurant.menus.values('price'):
            if string_price['price'].strip() == '':
                this_sum_size-=1
                continue
            this_sum_price += string_to_amount(string_price['price'])         
        
        mean_restaurant_price = total_sum_price // total_sum_size
        this_restaurant_price = this_sum_price  // (this_sum_size if this_sum_size > 0 else 1)
        plot_base64 = avg_price_plot(mean_restaurant_price, this_restaurant_price, font_path)
        #plot_base64 = "바그래프"
        
        # 메뉴 가격
        menu_name_list = [menu.menu_name for menu in restaurant.menus.all()]
        price_list = [string_to_amount(menu.price) for menu in restaurant.menus.all()]
        menu_dict = dict(sorted(zip(menu_name_list,price_list), key=lambda x: x[1],reverse=True)[:5])
        menu_name_list = list(menu_dict.keys())
        price_list = list(menu_dict.values())
        menu_price_bar_plot = menu_price_plot(menu_name_list, price_list, font_path)

        restaurant_data = {
            "restaurant_name": restaurant.restaurant_name,
            "address": restaurant.address,
            "style": restaurant.style,
            "url": restaurant.url,
            "review_count": restaurant.review_count,
            "description": restaurant.description,
            "menus": menus,
            "reviews": reviews,
            "bar_plot": plot_base64,
            "price_plot":menu_price_bar_plot
        }
        chef_json["restaurants"].append(restaurant_data)

    return chef_json

def string_to_amount(s):
    if s.strip() == '':
        return 0
    won = []
    for price_word in s.split(' - '):
        price_word = price_word.replace(",", "")
        price_word = price_word.replace("원", "")
        won.append(int(price_word))
    if len(won) == 0:
        return 0
    else:
        return int(sum(won)/len(won))
