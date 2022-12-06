from django.utils.datastructures import MultiValueDictKeyError
from django.shortcuts import render
from . import sentiment_analisis

def home(request):
    return render(request, 'partials/content.ejs')
def hasil(request):
    user_text=request.GET['user_text']
    result=sentiment_analisis.class_to_name(user_text)
    return render(request,'partials/hasil.ejs',{'hasil':result,'kalimat':'user_text'})


