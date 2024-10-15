from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt

import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 횟수를 기반으로 딕셔너리 생성
from collections import Counter

# 문장에서 명사를 추출하는 형태소 분석 라이브러리
from konlpy.tag import Hannanum
import io, os
import base64

def index(request):
    chefs = Chef.objects.all().values()
    return render(request, 'restaurant/index.html', {'chefs':chefs})

def detail(request, chef_id):
    
    chef = get_object_or_404(Chef, pk=chef_id)
    chef_json = {
        'chef_name' : chef.chef_name,
        'image_url' : chef.image_url
    }
    reviews_text = ""
    # 일단은... 모든 매장 기준 모든 리뷰로 조회
    for restaurant in chef.restaurants.all():
        for review in restaurant.reviews.all():
            reviews_text += review.review_text+' '
    
    if not reviews_text.strip():  
        chef_json['word_cloud'] = None  
    else:
        # 형태소 분석을 통해 명사 추출
        hannanum = Hannanum()
        nouns = hannanum.nouns(reviews_text)
        words = [noun for noun in nouns if len(noun) > 1]
        counter = Counter(words)

        
        # WordCloud 생성
        font_path = os.path.join(settings.BASE_DIR, 'restaurant', 'static', 'fonts', 'D2Coding-Ver1.3.2-20180524.ttc')
        wordcloud = WordCloud(
            font_path= font_path,
            background_color='white',
            width=1000,
            height=1000
        ).generate(reviews_text)  # 텍스트로부터 단어 클라우드 생성
        
        # 이미지로 저장
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')  # 축을 숨김
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        chef_json['word_cloud'] = image_base64

    return render(request, 'restaurant/detail.html', {'chef_info': chef_json})


def init(request):
    try:
        # JSON 파일 읽기
        with open(settings.BASE_DIR / 'restaurant' / 'static' / 'json' / 'db_init.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            
            # Chef 초기화
            Chef.objects.all().delete()
            chefs_data = data.get('chefs')
            for chef_data in chefs_data:
                chef, created = Chef.objects.get_or_create(
                    chef_name=chef_data['chef_name'],
                    image_url=chef_data['image_url']
                )
            chefs = Chef.objects.all().values()

            # Restaurant 초기화
            Restaurant.objects.all().delete()
            restaurants_data = data.get('restaurants')
            for restaurant_data in restaurants_data:
                chef = Chef.objects.get(chef_name=restaurant_data['chef_name'])
                Restaurant.objects.get_or_create(
                    chef=chef,
                    restaurant_name=restaurant_data['restaurant_name'],
                    restaurant_name_en=restaurant_data['restaurant_name_en'],
                    address=restaurant_data['address'],
                    style=restaurant_data['style'],
                    url=restaurant_data['url'],
                    review_count=restaurant_data['review_count'],
                    description=restaurant_data['description']
                )
        return redirect('index')
    except Exception as e:
        return redirect('index')