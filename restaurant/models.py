from django.contrib import admin
from django.db import models

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
        ('bad', 'Bad Review')
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')  # 레스토랑과 연결
    review_text = models.TextField(verbose_name='리뷰', null=False)
    review_category = models.CharField(max_length=4, choices=REVIEW_CHOICES, default='good', verbose_name='리뷰 종류')

    def __str__(self):
        return f'{self.restaurant.restaurant_name} - {self.get_review_category_display()}'

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')  # 레스토랑과 연결
    menu_name = models.CharField(max_length=100, verbose_name='메뉴명', null=False)
    price = models.CharField(max_length=50, verbose_name='가격', null=False)

    def __str__(self):
        return f'{self.restaurant.restaurant_name} - {self.menu_name} - {self.price} 원'
