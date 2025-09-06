from django import forms
from django.core.exceptions import ValidationError
from products.models import Product, Category, ProductImage
from orders.models import Order, OrderItem

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'available', 'slug']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'slug': forms.TextInput(attrs={'placeholder': 'Leave blank to auto-generate'}),
        }
    
    # Simple file field for product images
    images = forms.FileField(
        required=False,
        help_text="You can select multiple images by holding Ctrl while selecting files"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        
    def save(self, commit=True):
        product = super().save(commit=commit)
        
        # Handle image upload
        image = self.cleaned_data.get('images')
        if image:
            ProductImage.objects.create(product=product, image=image)
                
        return product

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class OrderNoteForm(forms.Form):
    note = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))