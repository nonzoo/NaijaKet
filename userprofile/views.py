from django.shortcuts import render, redirect
from django.contrib.auth.models import User 
from django.contrib.auth import login,authenticate,logout
from .models import Userprofile
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.contrib import messages
from .form import SignUpForm, EditAccountForm
from store.forms import ProductForm
from store.models import Product,Subcategory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .validator import validate_unique_email
from django.http import JsonResponse
from .models import Userprofile
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django import template
from django.contrib.auth import REDIRECT_FIELD_NAME
#from django.utils import translation

def vendor_detail(request, pk):
    user = User.objects.get(pk=pk)
    products = user.products.filter(user__userprofile__is_vendor=True, status = Product.ACTIVE)
    paginator = Paginator(products, 8)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)

    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'userprofile/vendor_detail.html', {
        'user':user,
        'products':products

    })




@login_required(login_url='login')
def my_store(request):
    
    if request.user.userprofile.is_vendor:
        products = request.user.products.exclude(status=Product.DELETED)
        
        paginator = Paginator(products, 8)
        page = request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)

        except EmptyPage:
            products = paginator.page(paginator.num_pages)


        return render(request, 'userprofile/my_store.html', {
            'products': products
        })
    else:
        return render(request, 'userprofile/create_subscription.html')

'''def my_store_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    return render(request, 'userprofile/my_store_order_detail.html',{
        'order':order
    })
'''


def create_subscription(request):
    user_profile = Userprofile.objects.get(user=request.user)
    if user_profile.is_vendor == False:
        if request.method == "POST":
            plan = int(request.POST.get("plan"))
            context = {
                "plan":plan
            }
            
            return render(request,"userprofile/subscription_confirm.html", context)
    else:
        return render(request, 'userprofile/my_store.html')

#to update the is_vendor field in userprofile model when the customer subscribe successfully
@login_required(login_url='login')
def update_vendor_status(request):
    user_profile = Userprofile.objects.get(user=request.user)
    user_profile.is_vendor = True
    user_profile.save()
    return JsonResponse({'message': 'Vendor status updated successfully'})
    


#for vendors to add product
@login_required(login_url='login')
def add_product(request):

    #saving the product to the database when the submit button is clicked 
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            title = request.POST.get('title')

            product = form.save(commit=False)
            product.user = request.user
            product.slug = slugify(title)
            product.save()
            messages.success(request, 'The product was added successfully!')

            #redirectng the vendor back to the store page after submitting the product form
            return redirect('my_store')
    
    else:
        form = ProductForm()

    return render(request, 'userprofile/product_form.html',{
        'title': 'Add product',
        'form':form
    })

#An edit function for the vendors
@login_required(login_url='login')
def edit_product(request, pk):
    product = Product.objects.filter(user=request.user).get(pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            messages.success(request, 'The changes was saved!')

            return redirect('my_store')
            
    else:
        form = ProductForm(instance=product)


    return render(request, 'userprofile/product_form.html',{

        'title': 'Edit product', 
        'product':product,
        'form':form
    })




def get_subcategories(request):
    category_id = request.GET.get('category_id')

    if category_id is not None and category_id.isdigit():
        # Valid category_id, proceed with filtering subcategories
        subcategories = Subcategory.objects.filter(category_id=int(category_id)).values('id', 'title')
        return JsonResponse({'subcategories': list(subcategories)})
    else:
        # Invalid or missing category_id, return an error response
        return JsonResponse({'error': 'Invalid or missing category_id'}, status=400)



@login_required(login_url='login')
def delete_product(request, pk):
    product = Product.objects.filter(user=request.user).get(pk=pk)
    product.status = Product.DELETED
    product.save()

    messages.success(request, 'The product was deleted!')
    return redirect('my_store')
    


@login_required(login_url='login')
def myaccount(request):
    return render (request, 'userprofile/myaccount.html')


@login_required(login_url='login')
def edit_account(request):
    user_profile = request.user.userprofile 
    
    if request.method == 'POST':
        form = EditAccountForm(request.POST, request.FILES, instance=user_profile)
        
        if form.is_valid():
            form.save()
            return redirect('myaccount')
    else:
        form = EditAccountForm(instance=user_profile)
    
    return render(request, 'userprofile/edit_account.html', {'form': form})


def loginView(request):
    if request.user.is_authenticated:
        return redirect('frontpage')

    if request.method == 'POST': #if the user enter thier information and login
        username = request.POST.get('username') #get the username
        password = request.POST.get('password') # get the password

        #check if the user exits
        try:
            user = User.objects.get(username = username)

        except:
            messages.error(request, 'User does not exit')

        #authenticate the user 
        user = authenticate(request, username=username, password= password)

        if user is not None:
            login(request, user) #log the user in

            return redirect('myaccount')# redirects the user back to the home page
        
        else:
          messages.error(request, "Username OR Password does not exit")

    context = {}
    return render (request, 'userprofile/login.html', context)



def logoutUser(request):

    logout(request)
    return redirect('frontpage')



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            user.username = user.username.lower()
            login(request, user)
            userprofile = Userprofile.objects.create(user=user)
            return redirect('myaccount')
    else:
      form = SignUpForm()

    return render(request, 'userprofile/signup.html',{
        'form':form,
        'domain': request.get_host,
        'protocol': request.scheme, 

    })



def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data)|Q(username=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					plaintext = template.loader.get_template('userprofile/password_reset_email.txt')
					htmltemp = template.loader.get_template('userprofile/password_reset_email.html')
					c = { 
					"email":user.email,
					'domain': request.get_host,
					'site_name': 'NaijaKet',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': request.scheme,
					}
					text_content = plaintext.render(c)
					html_content = htmltemp.render(c)
					try:
						msg = EmailMultiAlternatives(subject, text_content, 'NaijaKet <thenaijaket@outlook.com>', [user.email], headers = {'Reply-To': 'thenaijaket@outlook.com'})
						msg.attach_alternative(html_content, "text/html")
						msg.send()
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("password_reset_done")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="userprofile/password_reset_form.html", context={"password_reset_form":password_reset_form})

def privacy(request):
    return render(request, 'userprofile/privacy.html')

