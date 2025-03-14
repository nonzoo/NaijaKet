from django import forms

from .models import Product



'''class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'address','phone_number', 'email','zipcode','state','city',)'''




class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('category' ,'subcategory', 'title', 'description', 'brand','model','price', 'image','image_2','image_3','image_4','video','condition')
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full p-4 py-2 px-3 border border-gray-400'
            }),
            
            'subcategory': forms.Select(attrs={
                'class': 'w-full p-4 py-2 px-3 border border-gray-400'
            }),
            'title': forms.TextInput(attrs={
                 'class':'w-full p-4 py-2 px-3 border border-gray-400'
            }),
            'description':forms.Textarea(attrs={
                'class':'w-full p-4 py-2 px-3 border border-gray-400'
            }),
            'price': forms.TextInput(attrs={
                'class':'w-full p-4 py-2 px-3 border border-gray-400'
            }),
            'brand': forms.TextInput(attrs={
                'class':'w-full p-4 py-2 px-3 border border-gray-400'
            }),
            'model': forms.TextInput(attrs={
                'class':'w-full p-4 py-2 px-3 border border-gray-400'
            }),
            'image': forms.FileInput(attrs={
                'class':'w-full p-4 py-2 px-3 border border-gray-400'
            }),
            'image_2': forms.FileInput(attrs={
                'class':'w-full p-4 py-2 px-3 border border-gray-400'
            }),
            'image_3': forms.FileInput(attrs={
                'class':'w-full p-4 py-2 px-3 border border-gray-400'
            }),
            'image_4': forms.FileInput(attrs={
                'class':'w-full p-4 py-2 px-3 border border-gray-400'
            }),
            'video': forms.FileInput(attrs={
                'class':'w-full p-4 py-2 px-3 border border-gray-400'
            }),
             'condition': forms.Select(attrs={
                'class': 'w-full p-4 py-2 px-3 border border-gray-400'
            }),
        }