from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
import jpype
import matplotlib.pyplot as plt
from matplotlib import font_manager
from wordcloud import WordCloud

# 문장에서 명사를 추출하는 형태소 분석 라이브러리
from konlpy.tag import Hannanum
import io, os
import base64

from .utils import make_wordcloud



def index(request):
    chefs = Chef.objects.all().values()
    return render(request, 'restaurant/index.html', {'chefs':chefs})

def detail(request, chef_id):
    font_path = os.path.join(settings.BASE_DIR, 'restaurant', 'static', 'fonts', 'D2Coding-Ver1.3.2-20180524.ttc')
    chef = get_object_or_404(Chef, pk=chef_id)
    chef_json = {
        'chef_name' : chef.chef_name,
        'image_url' : chef.image_url
    }

    good_reviews_text = ""
    bad_reviews_text = ""
    # 좋은 리뷰와 안 좋은 리뷰 확인
    for restaurant in chef.restaurants.all():
        for good_review in restaurant.reviews.filter(review_category='good'):
            good_reviews_text += good_review.review_text+' '
        for bad_review in restaurant.reviews.filter(review_category='bad'):
            bad_reviews_text += bad_review.review_text+' '
    
    # 가격 평균 보여주기
    mean_restaurant_price = 100000
    this_restaurant_price = 50000

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
    chef_json['bar_plot'] = plot_base64  # Base64 문자열 저장
    
    chef_json['word_cloud_good'] = make_wordcloud(good_reviews_text, font_path)
    chef_json['word_cloud_bad'] = make_wordcloud(bad_reviews_text, font_path)

    return render(request, 'restaurant/detail.html', {'chef_info': chef_json})


