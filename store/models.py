from django.db import models
from django.contrib.auth.models import User
from django.core.files import File
from PIL import Image
from io import BytesIO
from django.utils.text import slugify
from random import randint
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models




class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)

    def __str__(self): 
        return self.title
    class Meta:
        verbose_name_plural='Category/Industry'
        ordering = ('title',)



class Subcategory(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)

    def __str__(self):
        return self.title.title()

    class Meta:
        verbose_name_plural = 'Subcategories'
        ordering = ('category',)



class Product(models.Model):
    ACTIVE = 'active'
    DELETED = 'deleted'

    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (DELETED, 'Deleted'),
    )
    
    user = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, related_name='products', on_delete=models.CASCADE , null=True, blank=True)
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    userprofile = models.ForeignKey('userprofile.Userprofile', related_name='products', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=20 , blank=True, null=True)
    model = models.CharField(max_length=20 , blank=True, null=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='uploads/product_images', null=True)
    image_2 = models.ImageField(upload_to='uploads/product_images', blank=True, null=True)
    image_3 = models.ImageField(upload_to='uploads/product_images', blank=True, null=True)
    image_4 = models.ImageField(upload_to='uploads/product_images', blank=True, null=True)
    video = models.FileField(upload_to='uploads/video', blank=True, null=True)
    condition = models.CharField(max_length=50, null=True, blank=True ,choices=(
        ('New','New'),
        ('Used', 'Used')
    ))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=ACTIVE)
    likes = models.ManyToManyField(User, related_name='liked_products', blank=True)
    comments_enabled = models.BooleanField(default=True)


    class Meta:
        ordering = ('-created_at',)

    def __str__(self): 
        return self.title

    

    def formatted_price(self):
        return intcomma(self.price)

    # a method used to create a unique slug
    def save(self, *args, **kwargs):
        if Product.objects.filter(title=self.title).exists():
            extra = str(randint(1, 1000000))
            self.slug = slugify(self.title) + "-" + extra
        else:
            self.slug = slugify(self.title)
        super(Product, self).save(*args, **kwargs)


class Comment(models.Model):
    product = models.ForeignKey(Product, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product.title}"
    class Meta:
        ordering = ['-created_at']







'''class Order(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.IntegerField()
    paid_amount = models.IntegerField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    payment_intent = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.first_name
    
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField(default=1)'''

    



    