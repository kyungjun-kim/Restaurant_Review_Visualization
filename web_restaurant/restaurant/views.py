from django.shortcuts import render, get_object_or_404
from .models import *
from django.http import HttpResponse
import json

def index(request):
    chefs = Chef.objects.all().values()
    return render(request, 'restaurant/index.html', {'chefs':chefs})

def detail(request, chef_id):
    # 숏컷 방식
    chef = get_object_or_404(Chef, pk=chef_id)
    chef_json = json.dumps({
        'id':chef.id,
        'chef_name':chef.chef_name,
        'image_url':chef.image_url
    })
    return render(request, 'restaurant/detail.html', {'chef': chef_json})