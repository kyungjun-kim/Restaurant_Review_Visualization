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
    

    def __str__(self):
        return f'쉐프 : {self.chef.chef_name} / 레스토랑 : {self.restaurant_name}'

class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')  # 레스토랑과 연결
    review_text = models.TextField(verbose_name='리뷰', null=False)

    def __str__(self):
        return f'Review for {self.restaurant}'

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')  # 레스토랑과 연결
    menu_name = models.CharField(max_length=100, verbose_name='메뉴명', null=False)
    price = models.BigIntegerField(verbose_name='가격', null=False)

    def __str__(self):
        return f'{self.restaurant.restaurant_name} - {self.menu_name} - {self.price} 원'
