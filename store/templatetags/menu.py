from django import template
from django.contrib.auth.models import User
from store.models import Category
register = template.Library()

@register.inclusion_tag('core/menu.html')
def menu(request):
    catgories = Category.objects.all()
    user = request.user
    context = {'categories': catgories,'user':user}
    return context