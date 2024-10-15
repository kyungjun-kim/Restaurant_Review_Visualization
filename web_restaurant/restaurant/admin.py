from django.contrib import admin
from .models import Chef, Restaurant, Review, Menu

admin.site.register(Chef)
admin.site.register(Restaurant)
admin.site.register(Review)
admin.site.register(Menu)