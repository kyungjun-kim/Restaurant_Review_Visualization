
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

from typing import List

from restaurant.models import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
font_path = os.path.join('restaurant/static/fonts/D2Coding-Ver1.3.2-20180524.ttc')


def make_wordcloud(reviews_list:List[str], font_path:str, num_each_fold:int):
    if not reviews_list.strip():  
        return None
    else:
        # 형태소 분석을 통해 명사 추출
        hannanum = Hannanum()
        noun_list = []
        total_num = len(reviews_list)
        for i in range(total_num//num_each_fold + 1):
            reviews_text = ""
            for s in reviews_list[i*num_each_fold:(i+1)*num_each_fold]:
                reviews_text += s[0] + ' '
            nouns = hannanum.nouns(reviews_text)
            noun_list.extend(nouns)
        
        words = [noun for noun in noun_list if len(noun) > 1]
        
        # 리뷰 없는 경우 예외처리
        if len(''.join(words).strip()) == 0:
            words = ["리뷰X"]

        # WordCloud 생성
        wordcloud = WordCloud(
            font_path= font_path,
            background_color='white',
            width=500,
            height=500
        ).generate(','.join(words))  # 텍스트(두 글자 이상의 명사)로부터 단어 클라우드 생성

        # 이미지로 저장
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')  # 축을 숨김
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)
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


def menu_price_plot(menu, price, font_path):
    font_prop = font_manager.FontProperties(fname=font_path)

    df = pd.DataFrame({"menu":menu, "price":price})
    df_sorted = df.sort_values("price")

    fig, ax = plt.subplots(figsize=(12,4))
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
  