from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .cart import Cart
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Subcategory
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse




#SEARCH VIEW
def search(request):
    query = request.GET.get('query')

    if not query or query.strip() == '':
        products = []

    elif len(query.strip()) == 1:
        products = []

    else:
        keywords = query.split()

        products = Product.objects.filter(user__userprofile__is_vendor=True, status=Product.ACTIVE)

        for keyword in keywords:
            products = products.filter(
                Q(title__icontains=keyword) |
                Q(brand__icontains=keyword)|
                Q(model__icontains=keyword)|
                Q(user__userprofile__state__state__icontains=keyword) |
                Q(user__userprofile__lga__icontains=keyword)|
                Q(user__username__icontains = keyword)
            )

    #PAGINATION FOR SEARCH
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if 'suggestions' in request.path:
        suggestions = [product.title for product in products]
        return JsonResponse({'suggestions': suggestions})

    return render(request, 'store/search.html', {
        'query': query,
        'page_obj': page_obj,
    })

#CATEGORY DETAIL VIEW 
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    subcategories = category.subcategories.all()
    products = category.products.filter(user__userprofile__is_vendor=True, status=Product.ACTIVE)

    # Paginate the products
    paginator = Paginator(products, 8)  # Show 8 products per page
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver the last page of results
        products = paginator.page(paginator.num_pages)

    return render(request, 'store/category_detail.html', {
        'category': category,
        'subcategories': subcategories,
        'products': products
    })

#SUBCATEGORY DETAIL VIEW
def subcategory_detail(request, category_slug, subcategory_slug):
    category = get_object_or_404(Category, slug=category_slug)
    subcategory = get_object_or_404(Subcategory, slug=subcategory_slug, category=category)
    products = subcategory.products.filter(user__userprofile__is_vendor=True, status=Product.ACTIVE)

    paginator = Paginator(products, 8)  # Show 8 products per page
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver the last page of results
        products = paginator.page(paginator.num_pages)


    return render(request, 'store/subcategory_detail.html', {
        'category': category,
        'subcategory': subcategory,
        'products': products
        


    })

#PRODUCT DETAIL VIEW
def product_detail(request, category_slug, subcategory_slug, slug):
    category = get_object_or_404(Category, slug=category_slug)
    subcategory = get_object_or_404(Subcategory, slug=subcategory_slug, category=category)
    product = get_object_or_404(Product, slug=slug, user__userprofile__is_vendor=True, status=Product.ACTIVE)

    owner_profile = product.user.userprofile  # Retrieve the UserProfile instance

    return render(request, 'store/product_detail.html', {
        'category': category,
        'subcategory': subcategory,
        'product': product,
        'owner_profile': owner_profile, # Pass the UserProfile instance to the template
        'domain': request.get_host,
        'protocol': request.scheme,  
        
    })
 
    




'''def add_to_cart(request,product_id):
    cart = Cart(request)
    cart.add(product_id)

    return redirect('cart_view')


#to increase and decrease quantity from the cart
def change_quantity(request, product_id):
    action = request.GET.get('action', '')
    if action:
        quantity = 1

        if action == 'decrease':
            quantity = -1

        cart = Cart(request)
        cart.add(product_id, quantity, True)

    return redirect('cart_view')



#to remover product from the cart
def remove_from_cart(request, product_id):
    cart= Cart(request)
    cart.remove (product_id)

    return redirect('cart_view')


def cart_view(request):
    cart = Cart(request)

    return render(request, 'store/cart_view.html',{
        'cart':cart
    })



def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            total_price = 0
            for item in cart:
                product = item['product']
                total_price += product.price * int(item['quantity'])


            order = form.save(commit=False)
            order.created_by = request.user
            order.paid_amount = total_price
            order.save()

            for item in cart:
                product = item['product']
                quantity = int(item['quantity'])
                price = product.price * quantity
                item = OrderItem.objects.create(order=order,product=product,price=price,quantity=quantity)

            cart.clear()
            
            return redirect('myaccount')
    else:
        form = OrderForm()

    return render(request, 'store/checkout.html',{
        'cart':cart,
        'form':form
    })'''

'''def initiate_payment(request):
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET,
    })

    # Create a payment object
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": "http://example.com/payment/execute/",
            "cancel_url": "http://example.com/payment/cancel/",
        },
        "transactions": [{
            "amount": {
                "total": "10.00",
                "currency": "USD",
            },
            "description": "Payment description",
        }],
    })

    # Create the payment on PayPal
    if payment.create():
        # Redirect to PayPal's approval URL
        for link in payment.links:
            if link.method == "REDIRECT":
                return redirect(link.href)
    else:
        # Handle payment creation failure
        # e.g., log an error or show an error page
        pass


def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Payment executed successfully
        # Perform further actions (e.g., update order status, send confirmation email)
        return redirect('payment_success')
    else:
        # Handle payment execution failure
        # e.g., log an error or show an error page
        pass'''
