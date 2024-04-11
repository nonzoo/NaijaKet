from random import shuffle
from django.shortcuts import render
from store.models import Product
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


from django.utils import translation

def frontpage(request):
    
    products = Product.objects.filter(user__userprofile__is_vendor=True, status=Product.ACTIVE)


    # Shuffle the carousel images
    shuffled_products = list(products)
    shuffle(shuffled_products)
    shuffled_products = shuffled_products[:5]
    # Create a Paginator object with the desired number of products per page
    paginator = Paginator(products, 20)  # Display 20 products per page

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the corresponding page object from the paginator
        products = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, display the first page
        products = paginator.page(1)
    except EmptyPage:
        # If the page parameter is out of range, display the last page
        products = paginator.page(paginator.num_pages)

    return render(request, 'core/frontpage.html', {
        'shuffled_products': shuffled_products,
        'products': products,
        
    })

