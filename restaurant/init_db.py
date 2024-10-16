import os
import django
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Django 설정 파일 로드
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_restaurant.settings")  # 'web_restaurant'-> 프로젝트 이름에 맞게 수정.
# Django 초기화
django.setup()
from restaurant.models import *

try:
    # JSON 파일 읽기
    with open('restaurant/static/json/db_init.json', 'r', encoding='utf-8') as json_file:
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
        
        for i, r in enumerate(restaurants_data):
            print("#", str(i), r)
        i=1
        for restaurant_data in restaurants_data:
            chef = Chef.objects.get(chef_name=restaurant_data['chef_name'])
            print(chef)
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
            print(str(i), chef.chef_name, restaurant_data['restaurant_name'])
            i+=1
except Exception as e:
    print(e)
