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

from typing import List, Union
from collections import Counter
from restaurant.models import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
font_path = os.path.join('restaurant/static/fonts/D2Coding-Ver1.3.2-20180524.ttc')


def make_wordcloud(reviews_list: List[str], font_path: str, num_each_fold: int, stopwords_path:Union[str, None]=None) -> Union[str, None]:
    if not reviews_list:
        return None
    
    if stopwords_path:
        stopwords = open(stopwords_path, 'r')
        stopwords_list = [line.split('\n')[0] for line in stopwords.readlines()]
        stopwords.close()

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
        height=500
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
  